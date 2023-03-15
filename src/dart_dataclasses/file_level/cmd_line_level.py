import subprocess
from pathlib import Path

def format_file(path: Path):
    subprocess.run(f'dart format {path}', shell=True)


