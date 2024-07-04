import copy
import dart_dataclasses.domain as domain
import dart_dataclasses.writing.class_functions as cf
import functools
import dart_dataclasses.parsing.config_file as config
import dart_dataclasses.writing.json_serialization as js
import dart_dataclasses.file_level.file_level as file_stuff
import dart_dataclasses.insertion.insertions as insert
import dart_dataclasses.insertion.insert_tests as test_insert
from pathlib import Path
import dart_dataclasses.parsing.config_file as conf
import dart_dataclasses.file_level.file_level as file_level
from dart_dataclasses.utils import project_root
import dart_dataclasses.writing.api_serialization as api


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


def final_case(varname: str, taipu: domain.Type, dataclasses):
    nullability_code = ''
    if api.type_is_dataclass(taipu, dataclasses):
        if taipu.nullable:
            nullability_code = f'{varname} == null ? null : '
            # type2defaults[Duration]!.fromMap!
        return f'{nullability_code}type2reflection[{taipu.type}]!.fromMap!({varname})'
    if type_is_non_collection_json_safe(taipu):
        return f'{varname} as {taipu.to_str()}'


def copy_with_final_case(varname: str, taipu: domain.Type, dataclasses):
    nullability_code = ''
    if api.type_is_dataclass(taipu, dataclasses) == api.ClassType.dataclass:
        if taipu.nullable:
            nullability_code = f'{varname} == null ? null : '
            # type2defaults[Duration]!.fromMap!
        return f'{nullability_code}{varname}.copyWith{taipu.type}()'
    else:
        return varname


def type_is_non_collection_json_safe(taipu: domain.Type):
    return taipu.type in domain.json_safe_types[2:]


@format_type_cast_for_api
def type_cast_iterable_for_api(taipu: domain.Type, var_name: str, dataclasses: list[domain.Class], recursion_level=0,
                               base_padding=4, pad_amount=4) -> str:
    nullability_code = ''
    new_line_code = f'\n{(base_padding * " ") + (" " * pad_amount * recursion_level)}'
    if taipu.nullable:
        taipu = copy.copy(taipu)
        taipu.nullable = False
        nullability_code = f'{var_name} == null ? null : {new_line_code}'

    # generic listlike
    if len(taipu.generics) == 1 and taipu.generics[0].generics:
        return f'{nullability_code}{cf.iterable_factory(taipu)}{var_name}.map((__e{recursion_level}) ' \
               f'=> {type_cast_iterable_for_api(taipu.generics[0], f"__e{recursion_level}", dataclasses, recursion_level + 1)}).toList())'
    # generic maplikes
    if len(taipu.generics) > 1:

        # Mappy key and value
        if all([taipu.generics[1].generics, taipu.generics[0].generics]):
            return f'{nullability_code}{cf.iterable_factory(taipu)}{var_name}.map((__k{recursion_level}, __v{recursion_level}) ' \
                   f'=> MapEntry(' \
                   f'{type_cast_iterable_for_api(taipu.generics[0], f"__k{recursion_level}", dataclasses, recursion_level + 1)}, ' \
                   f'{type_cast_iterable_for_api(taipu.generics[1], f"__v{recursion_level}", dataclasses, recursion_level + 1)})))'

        # Mappy Value
        if len(taipu.generics) > 1 and taipu.generics[1].generics:
            # __k{recursion_level} as {taipu.generics[0].to_str()
            return f'{nullability_code}{cf.iterable_factory(taipu)}{var_name}.map((__k{recursion_level}, __v{recursion_level}) ' \
                   f'=> MapEntry({final_case(f'__k{recursion_level}', taipu.generics[0], dataclasses)}, ' \
                   f'{type_cast_iterable_for_api(taipu.generics[1], f"__v{recursion_level}", dataclasses, recursion_level + 1)})))'

        # Mappy Key
        if len(taipu.generics) > 1 and taipu.generics[0].generics:
            # __v{recursion_level} as {taipu.generics[1].to_str()}
            return f'{nullability_code}{cf.iterable_factory(taipu)}{var_name}.map((__k{recursion_level}, __v{recursion_level}) ' \
                   f'=> MapEntry({type_cast_iterable_for_api(taipu.generics[0], f"__k{recursion_level}", dataclasses, recursion_level + 1)}, ' \
                   f'{final_case(f'__v{recursion_level}', taipu.generics[1], dataclasses)})))'
    # __k{recursion_level} as {taipu.generics[0].to_str()}
    # regular listlike
    if len(taipu.generics) == 1:
        if api.type_is_dataclass(taipu.generics[0], dataclasses):
            non_nullable_taipu = copy.copy(taipu.generics[0])
            non_nullable_taipu.nullable = False
            base_var = f'__v{recursion_level}'
            # base_nullability = f'{base_var} == null ? null : ' if taipu.generics[0].nullable else ''
            # randomList.map<Example>((element) => Example.fromMap(element))
            # List<Example>.from(randomList.map<Example>((element) => Example.fromMap(element)))
            return (f'{nullability_code}{cf.iterable_factory(taipu)}{var_name}.map(({base_var})'
                    f' => {final_case(base_var, taipu.generics[0], dataclasses)}))')
        return f'{nullability_code}{cf.iterable_factory(taipu)}{var_name})'
    # regular maplike
    if len(taipu.generics) > 1:
        # __k{recursion_level} as {taipu.generics[0].to_str()}
        # __v{recursion_level} as {taipu.generics[1].to_str()}
        return f'{nullability_code}{cf.iterable_factory(taipu)}{var_name}.map((__k{recursion_level}, __v{recursion_level}) ' \
               f'=> MapEntry({final_case(f'__k{recursion_level}', taipu.generics[0], dataclasses)},' \
               f' {final_case(f'__v{recursion_level}', taipu.generics[1], dataclasses)})))'
    raise Exception('Type casting exception!')


