from pathlib import Path
import sys
import dart_dataclasses.entry_points.entry_point_main
import dart_dataclasses.entry_points.entry_point_init

def help_msg():
    print('Welcome to dart_dataclasses. # TODO ADD TEXT')


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
        print(f'{func_call} is not a valid command for dart_dataclasses. Try either generate or init.')
        sys.exit(0)

    args = sys.argv[2:]
    cwd = Path.cwd()
    call(cwd, *args)

