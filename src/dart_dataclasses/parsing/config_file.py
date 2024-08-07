from pathlib import Path
import re


class ConfigParseError(Exception):
    pass


config_file_name_and_ext = 'dataclasses.config'


def parse_config_file(config_file: Path = Path(f'./{config_file_name_and_ext}')):
    with open(config_file, 'r') as f:
        content = f.read()
    lines = [line.strip() for line in content.splitlines()]
    lines_split = [re.split(r'\s*=\s*', line) for line in lines
                   if all([line, not line.startswith('#'), not line.startswith('[')])]
    configs = {line[0]: line[1] for line in lines_split}
    return configs


cwd: Path = None
config_file_dict: dict = None
parsing_path: Path = None
output_path: Path = None
testing_path: Path = None
metadata_file: Path = None
preferred_editor: str = None
warning_message: str = None
reference_private_methods: bool = None
format_files_with_insertion: bool = None
default_map_method_for_non_dataclass_api_instantiation: str = 'fromApiMap'
default_regeneration: str = ''


def config_var_declarations(inputted_cwd: Path | str):
    global cwd
    global config_file_dict
    global parsing_path
    global output_path
    global metadata_file
    global preferred_editor
    global warning_message
    global reference_private_methods
    global format_files_with_insertion
    global default_regeneration
    global testing_path
    global default_map_method_for_non_dataclass_api_instantiation

    try:
        cwd = Path(inputted_cwd)
        config_file_dict = parse_config_file(cwd.joinpath('dataclasses.config'))
        parsing_path = cwd.joinpath(Path(config_file_dict['parsing_path']))
        testing_path = cwd.joinpath(Path(config_file_dict['testing_path']))
        output_path = cwd.joinpath(Path(config_file_dict['output_path']))
        metadata_file = output_path.joinpath('metadata.dart')

        ensure_path_exists(parsing_path)
        ensure_path_exists(output_path)

        preferred_editor = config_file_dict['preferred_editor']
        warning_message = '''
    // WARNING! Any code written in this section is subject to be overwritten! 
    // Please move any code you wish to save outside of this section. 
    // Or else the next time the code generation runs your code will be overwritten!
    // If you wish to keep the capabilities of your class as a Dataclass, and
    // disable the code generation, delete the @Generate decorator.
        '''.strip() if config_file_dict['warning_message'].lower() == 'true' else ''
        reference_private_methods = config_file_dict['reference_private_methods'].lower() == 'true'
        format_files_with_insertion = config_file_dict['format_files_with_insertion'].lower() == 'true'
        default_map_method_for_non_dataclass_api_instantiation = config_file_dict['default_map_method_for_non_dataclass_api_instantiation']
        if config_file_dict['default_regeneration'].lower() == 'true':
            default_regeneration = '@Generate()\n'
    except:
        raise ConfigParseError()


def ensure_path_exists(path: str | Path):
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


def encapsulate_region(name, text):
    if preferred_editor == 'vscode':
        return f'//region {name}\n{text}\n//endregion\n'
    if preferred_editor == 'pound_vscode':
        return f'//#region {name}\n{text}\n//#endregion\n'
    if preferred_editor == 'jetbrains':
        return f'// <editor-fold desc="{name}">\n{text}\n// </editor-fold>\n'
    return f'// ------------------------ {name} --------------------------------\n{text}\n' \
           f'// ------------------------ End {name} --------------------------------\n'


if __name__ == '__main__':
    config_var_declarations(r'D:\StudioProjects\test_dataclasses')
    print(parsing_path)
    print(output_path)
