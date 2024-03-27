#!/usr/bin/python3

import subprocess as sp
from pathlib import Path
import sys
import json

script_path = Path(__file__).resolve()
bin_dir = script_path.parent
main_dir = bin_dir.parent
root_dir = main_dir.parent

gcovr = Path('/home/yangheechan/.local/bin/gcovr')

def get_test_suite_from_file():
    output_dir = main_dir / 'output'
    assert output_dir.exists(), f'{output_dir} does not exist'
    ts_dir = output_dir / 'test_suite'
    assert ts_dir.exists(), f'{ts_dir} does not exist'
    ts_path = ts_dir / 'test_suite.csv'
    assert ts_path.exists(), f'{ts_path} does not exist'
    # +++++++++++++++++++++++++++++++++++++++++++++

    ts_dict = {}
    with ts_path.open() as f:
        lines = f.readlines()
        for line in lines[1:]:
            tc_id, tc_name = line.strip().split(',')
            assert tc_id not in ts_dict, f'{tc_id} already exists in test suite'
            ts_dict[tc_id] = tc_name
    
    assert len(ts_dict.keys()) == 127, f'Expected 127 test cases, got {len(ts_dict.keys())}'
    return ts_dict

def reset_gcda(jsoncpp_dir):
    project_path = jsoncpp_dir
    cmd = [
        'find', '.', '-type',
        'f', '-name', '*.gcda',
        '-delete'
    ]
    res = sp.call(cmd, cwd=project_path)
    if res != 0:
        print('Failed to remove gcda files')
        exit(1)

def gen_cov_json(jsoncpp_dir, tc_id):
    coverage_per_tc_dir = main_dir / 'output/coverage/coverage_per_tc'

    cov_file_name = tc_id + '.cov.json'
    cov_file_path = coverage_per_tc_dir / cov_file_name
    cmd = [
        gcovr,
        '--gcov-executable', 'llvm-cov gcov',
        '--json-pretty', '-o', cov_file_path
    ]
    res = sp.call(cmd, cwd=jsoncpp_dir)
    if res != 0:
        print(f'Failed to generate coverage json for {tc_id}')
        exit(1)
    return cov_file_path

def gen_cov_summary_json(jsoncpp_dir, tc_id):
    coverage_summary_dir = main_dir / 'output/coverage/coverage_summary_per_tc'
    
    cov_summary_file_name = tc_id + '.cov.summary.json'
    cov_summary_file_path = coverage_summary_dir / cov_summary_file_name
    cmd = [
        gcovr,
        '--gcov-executable', 'llvm-cov gcov',
        '--json-summary-pretty', '-o', cov_summary_file_path
    ]
    res = sp.call(cmd, cwd=jsoncpp_dir)
    if res != 0:
        print(f'Failed to generate coverage summary json for {tc_id}')
        exit(1)

    return cov_summary_file_path


def run_test_suite(project_dir, ts_dict, gen_cov):
    output_dir = main_dir / 'output'
    assert output_dir.exists(), f'{output_dir} does not exist'
    coverage_dir = output_dir / 'coverage'
    if not coverage_dir.exists():
        coverage_dir.mkdir()
    coverage_per_tc_dir = coverage_dir / 'coverage_per_tc'
    if not coverage_per_tc_dir.exists():
        coverage_per_tc_dir.mkdir()
    coverage_summary_dir = coverage_dir / 'coverage_summary_per_tc'
    if not coverage_summary_dir.exists():
        coverage_summary_dir.mkdir()
    # +++++++++++++++++++++++++++++++++++++++++++++

    jsoncpp_test = project_dir / 'build/src/test_lib_json/jsoncpp_test'
    assert jsoncpp_test.exists(), f'{jsoncpp_test} does not exist'

    failing_tc = {}
    passing_tc = {}

    # run each test case one by one
    for tc_id, tc_name in ts_dict.items():
        print('Running test case: {} {}'.format(tc_id, tc_name))

        # reset gcda files before every TC runs
        reset_gcda(project_dir)

        cmd = ['timeout', '2s', jsoncpp_test, '--test', tc_name]
        res = sp.call(cmd, stdout=sp.PIPE, stderr=sp.STDOUT, encoding='utf-8')
        if res != 0:
            failing_tc[tc_id] = tc_name
            print('test failed: {} {}'.format(tc_id, tc_name))
        else:
            passing_tc[tc_id] = tc_name
            print('test passed: {} {}'.format(tc_id, tc_name))
        
        # measure coverage using gcovr
        if gen_cov:
            # generate coverage json for each TC
            cov_file_path = gen_cov_json(project_dir, tc_id)
            # generate coverage summary json for each TC
            cov_summary_file_path = gen_cov_summary_json(project_dir, tc_id)


        # reset gcda files after all TC runs
        reset_gcda(project_dir)
    
    return failing_tc, passing_tc
    

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: 5_run_test_suite.py <template_name> <gen_cov>')
        sys.exit(1)

    template_name = sys.argv[1]
    project_dir = root_dir / template_name
    assert project_dir.exists(), f'{project_dir} does not exist'
    build_dir = project_dir / 'build'

    gen_cov = True if sys.argv[2] == 'gen_cov' else False

    ts_dict = get_test_suite_from_file()
    assert len(ts_dict.keys()) == 127, f'Expected 127 test cases, got {len(ts_dict.keys())}'

    failing_tc, passing_tc = run_test_suite(project_dir, ts_dict, gen_cov)
    tot_tc = len(failing_tc) + len(passing_tc)
    assert tot_tc == 127, f'Expected 127 test cases, got {tot_tc}'

