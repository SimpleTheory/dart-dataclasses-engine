import functools
import dart_dataclasses.domain as domain
import dart_dataclasses.writing.class_functions as cf
import copy

"""
Declare all the parts for the constructor:
    If a part is supposed to be iterable recursively instantiate the objects therein
    If a part is a default json part leave as is
    Else call from Json
ex:
----------
class Person {
    Address address;
    List<Person> family;
    String name;
    
    fromJson(String json){
        Map map = jsonDecode(json);
        
        Address address = map[address].fromMap();
        List familyTemp = recursiveFromJsonIterable(json[family]);
        String name = map[name]
        
        List<Person> family = iterable_type_cast(family.type, f'{family.name}Temp')
        
        return Person(address: address, family: family, name: name);
    }
}

----------
Let it be that recursiveFromJsonIterable(Iterable iter) is a fx that takes in a Map or List and returns that same Map
or List as is with the same level of recursion, but with all valid objects instantiated therein! Such
that the only uninitialized things there are Iterable types and the correct type castings.

However, if it receives a null value arg then let it return null as well.

Let it be that a map called jsonFactoryMap<String, Function> maps the Class names to their respective
 factory method 'Person': Person.fromMap, such that jsonFactoryMap
"""


def to_json(dart_class: domain.Class) -> str:
    return '''
String toJson()=>jsonEncode(toMap());
Map<String, dynamic> toMap()=> {'__type': 'ClassName', ...nestedJsonMap(attributes__)};''' \
        .replace('ClassName', dart_class.name).strip()


def part_declaration_procedure(attr: domain.Attribute, space='    ') -> str:
    if cf.type_is_iterable(attr.type):
        temp_type = 'List'
        if 'map' in attr.type.type.lower():
            temp_type = 'Map'
        question_mark = '?' if attr.type.nullable else ''
        return f'{temp_type}{question_mark} {attr.name}Temp = dejsonify(map[\'{attr.name}\']);'
    if attr.type.type in domain.json_safe_types:
        return f'{attr.type.to_str()} {attr.name} = map[\'{attr.name}\'];'
    # Must keep lines like this to keep integrity of extension types, like enumJsons or BigIntJson, etc...
    # if attr.type.nullable:
    #     return f'{attr.type.to_str()} {attr.name} = ' \
    #            f'map[\'{attr.name}\'] == null ? null : dejsonify(map[\'{attr.name}\']);'
    # return f'{attr.type.to_str()} {attr.name} = str2reflection[map[\'{attr.name}\']["__type"]]!.fromMap!(map[\'{attr.name}\']);'
    return f'{attr.type.to_str()} {attr.name} = dejsonify(map[\'{attr.name}\']);'

def part_declaration(dynamic_attributes: list[domain.Attribute], padding=4) -> str:
    space = padding * ' '
    return ('\n' + space).join([part_declaration_procedure(attr, space) for attr in dynamic_attributes])


def format_type_cast(func):
    @functools.wraps(func)
    def wrapper(taipu, var_name, recursion_level=0, base_padding=4, pad_amount=2):
        result = func(taipu, var_name,
                      recursion_level=recursion_level, base_padding=base_padding, pad_amount=pad_amount)
        base_padding_space = ' ' * base_padding
        if not recursion_level:
            return f'{base_padding_space}{result};'
        else:
            space = ' ' * pad_amount * recursion_level
            return f'\n{base_padding_space}{space}{result}'

    return wrapper


