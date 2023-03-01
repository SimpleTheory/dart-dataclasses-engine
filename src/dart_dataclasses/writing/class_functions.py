import dart_dataclasses.domain as domain
import json


def constructor(dart_class: domain.Class) -> str:
    attrs_to_initialize = list(filter(
        lambda attribute: not any([attribute.external, attribute.static, attribute.late, attribute.const]),
        dart_class.attributes
    ))
    required, null = separate_null_required(attrs_to_initialize)

    base = f'{dart_class.name}(***{"".join([f"required this.{attr.name}, " for attr in required])}' \
           f'{", ".join([f"this.{attr.name}" for attr in null])}%%%)' \
        .replace('***', '{').replace('%%%', '}')

    if dart_class.parent:
        try:
            call_to_super = 'super.' + dart_class.dataclass_annotation.keyword_params['superFactory'][1:-1].strip()
        except KeyError:
            call_to_super = 'super'
        super_pos, super_kwarg = separate_pos_and_kwarg_super(attrs_to_initialize)
        print(super_pos, super_kwarg)

        parent = f'{call_to_super}({"".join([f"{pos.name}, " for pos in super_pos])}' \
                 f'{", ".join([f"{kwarg.super_param}: {kwarg.name}" for kwarg in super_kwarg])})'

        return f'{base} : {parent};'
    return base + ';'


def attributes(dart_class: domain.Class) -> str:
    attr_strs = [f'"{attr.name}": {attr.name}' for attr in get_dynamic_attributes(dart_class)]
    return f'Map get __attributes => ***{", ".join(attr_strs)}%%%;'.replace('***', '{').replace('%%%', '}')


def copy_with(dart_class: domain.Class) -> str:
    dynamic_attributes = get_dynamic_attributes(dart_class)
    null = lambda x: x if x.endswith('?') else x + '?'
    attrs_params = ", ".join([f'{null(attr.type.to_str())} {attr.name}' for attr in dynamic_attributes])
    attr_body = ", ".join([f'{attr.name}: {attr.name} ?? this.{attr.name}' for attr in dynamic_attributes])
    return f'{dart_class.name} copyWith{dart_class.name}({attrs_params}) => {dart_class.name}({attr_body});'


def equality_operator(dart_class: domain.Class) -> str:
    dynamic_attributes = get_dynamic_attributes(dart_class)
    base = f'@override\n' \
           f'bool operator ==(Object other) =>\n' \
           f'  identical(this, other) || '
    dynamic_attributes_equality = [f'equals({attr.name}, other.{attr.name})' for attr in dynamic_attributes]
    dynamics = [f'other is {dart_class.name}', 'runtimeType == other.runtimeType', *dynamic_attributes_equality]
    return f'{base}({" && ".join(dynamics)});'


def hashcode(dart_class: domain.Class) -> str:
    base = '@override\nint get hashCode => '
    body = " ^ ".join([f'{attr.name}.hashCode' for attr in get_dynamic_attributes(dart_class)])
    return base + body + ';'


# JSON SKELLY FACEEEEE!!!!! -----------------------
def to_json(dart_class: domain.Class) -> str:
    return '''
String toJson()=>jsonEncode(toMap());
Map toMap()=> {'__type': 'ClassName', ...nestedJsonMap(__attributes)}'''.replace('ClassName', dart_class.name)

def part_declaration_procedure(attr: domain.Attribute) -> str:
    if type_is_iterable(attr.type):
        temp_type = 'List'
        if 'map' in attr.type.type.lower():
            temp_type = 'Map'
        return f'{temp_type}? {attr.name}_temp = recursiveFromJsonIterable(map[{attr.name}]);'
    if attr.type.type in domain.json_safe_types:
        return f'{attr.type.to_str()} {attr.name} = map[{attr.name}];'
    if attr.type.nullable:
        return f'{attr.type.to_str()} {attr.name} = ' \
               f'jsonFactoryMap[\'{attr.type.type}\'] == null ? null : (map[{attr.name}]);'
    return f'{attr.type.to_str()} {attr.name} = jsonFactoryMap[\'{attr.type.type}\']!(map[{attr.name}]);'


