"""
entry_main(cwd)
load config file in cwd
    config-err
ast-parser
inserter
ast-parser
metadata write

entry_init(cwd)
writes a config file in cwd
"""
import sys
import dart_dataclasses.file_level.file_level as file_level
import dart_dataclasses.parsing.config_file as config
import dart_dataclasses.insertion.insertions as insert
import dart_dataclasses.writing.metadata as metadata


def entry_main(cwd):
    try:
        config.config_var_declarations(cwd)
    except config.ConfigParseError:
        print('ConfigParseError: Either the file was not found in the CWD or'
              ' the config file has some error in it. To generate'
              'a config file in the CWD use command: dart_dataclasses init')
        sys.exit(1)
    initial_file_classes = file_level.dir_procedure(config.parsing_path)
    insert.dir_level_insertions(initial_file_classes)
    file_classes_to_reflect = file_level.dir_procedure(config.parsing_path)
    metadata.write_metadata_file(file_classes_to_reflect)


def main():
    args = sys.argv[1:]
    cwd = args[0]
    entry_main(cwd)


if __name__ == '__main__':
    # main()
    entry_main(r'D:\StudioProjects\test_dataclasses')