@format_type_cast
def type_cast_iterable(taipu: domain.Type, var_name: str, recursion_level=0, base_padding=4, pad_amount=4) -> str:
    nullability_code = ''
    new_line_code = f'\n{(base_padding * " ") + (" " * pad_amount * recursion_level)}'
    if taipu.nullable:
        taipu = copy.copy(taipu)
        taipu.nullable = False
        nullability_code = f'{var_name} == null ? null : {new_line_code}'

    # generic listlike
    if len(taipu.generics) == 1 and taipu.generics[0].generics:
        return f'{nullability_code}{cf.iterable_factory(taipu)}{var_name}.map((__e{recursion_level}) ' \
            f'=> {type_cast_iterable(taipu.generics[0], f"__e{recursion_level}", recursion_level + 1)}).toList())'
    # generic maplikes
    if len(taipu.generics) > 1:

        # Mappy key and value
        if all([taipu.generics[1].generics, taipu.generics[0].generics]):
            return f'{nullability_code}{cf.iterable_factory(taipu)}{var_name}.map((__k{recursion_level}, __v{recursion_level}) ' \
                f'=> MapEntry(' \
                f'{type_cast_iterable(taipu.generics[0], f"__k{recursion_level}", recursion_level + 1)}, ' \
                f'{type_cast_iterable(taipu.generics[1], f"__v{recursion_level}", recursion_level + 1)})))'

        # Mappy Value
        if len(taipu.generics) > 1 and taipu.generics[1].generics:
            return f'{nullability_code}{cf.iterable_factory(taipu)}{var_name}.map((__k{recursion_level}, __v{recursion_level}) ' \
                f'=> MapEntry(__k{recursion_level} as {taipu.generics[0].to_str()}, ' \
                f'{type_cast_iterable(taipu.generics[1], f"__v{recursion_level}", recursion_level + 1)})))'

        # Mappy Key
        if len(taipu.generics) > 1 and taipu.generics[0].generics:
            return f'{nullability_code}{cf.iterable_factory(taipu)}{var_name}.map((__k{recursion_level}, __v{recursion_level}) ' \
                f'=> MapEntry({type_cast_iterable(taipu.generics[0], f"__k{recursion_level}", recursion_level + 1)}, ' \
                f'__v{recursion_level} as {taipu.generics[1].to_str()})))'
    # __k{recursion_level} as {taipu.generics[0].to_str()}
    # regular listlike
    if len(taipu.generics) == 1:
        return f'{nullability_code}{cf.iterable_factory(taipu)}{var_name})'
    # regular maplike
    if len(taipu.generics) > 1:
        return f'{nullability_code}{cf.iterable_factory(taipu)}{var_name}.map((__k{recursion_level}, __v{recursion_level}) ' \
        f'=> MapEntry(__k{recursion_level} as {taipu.generics[0].to_str()},' \
        f' __v{recursion_level} as {taipu.generics[1].to_str()})))'
    raise Exception('Type casting exception!')


def type_cast(list_of_attributes_to_cast: list[domain.Attribute], base_padding=4, pad_amount=2):
    if not list_of_attributes_to_cast:
        return '// No casting'
    casts = []
    for attribute in list_of_attributes_to_cast:
        # if attribute.type.nullable:
        #     casts.append(
        #         f'if ({attribute.name}Temp == null)***{attribute.type.to_str()} '
        #         f'{attribute.name} = null;%%%\n{space}'
        #         f'else***{attribute.type.to_str()} {attribute.name} =\n'
        #         f'{type_cast_iterable(attribute.type, f"{attribute.name}Temp", base_padding=base_padding+4)}'
        #         f'\n{space}%%%'
        #         .replace('***', '{')
        #         .replace('%%%', '}')
        #     )
        # else:
        #     casts.append(
        #         f'{"Map" if cf.type_is_map(attribute.type) else "List"} '
        #         f'{attribute.name}Temp_2 = {attribute.name}Temp!;\n{space}'
        #         f'{attribute.type.to_str()} {attribute.name} =\n'
        #         f'{type_cast_iterable(attribute.type, f"{attribute.name}Temp_2", base_padding=base_padding+4)}'
        #     )
        casts.append(
            f'{attribute.type.to_str()} {attribute.name} =\n'
            f'{type_cast_iterable(attribute.type, f"{attribute.name}Temp", base_padding=base_padding + pad_amount, pad_amount=pad_amount)}'
        )

    return f'\n\n{base_padding * " "}'.join(casts)


def return_constructor(dart_class: domain.Class) -> str:
    return f'{dart_class.name}' \
           f'({", ".join([f"{attr.name}: {attr.name}" for attr in cf.get_dynamic_attributes(dart_class, construction=True)])})'


def from_json(dart_class: domain.Class) -> str:
    attrs = cf.get_dynamic_attributes(dart_class, construction=True)
    return '''
factory ClassName.fromJson(String json) => ClassName.fromMap(jsonDecode(json));

factory ClassName.fromMap(Map map){    

    part_declaration

    type_casting

    return return_constructor;
  }
    '''.replace('part_declaration', part_declaration(attrs)) \
        .replace('type_casting', type_cast([i for i in attrs if cf.type_is_iterable(i.type)])) \
        .replace('return_constructor', return_constructor(dart_class)) \
        .replace('ClassName', dart_class.name) \
        .strip()


def enum_from_map(dart_enum: domain.DartEnum):
    option_ifs = ' '.join([f'if (map[\'value\'] == \'{dart_enum.name}.{enum_option}\'){{return {dart_enum.name}.{enum_option};}}'
                           for enum_option in dart_enum.options])
    return f'(Map map){{{option_ifs} throw Exception("Enum {dart_enum.name} can not instantiate ' \
           f'from map $map");}}'


def enum_to_reflected_type(dart_enum: domain.DartEnum):
    return f'ReflectedType.create({dart_enum.name}, "{dart_enum.name}")'


def dart_enum_methods(dart_enum: domain.DartEnum):
    return f'[\n' \
           f'      Method.create("fromMap", {enum_to_reflected_type(dart_enum)}, MethodType.factory, false, null,' \
           f' false, {enum_from_map(dart_enum)}),\n' \
           f'    ]'
