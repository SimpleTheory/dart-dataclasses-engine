from enum import Enum
from pathlib import Path, PurePath
import re


class ConfigParseError(Exception):
    pass


config_file_name_and_ext = 'dataclases.config'


def parse_config_file(config_file: Path = Path(f'./{config_file_name_and_ext}')):
    with open(config_file, 'r') as f:
        content = f.read()
    lines = [line.strip() for line in content.splitlines()]
    lines_split = [re.split('\s*=\s*', line) for line in lines
                   if all([line, not line.startswith('#'), not line.startswith('[')])]
    configs = {line[0]: line[1] for line in lines_split}
    return configs


def ensure_path_exists(path: str):
    """
    Checks if a path exists, and creates it if it doesn't.
    """
    given_path = Path(path)
    if not given_path.exists():
        given_path.mkdir(parents=True, exist_ok=True)


def create_config_file(project_dir: str):
    config_path = Path(project_dir).joinpath('dataclasses.config')
    with open('/../../../cache/dataclasses.config', 'r') as default:
        default_config_content = default.read()
        with open(config_path, 'w+') as new_file:
            new_file.write(default_config_content)
            # Maybe have them fill in a questioner as its created?


# TODO: Implement config file and parsing

try:
    config_file_dict = parse_config_file(Path(r'D:\PycharmProjects\dart_dataclasses\cache\dataclasses.config'))
    # TODO Change to project home dir when working with bash ^^
    parsing_path = Path(config_file_dict['parsing_path'])
    output_path = Path(config_file_dict['parsing_path'])

    # ensure_path_exists(parsing_path) # TODO UNCOMMENT
    # ensure_path_exists(output_path)

    preferred_editor: str = config_file_dict['preferred_editor']
    warning_message: str = '''
// WARNING! Any code written in this section is subject to be overwritten! Please move any code you wish to save outside
// of this section. Or else the next time the code generation runs your code will be overwritten! (Even if you disable
// said functions in the @Dataclass() annotation. If you wish to keep the capabilities of your class as a Metaclass and
// disable the code generation, change the annotation to @Metaclass).
    '''.strip() if config_file_dict['warning_message'].lower() == 'true' else ''
    reference_private_methods: bool = config_file_dict['reference_private_methods'].lower() == 'true'
    format_files_with_insertion: bool = config_file_dict['format_files_with_insertion'].lower() == 'true'

    insertion_imports = [config_file_dict['parsing_path'] + '/mydataclasses.dart']
    insertion_imports_strings = [f'import \'{file}\';' for file in insertion_imports]

except:
    raise ConfigParseError()


def encapsulate_region(name, text):
    if preferred_editor == 'vscode':
        return f'//region {name}\n{text}\n//endregion'
    if preferred_editor == 'jetbrains':
        return f'// <editor-fold desc="{name}">\n{text}\n// </editor-fold>'
    return f'// ------------------------ {name} --------------------------------\n{text}\n'


if __name__ == '__main__':
    print(config_file_dict)
    print(parsing_path)
    print(output_path)
