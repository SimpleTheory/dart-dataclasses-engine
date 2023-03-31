import functools
from enum import Enum
import dart_dataclasses.domain as domain
import dart_dataclasses.writing.class_functions as cf
import dart_dataclasses.parsing.config_file as conf

"""
This file specifically focuses on writing the tests and not inserting them or scanning files for them.
That is divided into 2 parts: dataclasses function tests & template tests

Dataclass Function Tests are the tests specifically made for the generated functions given each dataclass
The template tests are just generated templates used to later implement tests for said class methods

At the highest level Dataclass functions will be wrapped in group('Dataclass Function Tests' ,(){}); Within the
brackets each individual test will take place
    The order of which will be
        toString `
        toMap `
        copyWith & == `
        toJson `
        fromMap `
        fromJson `
"""


# <editor-fold desc="Base Known Tests">
def to_str(dart_class: domain.Class, reference: str):
    attrs = cf.get_dynamic_attributes(dart_class)
    to_str_expectation = ", ".join([f'{attr.name}: ${{{reference}.{attr.name}}}' for attr in attrs])
    return f'''
test('{dart_class.name}.toString()', (){{
    String expectation = '{dart_class.name}({to_str_expectation})';
    expect({reference}.toString(), expectation);
}});
'''.strip()


def to_map(dart_class: domain.Class, reference: str):
    # attr_strs = [f'"{attr.name}": {reference}.{attr.name}' for attr in cf.get_dynamic_attributes(dart_class)]
    expectation = f'{{"__type": "{dart_class.name}", ...nestedJsonMap({reference}.attributes__)}}'
    return f'''
    test('{dart_class.name}.toMap()', (){{
        Map<String, dynamic> expectation = {expectation};
        expect({reference}.toMap(), expectation);
    }});
    '''.strip()


def to_json(dart_class: domain.Class, reference: str):
    return f'''
    test('{dart_class.name}.toJson()', (){{
        String expectation = jsonEncode({reference}.toMap());
        expect({reference}.toJson(), expectation);
    }});
    '''.strip()


def copy_with_and_eq(dart_class: domain.Class, reference: str):
    if method_in_class(f'copyWith{dart_class.name}', dart_class):
        copy_with_name = f'copyWith{dart_class.name}'
    else:
        copy_with_name = 'copyWith'
    return f'''
    test('{dart_class.name} == and copyWith', (){{
        {dart_class.name} copy = {reference}.{copy_with_name}();
        bool eq = {reference} == copy;
        expect(eq, true);
        expect(copy, {reference});
    }});
    '''.strip()


def from_map(dart_class: domain.Class, reference: str):
    return f'''
    test('{dart_class.name}.fromMap() and ==', (){{
        Map<String, dynamic> map = {reference}.toMap();
        {dart_class.name} expectation = {dart_class.name}.fromMap(map);
        expect({reference}, expectation);
    }});
    '''.strip()


def from_json(dart_class: domain.Class, reference: str):
    return f'''
    test('{dart_class.name}.fromJson() and ==', (){{
        String json = {reference}.toJson();
        {dart_class.name} expectation = {dart_class.name}.fromJson(json);
        expect({reference}, expectation);
    }});
    '''.strip()


def static_constructor(dart_class: domain.Class, reference: str):
    attr_strs = [f'{attr.name}: {reference}.{attr.name}' for attr in cf.get_dynamic_attributes(dart_class)]
    expectation = f'{dart_class.name}.staticConstructor({", ".join(attr_strs)})'
    return f'''
    test('{dart_class.name}.staticConstructor()', (){{
        {dart_class.name} expectation = {expectation};
        expect(expectation.runtimeType, {dart_class.name});
    }});
    '''.strip()


def base_known_tests(dart_class: domain.Class, reference: str) -> str:
    tests = []

    if method_in_class('toString', dart_class):
        tests.append(to_str(dart_class, reference))

    if method_in_class('toMap', dart_class) and 'attributes__' in [gettr.name for gettr in dart_class.getters]:
        tests.append(to_map(dart_class, reference))

    if method_in_class('==', dart_class) \
            and \
            any([method_in_class('copyWith', dart_class),
                 method_in_class(f'copyWith{dart_class.name}', dart_class)]):
        tests.append(copy_with_and_eq(dart_class, reference))

    if method_in_class('toJson', dart_class):
        tests.append(to_json(dart_class, reference))

    if method_in_class('fromMap', dart_class):
        tests.append(from_map(dart_class, reference))

    if method_in_class('fromJson', dart_class):
        tests.append(from_json(dart_class, reference))

    if method_in_class('staticConstructor', dart_class) \
            and cf.check_for_bool_dataclass_args('staticConstructor', dart_class):
        tests.append(static_constructor(dart_class, reference))

    return cf.left_pad_string("\n\n".join(tests), 2)


# </editor-fold>

dataclass_methods = ['==', 'toString', 'toMap', 'toJson', 'fromMap', 'fromJson', 'copyWith', 'staticConstructor']


# <editor-fold desc="Base Template Tests">

def comment_out_body(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, str):
            result = '// ' + result.replace('\n', '\n//')
        return result

    return wrapper


@comment_out_body
def method_body(dart_class: domain.Class, method: domain.Method, reference: str) -> str:
    if method.method_type == domain.MethodType.factory or method.static:
        reference = f'{dart_class.name}'
    if method.return_type.type == 'void' or not method.return_type:
        return f'{reference}.{method.name}();'
    if method.method_type == domain.MethodType.operator:
        return f'{method.return_type.to_str()} result = {reference} {method.name} ;'
    return f'{method.return_type.to_str()} result = {reference}.{method.name}();'


def convert_to_test(name: str, body: str) -> str:
    return f'''
test('{name}',(){{
  // TODO: complete test
  {body}
  // expect(result, expectation);
}});
'''


def base_template_test_unit(dart_class: domain.Class, method: domain.Method, reference: str) -> str:
    body = method_body(dart_class, method, reference)
    return convert_to_test(f'{dart_class.name}.{method.name}', body)


def base_template_tests(dart_dataclass: domain.Class, reference: str):
    template_methods = [method for method in dart_dataclass.methods
                        if not any([method.method_type == domain.MethodType.constructor,
                                    method.name == f'copyWith{dart_dataclass.name}',
                                    method.name in dataclass_methods
                                    ])]
    result = "\n".join([base_template_test_unit(dart_dataclass, method, reference) for method in template_methods])
    return cf.left_pad_string(result, 2).rstrip()


# </editor-fold>

class TestType(Enum):
    known = 1
    template = 2


def gen_tests(test_type: TestType, dart_class: domain.Class, reference: str) -> str:
    if test_type == TestType.known:
        base = base_known_tests(dart_class, reference)
        group_name = f'{dart_class.name} Dataclass Methods'
        decorator = f'@Cr8Tests({dart_class.name}, \'{reference}\')'
    else:
        base = base_template_tests(dart_class, reference)
        group_name = f'{dart_class.name} Tests'
        decorator = f'@Cr8TestTemplates({dart_class.name}, \'{reference}\')'
    if not conf.default_regeneration:
        decorator = ''
    result = f'''
{decorator}
void {group_name[0].lower() + group_name[1:].replace(' ', '')}(){{
    group('{group_name}', (){{
    {base}
  }});
}}
'''
    return result


# <editor-fold desc="Utils">
def method_in_class(name: str, dart_dataclass: domain.Class):
    return name in [method.name for method in dart_dataclass.methods]

# </editor-fold>
