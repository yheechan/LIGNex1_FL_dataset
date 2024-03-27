#!/usr/bin/python3

import subprocess as sp
from pathlib import Path
import sys
import json

script_path = Path(__file__).resolve()
bin_dir = script_path.parent
main_dir = bin_dir.parent
root_dir = main_dir.parent

def get_test_suite(build_dir):
    jsoncpp_test = build_dir / 'src/test_lib_json/jsoncpp_test'
    assert jsoncpp_test.exists(), f'{jsoncpp_test} does not exist'

    cmd = [jsoncpp_test, '--list-tests']
    process = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.STDOUT, encoding='utf-8')

    tc_cnt = 1
    ts_dict = {}
    while True:
        line = process.stdout.readline()
        if line == '' and process.poll() is not None:
            break
        line = line.strip()
        if line == '':
            continue

        tc_id = 'TC{}'.format(tc_cnt)
        ts_dict[tc_id] = line
        tc_cnt += 1
    
    return ts_dict

def save_ts(ts_dict):
    output_dir = main_dir / 'output'
    assert output_dir.exists(), f'{output_dir} does not exist'
    ts_dir = output_dir / 'test_suite'
    if not ts_dir.exists():
        ts_dir.mkdir()
    
    ts_path = ts_dir / 'test_suite.csv'
    with ts_path.open('w') as f:
        f.write('Test Case,Test Name\n')
        for tc_id, tc_name in ts_dict.items():
            f.write(f'{tc_id},{tc_name}\n')
    
    print('>> Test suite saved to output/test_suite/test_suite.csv')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: 1_make_template.py <template_name>')
        sys.exit(1)

    template_name = sys.argv[1]
    project_dir = root_dir / template_name
    assert project_dir.exists(), f'{project_dir} does not exist'
    build_dir = project_dir / 'build'

    ts_dict = get_test_suite(build_dir)
    assert len(ts_dict.keys()) == 127, f'Expected 127 test cases, got {len(ts_dict.keys())}'

    save_ts(ts_dict)
