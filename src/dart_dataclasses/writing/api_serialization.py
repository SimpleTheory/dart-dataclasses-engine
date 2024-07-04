import copy
import functools
import dart_dataclasses.writing.class_functions as cf
import dart_dataclasses.writing.json_serialization as js
import dart_dataclasses.domain as domain
from dart_dataclasses.parsing.config_file import default_map_method_for_non_dataclass_api_instantiation
from enum import Enum

class ClassType(Enum):
    supported_types = 1
    dataclass = 2
    enum = 3

# <editor-fold desc="Utility">
def type_is_dataclass(taipu: domain.Type, dataclasses_and_enums: list[domain.Class | domain.DartEnum]) -> ClassType | None:
    if taipu.type in domain.types_with_extensions:
        return ClassType.supported_types
    elif taipu.type in [cls.name for cls in dataclasses_and_enums if isinstance(cls, domain.Class)]:
        return ClassType.dataclass
    elif taipu.type in [cls.name for cls in dataclasses_and_enums if isinstance(cls, domain.DartEnum)]:
        return ClassType.enum
    else:
        return None
    # return taipu.type in [dataclass.name for dataclass in dataclasses_and_enums] + domain.types_with_extensions

def type_is_non_collection_json_safe(taipu: domain.Type):
    return taipu.type in ['int', 'String', 'double', 'num', 'bool']

def format_type_cast_for_api(func):
    @functools.wraps(func)
    def wrapper(taipu, var_name, dataclasses, recursion_level=0):
        result = func(taipu, var_name, dataclasses, recursion_level)
        if not recursion_level:
            return f'{result};'
        else:
            space = '    ' * recursion_level
            return f'\n{space}{result}'

    return wrapper

# </editor-fold>

# <editor-fold desc="API Type Cast">
# noinspection DuplicatedCode
def final_case(varname: str, taipu: domain.Type, dataclasses_and_enums: list[domain.Class | domain.DartEnum]):
    nullability_code = ''
    dataclass_type = type_is_dataclass(taipu, dataclasses_and_enums)
    map_factory = 'fromApiMap' if dataclass_type == ClassType.dataclass else 'fromMap'
    if dataclass_type:
        if taipu.nullable:
            nullability_code = f'{varname} == null ? null : '
            # type2defaults[Duration]!.fromMap!
        return f'{nullability_code}type2reflection[{taipu.type}]!.{map_factory}!({varname})'
    if type_is_non_collection_json_safe(taipu):
        return f'{varname} as {taipu.to_str()}'
    # Unknown case
    return f'{nullability_code}{taipu.type}.{default_map_method_for_non_dataclass_api_instantiation}({varname})'
    # raise ValueError(f'Type {taipu.to_str()} in base case for {varname} is not JSON Serializable')



