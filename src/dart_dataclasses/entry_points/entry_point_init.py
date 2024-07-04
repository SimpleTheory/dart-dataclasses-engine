"""
entry_init(cwd, source=)
"""
from pathlib import Path
import sys

default = '''
[Examples]
# Write relative paths to project dir (parent of this file)
# Example: parsing_path = ./lib
# Example: output_path = ./mydataclasses

[Pathing]
# Path to parse all dataclasses and enums
parsing_path = ./lib
# For output of non-inserted generated code (MUST BE IN LIB FOR AUTOMATIC IMPORTS TO WORK!!!!)
output_path = ./lib/mydataclasses
# For insertion of generated tests given the right decorators
testing_path = ./test

[Options]
# Options: vscode, pound_vscode, jetbrains, other
# (this will change some internal settings namely how the generated code will be organized)
preferred_editor = jetbrains
warning_message = True
reference_private_methods = False
# Will run dart format on files with insertion
format_files_with_insertion = True
# This causes generated class to auto-mark their code for replacement if the program is rerun
default_regeneration = True
# What method should the program call if it doesn't know how to instantiate the class from an unmarked Map
# (just use name with no preceding .)
default_map_method_for_non_dataclass_api_instantiation = fromApiMap
'''.strip()

def check_given_source(given_source: str):
    given_source = Path(given_source)
    if any([not given_source.exists(), given_source.name == 'dataclasses', given_source.stem == 'config']):
        raise FileNotFoundError(f'Given source file for config {given_source} was either not found or not called '
                                f'dataclasses.config')
    return given_source

def write_to_config(cwd, source=None):
    config_content = source.read_text() if source else default
    config_path = cwd.joinpath('dataclasses.config')
    if config_path.exists():
        raise FileExistsError(f'{config_path} already exists, please delete or move file to'
                              f'a different dir before re-running.')
    with open(config_path, 'w') as f:
        f.write(config_content)
def main():
    # Parse args
    global source_file
    args = sys.argv[1:]
    cwd = Path().cwd()
    try:
        source_file = check_given_source(args[0])
    except IndexError:
        pass
    # Write to file
    write_to_config(cwd)


if __name__ == '__main__':
    main()
    # write_to_config(Path(r'D:\StudioProjects\test_dataclasses'))
