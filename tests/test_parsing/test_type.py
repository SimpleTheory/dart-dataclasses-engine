from dart_dataclasses.domain import *

def test_clean_subgenerics():
    x=Type.clean_generics_in_generics_string('int, Map<int, Map<int, List<String>>>')
    assert x == ('int, Map____sub_0____', ['<int, Map<int, List<String>>>'])

def test_new_type_constructor():
    test_type_2 = Type.from_isolated_string('Map<int, Map<int, Map<int, List<String>>>>')
    assert 'Map<int, Map<int, Map<int, List<String>>>>' == test_type_2.to_str()
def test_nested_map():
    supposed_to_be =  \
        Type('Map', False, [
               Type('int', False), Type('Map', False, [
                   Type('int', False), Type('Map', False, [
                        Type('int', False),
                        Type('List', False, [Type('String', False)])
                   ])
               ])
           ])

    test_type_2 = Type.from_isolated_string('Map<int, Map<int, Map<int, List<String>>>>')
    assert supposed_to_be.to_str() == 'Map<int, Map<int, Map<int, List<String>>>>'
    print()
    print('pass1')
    assert test_type_2.to_str() == supposed_to_be.to_str()

