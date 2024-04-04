#!/usr/bin/python3

import subprocess as sp
from pathlib import Path
import sys

script_path = Path(__file__).resolve()
bin_dir = script_path.parent
main_dir = bin_dir.parent

def remove_if_exists(path):
    if path.exists():
        cmd = ['rm', '-rf', path]
        res = sp.call(cmd)
        if res != 0:
            print(f'Failed to remove {path}')
            return False
    return True

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: 1_make_template.py <template_name>')
        sys.exit(1)

    template_name = sys.argv[1]
    template_dir = main_dir / template_name
    if not template_dir.exists():
        print(f'Template {template_name} does not exist')
        sys.exit(1)
    remove_if_exists(template_dir)