# noinspection DuplicatedCode
@format_type_cast_for_api
def type_cast_iterable_for_api(taipu: domain.Type, var_name: str,
                               dataclasses_and_enums: list[domain.Class | domain.DartEnum], recursion_level=0,
                               base_padding=4, pad_amount=4) -> str:
    # DATACLASSES MEANS LIST DATACLASSES + ENUMS
    nullability_code = ''
    new_line_code = f'\n{(base_padding * " ") + (" " * pad_amount * recursion_level)}'
    if taipu.nullable:
        taipu = copy.copy(taipu)
        taipu.nullable = False
        nullability_code = f'{var_name} == null ? null : {new_line_code}'

    # generic listlike
    if len(taipu.generics) == 1 and taipu.generics[0].generics:
        return f'{nullability_code}{cf.iterable_factory(taipu)}{var_name}.map((__e{recursion_level}) ' \
               f'=> {type_cast_iterable_for_api(taipu.generics[0], f"__e{recursion_level}", dataclasses_and_enums, recursion_level + 1)}).toList())'
    # generic maplikes
    if len(taipu.generics) > 1:

        # Mappy key and value
        if all([taipu.generics[1].generics, taipu.generics[0].generics]):
            return f'{nullability_code}{cf.iterable_factory(taipu)}{var_name}.map((__k{recursion_level}, __v{recursion_level}) ' \
                   f'=> MapEntry(' \
                   f'{type_cast_iterable_for_api(taipu.generics[0], f"__k{recursion_level}", dataclasses_and_enums, recursion_level + 1)}, ' \
                   f'{type_cast_iterable_for_api(taipu.generics[1], f"__v{recursion_level}", dataclasses_and_enums, recursion_level + 1)})))'

        # Mappy Value
        if len(taipu.generics) > 1 and taipu.generics[1].generics:
            # __k{recursion_level} as {taipu.generics[0].to_str()
            return f'{nullability_code}{cf.iterable_factory(taipu)}{var_name}.map((__k{recursion_level}, __v{recursion_level}) ' \
                   f'=> MapEntry({final_case(f'__k{recursion_level}', taipu.generics[0], dataclasses_and_enums)}, ' \
                   f'{type_cast_iterable_for_api(taipu.generics[1], f"__v{recursion_level}", dataclasses_and_enums, recursion_level + 1)})))'

        # Mappy Key
        if len(taipu.generics) > 1 and taipu.generics[0].generics:
            # __v{recursion_level} as {taipu.generics[1].to_str()}
            return f'{nullability_code}{cf.iterable_factory(taipu)}{var_name}.map((__k{recursion_level}, __v{recursion_level}) ' \
                   f'=> MapEntry({type_cast_iterable_for_api(taipu.generics[0], f"__k{recursion_level}", dataclasses_and_enums, recursion_level + 1)}, ' \
                   f'{final_case(f'__v{recursion_level}', taipu.generics[1], dataclasses_and_enums)})))'
    # __k{recursion_level} as {taipu.generics[0].to_str()}
    # regular listlike
    if len(taipu.generics) == 1:
        if type_is_dataclass(taipu.generics[0], dataclasses_and_enums):
            non_nullable_taipu = copy.copy(taipu.generics[0])
            non_nullable_taipu.nullable = False
            base_var = f'__v{recursion_level}'
            # base_nullability = f'{base_var} == null ? null : ' if taipu.generics[0].nullable else ''
            # randomList.map<Example>((element) => Example.fromMap(element))
            # List<Example>.from(randomList.map<Example>((element) => Example.fromMap(element)))
            return (f'{nullability_code}{cf.iterable_factory(taipu)}{var_name}.map(({base_var})'
                    f' => {final_case(base_var, taipu.generics[0], dataclasses_and_enums)}))')
        return f'{nullability_code}{cf.iterable_factory(taipu)}{var_name})'
    # regular maplike
    if len(taipu.generics) > 1:
        # __k{recursion_level} as {taipu.generics[0].to_str()}
        # __v{recursion_level} as {taipu.generics[1].to_str()}
        return f'{nullability_code}{cf.iterable_factory(taipu)}{var_name}.map((__k{recursion_level}, __v{recursion_level}) ' \
               f'=> MapEntry({final_case(f'__k{recursion_level}', taipu.generics[0], dataclasses_and_enums)},' \
               f' {final_case(f'__v{recursion_level}', taipu.generics[1], dataclasses_and_enums)})))'
    raise Exception('Type casting exception!')


# </editor-fold>

# <editor-fold desc="From API main">
def part_declaration_procedure(attr: domain.Attribute, dataclasses_and_enums: list[domain.Class | domain.DartEnum]) -> str:
    prefix = f'{attr.type.to_str()} {attr.name} ='
    if cf.type_is_iterable(attr.type):
        return f'{prefix} {type_cast_iterable_for_api(attr.type, f'map[\'{attr.name}\']', dataclasses_and_enums)}'
    if type_is_non_collection_json_safe(attr.type) or attr.type.type == 'dynamic':
        return f'{prefix} map[\'{attr.name}\'];'
    if type_is_dataclass(attr.type, dataclasses_and_enums):
        return f'{prefix} {final_case(f'map[\'{attr.name}\']', attr.type, dataclasses_and_enums)};'
    return f'{prefix} {final_case(f'map[\'{attr.name}\']', attr.type, dataclasses_and_enums)};'
    # Must keep lines like this to keep integrity of extension types, like enumJsons or BigIntJson, etc...
    # if attr.type.nullable:
    #     return f'{attr.type.to_str()} {attr.name} = ' \
    #            f'map[\'{attr.name}\'] == null ? null : dejsonify(map[\'{attr.name}\']);'
    # return f'{attr.type.to_str()} {attr.name} = str2reflection[map[\'{attr.name}\']["__type"]]!.fromMap!(map[\'{attr.name}\']);'
    # return f'{attr.type.to_str()} {attr.name} = dejsonify(map[\'{attr.name}\']);'