def entry_main(cwd):
    import sys
    try:
        config.config_var_declarations(cwd)
    except config.ConfigParseError:
        print('ConfigParseError: Either the file was not found in the CWD or'
              ' the config file has some error in it. To generate'
              'a config file in the CWD use command: dart_dataclasses init')
        sys.exit(1)
    initial_file_classes = file_level.dir_procedure(config.parsing_path)
    return initial_file_classes


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
        if api.type_is_dataclass(taipu, dataclasses_and_enums):
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
        if api.type_is_dataclass(taipu.generics[0], dataclasses_and_enums):
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


if __name__ == '__main__':
    # file = project_root() / r'tests/test_cache/class.dart'
    # # f2 = Path(r'D:\StudioProjects\test_dataclasses\lib\test_dataclasses.dart')
    # f3 = project_root() / r'tests/test_cache/nut_app_test.dart'
    # file_for_test_gen = project_root() / r'tests/test_cache/test_classes.dart'
    # trial = file_stuff.file_reading(project_root() / r'tests/test_cache/class.dart')
    # trial2 = file_stuff.file_reading(f3)
    # print(trial2)
    # print([i for i in trial2['dataclasses'][0].methods if i.method_type == domain.MethodType.named_constructor])

    # test_type = domain.Type.from_isolated_string('Map<int, Queue<List<String>>>')
    # # trial_class = file_stuff.file_reading_procedure_for_classes(r'D:\StudioProjects\ari_utils\test\trying_things.dart')[1]
    # trial_class2: domain.Class = \
    # file_stuff.file_reading(project_root() / r'tests/test_cache/class.dart')['dataclasses'][-1]

    # # Variable to cast
    init_class_dict = entry_main(r'C:\projects\flutter_projects\nutrition_app')
    all_ = insert.comprehensive_list_of_all_dataclasses_and_enums(init_class_dict)
    print([(index, value.name) for index, value in enumerate(all_)])
    print()
    print(api.from_api(all_[15], all_))
    print()
    print(api.copy_with(all_[15], all_))
    # print('\n------------\n')
    # print(from_api(all_[7], all_))

    # var_name = 'myVar'
    # test_type_2 = domain.Type.from_isolated_string('Map<int, Map<Uri?, Map<int, List<Duration?>?>>?>?')
    # # print(test_type_2.to_str())
    # #
    # # # Generate casting code
    # casting_code = type_cast_iterable_for_api(test_type_2, var_name, trial['dataclasses'])
    # casting_code_2 = js.type_cast_iterable(test_type_2, var_name)
    # #
    # # # Print result
    # from_api()
    # print(casting_code)
    print()
    # print(casting_code_2)
    # fun_funcs_to_try = [
    # #     cf.constructor,
    # #     cf.static_constructor,
    # #     cf.attributes,
    # #     cf.hashcode,
    # #     cf.equality_operator,
    #     cf.copy_with,
    # #     cf.to_str,
    # #     js.to_json,
    #     js.from_json
    # ]
    # # print()
    # # print('-------------')
    # # print()
    # print(trial_class2)
    # for func in fun_funcs_to_try:
    #     print(func(trial_class2))
    #     print()
    #     print('-------------')
    #     print()
    # print(trial_class2.to_dart())
    # print()
    # print('------------')
    # print()
    # from dart_dataclasses.insertion.insertions import write_class_functions_main
    # print(write_class_functions_main(trial_class2))
    # insert.dataclass_insertions(file, trial['dataclasses'])
    # Assuming no default regen
    # conf.default_regeneration = '@Generate'
    # conf.preferred_editor = 'jetbrains'
    # yes = test_insert.file_level_test_insertion(file_for_test_gen, {trial_class2.name: trial_class2})
