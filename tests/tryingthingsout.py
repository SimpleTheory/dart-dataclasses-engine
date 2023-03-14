import dart_dataclasses.domain as domain
import dart_dataclasses.writing.class_functions as cf
import functools
import dart_dataclasses.writing.json_serialization as js
import dart_dataclasses.file_level.file_level as file_stuff

test_type = domain.Type.from_isolated_string('Map<int, Queue<List<String>>>')
# trial_class = file_stuff.file_reading_procedure_for_classes(r'D:\StudioProjects\ari_utils\test\trying_things.dart')[1]
trial_class2 = file_stuff.file_reading('./test_cache/class.dart')['dataclasses'][-1]
# trial_class3 = file_stuff.file_reading('./../tests/test_cache/dart_core_datetime.dart')['dataclasses'][0]


def generate_casting_code(type_list: list[domain.Type], var_name):
    """
    Generate Dart code for casting a nested dynamic List or Map to the correct type.
    :param type_list: List of types in the nested structure. The last element of the list should be the target type.
    :param var_name: Name of the variable to be casted.
    :return: Dart code for casting the variable to the target type.
    """
    target_type = type_list[-1]
    cast_code = f"{var_name} as {target_type.to_str()}"
    for index, taipu in enumerate(reversed(type_list[:-1])):
        if cf.type_is_map(taipu):
            cast_code = f"({cast_code} as Map<dynamic, dynamic>).map((k{index}, v{index}) => MapEntry(k{index} as " \
                        f"{taipu.generics[0].to_str()}, v{index} as {taipu.generics[1].to_str()})).cast" \
                        f"<{taipu.generics[0].to_str()}, {taipu.generics[1].to_str()}>()"
        elif cf.type_is_iterable(taipu):  # issubclass(taipu, list):
            cast_code = f"({cast_code} as List<dynamic>).map((e{index}) => e{index} " \
                        f"as {taipu.generics[0].to_str()}).toList()"

    return cast_code


def format_type_cast(func):
    @functools.wraps(func)
    def wrapper(taipu, var_name, recursion_level=0):
        result = func(taipu, var_name, recursion_level)
        if not recursion_level:
            return f'{result};'
        else:
            space = '  ' * recursion_level
            return f'\n{space}{result}'

    return wrapper


@format_type_cast
def type_cast_iterable(taipu: domain.Type, var_name: str, recursion_level=0) -> str:
    # nullability_code = ''
    # if taipu.nullable:
    # # nullability_code =
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


if __name__ == '__main__':
    # Variable to cast
    var_name = 'myVar'
    test_type_2 = domain.Type.from_isolated_string('Map<int, Map<int, Map<int, List<String>?>>?>?')
    # print(test_type_2.to_str())
    #
    # # Generate casting code
    casting_code = type_cast_iterable(test_type, var_name)
    casting_code_2 = js.type_cast_iterable(test_type_2, var_name)
    #
    # # Print result
    print(casting_code)
    # print()
    # print(casting_code_2)
    fun_funcs_to_try = [
        cf.constructor,
        cf.static_constructor,
        cf.attributes,
        cf.hashcode,
        cf.equality_operator,
        cf.copy_with,
        cf.to_str,
        js.to_json,
        js.from_json
    ]
    # print()
    # print('-------------')
    # print()
    print(trial_class2)
    for func in fun_funcs_to_try:
        print(func(trial_class2))
        print()
        print('-------------')
        print()
    print(trial_class2.to_dart())
    print()
    print('------------')
    print()
    from dart_dataclasses.insertion.insertions import write_class_functions_main
    print(write_class_functions_main(trial_class2))
