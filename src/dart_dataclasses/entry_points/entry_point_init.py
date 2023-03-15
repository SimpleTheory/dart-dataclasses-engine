"""
entry_init(cwd, source=)
"""
from pathlib import Path
import sys

source_file = Path('../../../cache/dataclasses.config').resolve()


def check_given_source(given_source: str):
    given_source = Path(given_source)
    if any([not given_source.exists(), given_source.name == 'dataclasses', given_source.stem == 'config']):
        raise FileNotFoundError(f'Given source file for config {given_source} was either not found or not called '
                                f'dataclasses.config')
    return given_source

def write_to_config(cwd, source=source_file):
    config_content = source.read_text()
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
    cwd = Path(args[0])
    try:
        source_file = check_given_source(args[1])
    except IndexError:
        pass
    # Write to file
    write_to_config(cwd)


if __name__ == '__main__':
    main()
    # write_to_config(Path(r'D:\StudioProjects\test_dataclasses'))
