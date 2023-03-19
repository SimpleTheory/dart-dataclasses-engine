from pathlib import Path
import sys
import dart_dataclasses.entry_points.entry_point_main
import dart_dataclasses.entry_points.entry_point_init

def help_msg():
    print('Welcome to dart_dataclasses where you can generate boiler-plate and reflective code at your command.'
          '\nSpeaking of commands there are three commands you should know:'
          '\n    dart_dataclasses init {optional path to preset config file}'
          '\n        - This command generates a dataclasses.config file in the CWD. By default it creates a new file,'
          '\n          however you can also copy a pre-existing dataclasses.config file if you wish.'          
          '\n    dart_dataclasses generate'
          '\n        - This command reads your dataclasses.config file and generates all the code desired as specified'
          '\n          by the decorators in your code.'
          '\n    dart_dataclasses help'
          '\n        - Type this command or dart_dataclasses by itself to see this message again.'
          )


possible_calls = {
    'init': dart_dataclasses.entry_points.entry_point_init.write_to_config,
    'generate': dart_dataclasses.entry_points.entry_point_main.entry_main,
    'help': help_msg
    }


def main():
    try:
        func_call = sys.argv[1]
        if func_call == 'help':
            raise IndexError
        call = possible_calls[func_call]
    except IndexError:
        help_msg()
        sys.exit(0)
    except KeyError:
        print(f'"{func_call}" is not a valid command for dart_dataclasses. Current valid commands are'
              f'\neither generate, init or help. (for example: dart_dataclasses help)')
        sys.exit(0)

    args = sys.argv[2:]
    cwd = Path.cwd()
    call(cwd, *args)

