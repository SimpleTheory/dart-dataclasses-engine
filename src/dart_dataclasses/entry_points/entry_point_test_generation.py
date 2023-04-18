import sys
import dart_dataclasses.parsing.config_file as conf
import dart_dataclasses.file_level.file_level as file_level
from dart_dataclasses import domain
from dart_dataclasses.insertion.insert_tests import file_level_test_insertion

def get_all_dataclasses() -> dict[str: domain.Class]:
    all_dataclasses_list: list[domain.Class] = []
    info: dict = file_level.dir_procedure(conf.parsing_path)
    for dataclasses_enums in info.values():
        if dataclasses_enums:
            if dataclasses_enums['dataclasses']:
                all_dataclasses_list.extend(dataclasses_enums['dataclasses'])
    return {cls.name: cls for cls in all_dataclasses_list}

def dir_procedure_for_test_gen():
    for file in conf.testing_path.glob('**/*.dart'):
        if '@CreateTest' in file.read_text():
            file_level_test_insertion(file, get_all_dataclasses())

def entry_test_generation(cwd):
    try:
        conf.config_var_declarations(cwd)
    except conf.ConfigParseError:
        print('ConfigParseError: Either the file was not found in the CWD or'
              ' the config file has some error in it. To generate'
              'a config file in the CWD use command: dart_dataclasses init')
        sys.exit(1)
    dir_procedure_for_test_gen()


if __name__ == '__main__':
    # entry_test_generation(r'D:\StudioProjects\test_dataclasses')
    entry_test_generation(r'D:\StudioProjects\nutrition_app')
