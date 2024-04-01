#!/usr/bin/python3

import subprocess as sp
from pathlib import Path
import sys

script_path = Path(__file__).resolve()
bin_dir = script_path.parent
main_dir = bin_dir.parent

clangPP = Path('/usr/bin/clang++-13')

def remove_if_exists(path):
    if path.exists():
        cmd = ['rm', '-rf', path]
        res = sp.call(cmd)
        if res != 0:
            print(f'Failed to remove {path}')
            return False
    return True

def build_jsoncpp(project_dir):
    build_dir = project_dir / 'build'

    remove_if_exists(build_dir)
    build_dir.mkdir()

    cmd = [
        'cmake',
        '-DCMAKE_EXPORT_COMPILE_COMMANDS=ON',
        '-DCMAKE_CXX_COMPILER={}'.format(clangPP),
        # this command is for debugging and coverage + line2function
        # '-DCMAKE_CXX_FLAGS=-O0 -fprofile-arcs -ftest-coverage -g -fno-omit-frame-pointer -gline-tables-only -DFUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION --save-temps',
        '-DCMAKE_CXX_FLAGS=-O0 -fprofile-arcs -ftest-coverage -g -fno-omit-frame-pointer -gline-tables-only -DFUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION',
        '-DBUILD_SHARED_LIBS=OFF', '-G',
        'Unix Makefiles',
        '../'
    ]

    res = sp.call(cmd, cwd=build_dir)
    if res != 0:
        print('Failed to run cmake')
        return
    
    cmd = ['make', '-j20']
    res = sp.call(cmd, cwd=build_dir)
    if res != 0:
        print('Failed to run make')
        return
    

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: 2_build_jsoncpp.py <template_name>')
        sys.exit(1)

    template_name = sys.argv[1]
    project_dir = main_dir / template_name
    assert project_dir.exists(), f'{project_dir} does not exist'
    build_jsoncpp(project_dir)