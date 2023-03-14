import subprocess
from pathlib import Path

def format_file(path: Path):
    # TODO: check if works
    subprocess.run(f'dart format {path}', shell=True)

