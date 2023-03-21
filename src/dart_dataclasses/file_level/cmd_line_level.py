import subprocess
from pathlib import Path

def format_file(path: Path):
    """
    Formats dart files through dart format path
    """
    subprocess.run(f'dart format {path}', shell=True)


