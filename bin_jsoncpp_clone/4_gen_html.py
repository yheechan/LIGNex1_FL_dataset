#!/usr/bin/python3

import subprocess as sp
from pathlib import Path
import sys

script_path = Path(__file__).resolve()
bin_dir = script_path.parent
main_dir = bin_dir.parent

clangPP = Path('/usr/bin/clang++-13')
gcovr = Path('/home/yangheechan/.local/bin/gcovr')

def gen_html(jsoncpp_dir):
    project_path = jsoncpp_dir
    html_dir = project_path / 'html'
    if html_dir.exists():
        cmd = ['rm', '-rf', html_dir]
        res = sp.call(cmd)
        if res != 0:
            print(f'Failed to remove {html_dir}')
            return
    # html_dir.mkdir()

    cmd = [
        gcovr,
        '--gcov-executable', 'llvm-cov gcov',
        '--html-details', '-o', 'html/'
    ]
    res = sp.call(cmd, cwd=project_path)
    

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: 4_gen_html.py <template_name>')
        sys.exit(1)

    template_name = sys.argv[1]
    project_dir = main_dir / template_name
    assert project_dir.exists(), f'{project_dir} does not exist'
    gen_html(project_dir)
