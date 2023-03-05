import functools
import dart_dataclasses.domain as domain
import dart_dataclasses.writing.class_functions as cf

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
        List family_temp = recursiveFromJsonIterable(json[family]);
        String name = map[name]
        
        List<Person> family = iterable_type_cast(family.type, f'{family.name}_temp')
        
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
Map toMap()=> {'__type': 'ClassName', ...nestedJsonMap(__attributes)}'''.replace('ClassName', dart_class.name).strip()


def part_declaration_procedure(attr: domain.Attribute) -> str:
    if cf.type_is_iterable(attr.type):
        temp_type = 'List'
        if 'map' in attr.type.type.lower():
            temp_type = 'Map'
        return f'{temp_type}? {attr.name}_temp = recursiveFromJsonIterable(map[{attr.name}]);'
    if attr.type.type in domain.json_safe_types:
        return f'{attr.type.to_str()} {attr.name} = map[{attr.name}];'
    # TODO MODIFY BELOW LINES IN THIS FUNCTION SUCH THAT:
    # Address address = jsonFactoryMap['Address']!(map[address]); NOT THIS!! Rather
    # Address address = Address.fromMap(map[address])
    if attr.type.nullable:
        return f'{attr.type.to_str()} {attr.name} = ' \
               f'jsonFactoryMap[\'{attr.type.type}\'] == null ? null : (map[{attr.name}]);'
    return f'{attr.type.to_str()} {attr.name} = jsonFactoryMap[\'{attr.type.type}\']!(map[{attr.name}]);'


def part_declaration(dynamic_attributes: list[domain.Attribute]) -> str:
    return "\n    ".join([part_declaration_procedure(attr) for attr in dynamic_attributes])


def format_type_cast(func):
    @functools.wraps(func)
    def wrapper(taipu, var_name, recursion_level=0, base_padding=4, pad_amount=2):
        result = func(taipu, var_name, recursion_level)
        base_padding_space = ' ' * base_padding
        if not recursion_level:
            return f'{base_padding_space}{result};'
        else:
            space = ' ' * pad_amount * recursion_level
            return f'\n{base_padding_space}{space}{result}'

    return wrapper


@format_type_cast
def type_cast_iterable(taipu: domain.Type, var_name: str, recursion_level=0) -> str:
    # generic listlike
    if len(taipu.generics) == 1 and taipu.generics[0].generics:
        return \
            f'{cf.iterable_factory(taipu)}{var_name}.map((__e{recursion_level}) ' \
            f'=> {type_cast_iterable(taipu.generics[0], f"__e{recursion_level}", recursion_level + 1)}).toList())'
    # generic maplike
    if len(taipu.generics) > 1 and taipu.generics[1].generics:
        return \
            f'{cf.iterable_factory(taipu)}{var_name}.map((__k{recursion_level}, __v{recursion_level}) ' \
            f'=> MapEntry(__k{recursion_level} as {taipu.generics[0].to_str()}, ' \
            f'{type_cast_iterable(taipu.generics[1], f"__v{recursion_level}", recursion_level + 1)})))'
    # regular listlike
    if len(taipu.generics) == 1:
        return f'{cf.iterable_factory(taipu)}{var_name})'
    # regular maplike
    if len(taipu.generics) > 1:
        f'{cf.iterable_factory(taipu)}{var_name}.map((__k{recursion_level}, __v{recursion_level}) ' \
        f'=> MapEntry(__k{recursion_level} as {taipu.generics[0].to_str()},' \
        f' __v{recursion_level} as {taipu.generics[1].to_str()})))'
    return ''


def type_cast(list_of_attributes_to_cast: list[domain.Attribute], base_padding=4):
    if not list_of_attributes_to_cast:
        return '\\\\ No casting'
    casts = []
    for attribute in list_of_attributes_to_cast:
        if attribute.type.nullable:
            casts.append(
                f'if ({attribute.name}_temp == null)***{attribute.type.to_str()} '
                f'{attribute.name} = null%%%\n{base_padding * " "}'
                f'else***{attribute.type.to_str()} {attribute.name} =\n'
                f'{type_cast_iterable(attribute.type, f"{attribute.name}_temp", base_padding=base_padding+4)}'
                f'\n{base_padding * " "}%%%'
                .replace('***', '{')
                .replace('%%%', '}')
            )
        else:
            casts.append(
                f'{"Map" if cf.type_is_map(attribute.type) else "List"} '
                f'{attribute.name}_temp_2 = {attribute.name}_temp!;\n{base_padding * " "}'
                f'{attribute.type.to_str()} {attribute.name} =\n'
                f'{type_cast_iterable(attribute.type, f"{attribute.name}_temp_2", base_padding=base_padding+4)}'
            )

    return '\n    '.join(casts)


def return_constructor(dart_class: domain.Class) -> str:
    return f'{dart_class.name}' \
           f'({", ".join([f"{attr.name}: {attr.name}" for attr in cf.get_dynamic_attributes(dart_class)])})'


def from_json(dart_class: domain.Class) -> str:
    return '''
factory fromJson(String json) => ClassName.fromMap(jsonDecode(json));

factory fromMap(Map map){    

    part_declaration

    type_casting

    return return_constructor;
}
    '''.replace('part_declaration', part_declaration(cf.get_dynamic_attributes(dart_class))) \
        .replace('type_casting',
                 type_cast([i for i in cf.get_dynamic_attributes(dart_class) if cf.type_is_iterable(i.type)])
                 ) \
        .replace('return_constructor', return_constructor(dart_class)) \
        .replace('ClassName', dart_class.name) \
        .strip()