def part_declaration(dynamic_attributes: list[domain.Attribute], dataclasses_and_enums: list[domain.Class | domain.DartEnum], padding=4) -> str:
    space = padding * ' '
    return ('\n' + space).join([part_declaration_procedure(attr, dataclasses_and_enums) for attr in dynamic_attributes])


def from_api(dart_class: domain.Class, dataclasses_and_enums: list[domain.Class | domain.DartEnum]) -> str:
    attrs = cf.get_dynamic_attributes(dart_class, construction=True)
    return '''
factory ClassName.fromApi(String json) => ClassName.fromApiMap(jsonDecode(json));

factory ClassName.fromApiMap(Map map){    
    part_declaration

    return return_constructor;
  }
    '''.replace('part_declaration', part_declaration(attrs, dataclasses_and_enums)) \
        .replace('return_constructor', js.return_constructor(dart_class)) \
        .replace('ClassName', dart_class.name) \
        .strip()

def to_api(dart_class: domain.Class):
    return ("Map<String, dynamic> toApiMap() => removeTypeKey({'__type': 'ClassName', ...nestedJsonMap(attributes__)});"
            "\n\nString toApi() => jsonEncode(toApiMap());").replace('ClassName', dart_class.name).strip()

# </editor-fold>

# <editor-fold desc="Deep Copy With">
def copy_with_final_case(varname: str, taipu: domain.Type, dataclasses):
    nullability_code = ''
    if type_is_dataclass(taipu, dataclasses) == ClassType.dataclass:
        the_dataclass: domain.Class = {cls.name: cls for cls in dataclasses}[taipu.type]
        method = find_proper_dataclass_copy_method(the_dataclass)
        if taipu.nullable:
            nullability_code = f'{varname} == null ? null : '
            # type2defaults[Duration]!.fromMap!
        return f'{nullability_code}{varname}.{method}()'
    else:
        return varname

def find_proper_dataclass_copy_method(the_dataclass: domain.Class):
    method_names = [method.name for method in the_dataclass.methods]
    if (method := f'copyWith{the_dataclass.name}') in method_names:
        return method
    elif (method := f'copyWith') in method_names:
        return method
    elif (method := f'copy') in method_names:
        return method
    elif (method := f'copy{the_dataclass.name}') in method_names:
        return method
    elif (method := f'clone{the_dataclass.name}') in method_names:
        return method
    elif (method := f'clone') in method_names:
        return method



