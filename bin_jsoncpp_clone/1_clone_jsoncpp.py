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

def make_clone(template_name):
    template_dir = main_dir / template_name
    remove_if_exists(template_dir)

    cmd = [
        'git', 'clone',
        'https://github.com/open-source-parsers/jsoncpp.git',
        template_name
    ]

    reset_cmd = ['git', 'reset', '--hard', '83946a2']

    res = sp.call(cmd, cwd=main_dir)
    if res != 0:
        print('Failed to clone template')
        return
    

    res = sp.call(reset_cmd, cwd=template_dir)
    if res != 0:
        print('Failed to reset template')
        return

def change_files(template_name):
    project_path = main_dir / template_name
    og_dir = main_dir / 'original_code_files_on_jsoncpp'

    cp_dict = {
        'value_file' : [
            project_path / 'src/lib_json/json_value.cpp',
            og_dir / 'json_value.cpp'
        ],
        'reader_file' : [
            project_path / 'src/lib_json/json_reader.cpp',
            og_dir / 'json_reader.cpp'
        ],
        'test_main_file' : [
            project_path / 'src/test_lib_json/main.cpp',
            og_dir / 'main.cpp'
        ],
        'cmakeFile' : [
            project_path / 'CMakeLists.txt',
            og_dir / 'CMakeLists.txt'
        ],
    }

    for key in cp_dict:
        cp_cmd = ['cp', cp_dict[key][1], cp_dict[key][0]]
        res = sp.call(cp_cmd)
        if res != 0:
            print(f'Failed to copy {key}')
            exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: 1_make_template.py <template_name>')
        sys.exit(1)

    template_name = sys.argv[1]
    make_clone(template_name)
    change_files(template_name)