def part_declaration(dynamic_attributes: list[domain.Attribute]) -> str:
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
    }
    Address address = json[address].fromJson();
    List family = recursiveFromJsonIterable(json[family]);
    String name = json[name]
----------
    Let it be that recursiveFromJsonIterable(Iterable iter) is a fx that takes in a Map or List and returns that same Map
    or List as is with the same level of recursion, but with all valid objects instantiated therein! Such
    that the only uninitialized things there are Iterable types and the correct type castings.

    However, if it receives a null value arg then let it return null as well.

    Let it be that a map called jsonFactoryMap<String, Function> maps the Class names to their respective
     factory method 'Person': Person.fromMap, such that jsonFactoryMap
    """
    return "\n".join([part_declaration_procedure(attr) for attr in dynamic_attributes])

def type_casting(iterable_types: list[domain.Attribute]) -> str:
    if not iterable_types:
        return ''
    # TODO IMPLEMENT ITERABLE TYPES

def return_constructor(dart_class: domain.Class) -> str:
    return f'{dart_class.name}' \
           f'({", ".join([f"{attr.name}: {attr.name}" for attr in get_dynamic_attributes(dart_class)])})'
def from_json(dart_class: domain.Class) -> str:
    return '''
factory fromJson(String json) => ClassName.fromMap(jsonDecode(json));

factory fromMap(Map map){    

    part_declaration
    
    type_casting
    
    return return_constructor;
}
    '''.replace('part_declaration', part_declaration(get_dynamic_attributes(dart_class))) \
       .replace('type_casting', type_casting([i for i in get_dynamic_attributes(dart_class) if type_is_iterable(i.type)])) \
       .replace('return_constructor', return_constructor(dart_class)) \
       .replace('ClassName', dart_class.name)

# ---------------------------------------------------------------------------
# Sub writing

# ----------------------------------------------------------------------------
# Utility Functions
def separate_null_required(attrs: list[domain.Attribute]) -> tuple[list[domain.Attribute], list[domain.Attribute]]:
    required = list(
        filter(lambda attribute: not attribute.type.nullable and not attribute.late and not attribute.default_value,
               attrs))
    null = list(filter(lambda attribute: attribute.type.nullable or attribute.late or attribute.default_value, attrs))
    return required, null


def separate_pos_and_kwarg_super(attrs: list[domain.Attribute]) -> tuple[
    list[domain.Attribute], list[domain.Attribute]]:
    super_attrs = list(filter(lambda attribute: attribute.super_param, attrs))
    print(list(super_attrs))
    pos = sorted(
        filter(lambda attr: attr.super_param[0] == '+', super_attrs),
        key=lambda attr: len(attr.super_param)
    )

    kwarg = list(
        filter(lambda attr: attr.super_param[0] != '+', super_attrs)
    )
    return pos, kwarg


def get_dynamic_attributes(attrs: list[domain.Attribute] | domain.Class) -> list[domain.Attribute]:
    if isinstance(attrs, domain.Class):
        attrs = attrs.attributes
    return list(filter(
        lambda attribute: not any([attribute.external, attribute.static, attribute.const]),
        attrs
    ))


def type_is_iterable(type_: domain.Type) -> bool:
    return type_.type in domain.iterable_types


def iterable_factory(type_: domain.Type) -> str:
    return type_.type + '.from(' if type_.type != 'Iterable' else type_.type + '.castFrom('


if __name__ == '__main__':
    from dart_dataclasses.file_level.file_level import file_reading_procedure_for_classes

    trial_class = file_reading_procedure_for_classes(r'D:\StudioProjects\ari_utils\test\trying_things.dart')[1]
    print(constructor(trial_class))