# noinspection DuplicatedCode
@format_type_cast_for_api
def copy_with_type_cast(taipu: domain.Type, var_name: str, dataclasses_and_enums: list[domain.Class], recursion_level=0,
                        base_padding=4, pad_amount=4) -> str:
    nullability_code = ''
    new_line_code = f'\n{(base_padding * " ") + (" " * pad_amount * recursion_level)}'

    if taipu.nullable:
        taipu = copy.copy(taipu)
        taipu.nullable = False
        nullability_code = f'{var_name} == null ? null : {new_line_code}'

    # base cases
    if len(taipu.generics) == 0:
        if type_is_dataclass(taipu, dataclasses_and_enums):
            return copy_with_final_case(var_name, taipu, dataclasses_and_enums)
        return var_name

    # generic listlike
    if len(taipu.generics) == 1 and taipu.generics[0].generics:
        return f'{nullability_code}{cf.iterable_factory(taipu)}{var_name}.map((__e{recursion_level}) ' \
               f'=> {copy_with_type_cast(taipu.generics[0], f"__e{recursion_level}", dataclasses_and_enums, recursion_level + 1)}).toList())'
    # generic maplikes
    if len(taipu.generics) > 1:

        # Mappy key and value
        if all([taipu.generics[1].generics, taipu.generics[0].generics]):
            return f'{nullability_code}{cf.iterable_factory(taipu)}{var_name}.map((__k{recursion_level}, __v{recursion_level}) ' \
                   f'=> MapEntry(' \
                   f'{copy_with_type_cast(taipu.generics[0], f"__k{recursion_level}", dataclasses_and_enums, recursion_level + 1)}, ' \
                   f'{copy_with_type_cast(taipu.generics[1], f"__v{recursion_level}", dataclasses_and_enums, recursion_level + 1)})))'

        # Mappy Value
        if len(taipu.generics) > 1 and taipu.generics[1].generics:
            # __k{recursion_level} as {taipu.generics[0].to_str()
            return f'{nullability_code}{cf.iterable_factory(taipu)}{var_name}.map((__k{recursion_level}, __v{recursion_level}) ' \
                   f'=> MapEntry({copy_with_final_case(f'__k{recursion_level}', taipu.generics[0], dataclasses_and_enums)}, ' \
                   f'{copy_with_type_cast(taipu.generics[1], f"__v{recursion_level}", dataclasses_and_enums, recursion_level + 1)})))'

        # Mappy Key
        if len(taipu.generics) > 1 and taipu.generics[0].generics:
            # __v{recursion_level} as {taipu.generics[1].to_str()}
            return f'{nullability_code}{cf.iterable_factory(taipu)}{var_name}.map((__k{recursion_level}, __v{recursion_level}) ' \
                   f'=> MapEntry({copy_with_type_cast(taipu.generics[0], f"__k{recursion_level}", dataclasses_and_enums, recursion_level + 1)}, ' \
                   f'{copy_with_final_case(f'__v{recursion_level}', taipu.generics[1], dataclasses_and_enums)})))'
    # __k{recursion_level} as {taipu.generics[0].to_str()}
    # regular listlike
    if len(taipu.generics) == 1:
        if type_is_dataclass(taipu.generics[0], dataclasses_and_enums):
            non_nullable_taipu = copy.copy(taipu.generics[0])
            non_nullable_taipu.nullable = False
            base_var = f'__v{recursion_level}'
            # base_nullability = f'{base_var} == null ? null : ' if taipu.generics[0].nullable else ''
            # randomList.map<Example>((element) => Example.fromMap(element))
            # List<Example>.from(randomList.map<Example>((element) => Example.fromMap(element)))
            return (f'{nullability_code}{cf.iterable_factory(taipu)}{var_name}.map(({base_var})'
                    f' => {copy_with_final_case(base_var, taipu.generics[0], dataclasses_and_enums)}))')
        return f'{nullability_code}{cf.iterable_factory(taipu)}{var_name})'
    # regular maplike
    if len(taipu.generics) > 1:
        # __k{recursion_level} as {taipu.generics[0].to_str()}
        # __v{recursion_level} as {taipu.generics[1].to_str()}
        return f'{nullability_code}{cf.iterable_factory(taipu)}{var_name}.map((__k{recursion_level}, __v{recursion_level}) ' \
               f'=> MapEntry({copy_with_final_case(f'__k{recursion_level}', taipu.generics[0], dataclasses_and_enums)},' \
               f' {copy_with_final_case(f'__v{recursion_level}', taipu.generics[1], dataclasses_and_enums)})))'

    raise Exception('Type casting exception!')

def copy_with(dart_class: domain.Class, dataclasses_and_enums: list[domain.Class | domain.DartEnum]) -> str:
    dynamic_attributes = cf.get_dynamic_attributes(dart_class, construction=True)
    null = lambda x: x if x.endswith('?') else x + '?'
    attrs_params = ", ".join([f'{null(attr.type.to_str())} {attr.name}' for attr in dynamic_attributes])
    attr_body = [
        f'{attr.name} = {attr.name} ?? {copy_with_type_cast(attr.type, f"this.{attr.name}", dataclasses_and_enums)}' for
        attr in dynamic_attributes]

    if attrs_params:
        constructor = js.return_constructor(dart_class)
        result = (f'{dart_class.name} copyWith{dart_class.name}({{{attrs_params}}}){{\n  '
                  f'{"\n  ".join(attr_body)}'
                  f'\n\n  return {constructor};'
                  '\n}')
        return result
    else:
        return f'{dart_class.name} copyWith{dart_class.name}() => {dart_class.name}();'
# </editor-fold>