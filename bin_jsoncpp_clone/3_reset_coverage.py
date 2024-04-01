#!/usr/bin/python3

import subprocess as sp
from pathlib import Path
import sys

script_path = Path(__file__).resolve()
bin_dir = script_path.parent
main_dir = bin_dir.parent

clangPP = Path('/usr/bin/clang++-13')

def reset_gcda(jsoncpp_dir):
    project_path = jsoncpp_dir
    cmd = [
        'find', '.', '-type',
        'f', '-name', '*.gcda',
        '-delete'
    ]
    res = sp.call(cmd, cwd=project_path)
    

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: 2_reset_coverage.py <template_name>')
        sys.exit(1)

    template_name = sys.argv[1]
    project_dir = main_dir / template_name
    assert project_dir.exists(), f'{project_dir} does not exist'
    reset_gcda(project_dir)
