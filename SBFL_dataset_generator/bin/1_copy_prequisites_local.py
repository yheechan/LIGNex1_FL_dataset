#!/usr/bin/python3

from pathlib import Path
import sys
import csv
import math
import subprocess as sp

script_path = Path(__file__).resolve()
bin_dir = script_path.parent
main_dir = bin_dir.parent
root_dir = main_dir.parent


def custome_sort(bug_path):
    return int(bug_path.name[3:])

def init_dir(start_pos, target_dir):
    target_path = start_pos / target_dir
    if not target_path.exists():
        target_path.mkdir()
    else:
        sp.run(f'rm -rf {target_path}', shell=True)
        target_path.mkdir()
    return target_path

def initialize_directories_ALL(sbfl_dir):
    directories = [
        'buggy_code_file_per_bug_version',                  # 0
        'buggy_line_key_per_bug_version',                   # 1
        'test_case_info_per_bug_version',                   # 2
        'postprocessed_coverage_per_bug_version'            # 3
    ]

    directories_path = []
    for directory in directories:
        made_dir = init_dir(sbfl_dir, directory)
        directories_path.append(made_dir)

    return directories_path

def get_target_code_filename(buggy_code_dir):
    target_code_files = list(buggy_code_dir.iterdir())
    assert len(target_code_files) == 1, f"More than 1 file in {buggy_code_dir}"
    return target_code_files[0].name
    
# 0
def copy_buggy_code_file(bug_dir, target_dir):
    bug_id = bug_dir.name

    # get buggy code directory
    buggy_code_dir = bug_dir / 'prerequisite_data/buggy_code_file'
    assert buggy_code_dir.exists(), f"{buggy_code_dir} does not exist"

    # get target code file
    target_code_filename = get_target_code_filename(buggy_code_dir)
    target_code_file = buggy_code_dir / target_code_filename
    assert target_code_file.exists(), f"{target_code_file} does not exist"

    # make target_dir/<bug_id> directory
    target_bug_dir = target_dir / bug_id
    assert not target_bug_dir.exists(), f"{target_bug_dir} already exists"
    target_bug_dir.mkdir()

    # copy target code file to target_bug_dir
    sp.run(f'cp {target_code_file} {target_bug_dir}', shell=True)

# 1
def copy_buggy_line_key(bug_dir, target_dir):
    bug_id = bug_dir.name

    # get buggy line key file
    buggy_line_key_file = bug_dir / 'prerequisite_data/buggy_line_key.txt'
    assert buggy_line_key_file.exists(), f"{buggy_line_key_file} does not exist"

    # make target_dir/<bug_id> directory
    target_filename = f'{bug_id}.buggy_line_key.txt'
    target_file = target_dir / target_filename

    # copy buggy line key file to target_bug_dir
    sp.run(f'cp {buggy_line_key_file} {target_file}', shell=True)

# 2
def copy_test_case_info(bug_dir, target_dir):
    bug_id = bug_dir.name

    # make target_dir/<bug_id> directory
    target_bug_dir = target_dir / bug_id
    assert not target_bug_dir.exists(), f"{target_bug_dir} already exists"
    target_bug_dir.mkdir()

    # get test_case_info directory
    test_case_info_dir = bug_dir / 'prerequisite_data/testcase_info'
    assert test_case_info_dir.exists(), f"{test_case_info_dir} does not exist"

    # copy files in test_case_info directory to target_bug_dir
    sp.run(f'cp -r {test_case_info_dir}/* {target_bug_dir}', shell=True)

# 3
def copy_postprocessed_cov(bug_dir, target_dir):
    bug_id = bug_dir.name

    # get coverage dir
    cov_csv = bug_dir / 'prerequisite_data/postprocessed_coverage_data/cov_data.csv'
    assert cov_csv.exists(), f"{cov_csv} does not exist"

    target_filename = f"{bug_id}.cov_data.csv"
    target_file = target_dir / target_filename

    # copy cov csv file to targetfile
    sp.run(f"cp {cov_csv} {target_file}", shell=True)

def start_program(prequisite_dir_name, sbfl_dir_name):
    prerequisite_dir = root_dir / 'prerequisite_dataset' / prequisite_dir_name
    assert prerequisite_dir.exists(), f"{prerequisite_dir} does not exist"

    sbfl_dir = root_dir / 'sbfl_datasets' / sbfl_dir_name
    if not sbfl_dir.exists():
        sbfl_dir.mkdir()
    else:
        sp.run(f"rm -rf {sbfl_dir}", shell=True)
        

    directories = initialize_directories_ALL(sbfl_dir)

    bug_dirs = sorted(prerequisite_dir.iterdir(), key=custome_sort)
    cnt = 0
    for bug_dir in bug_dirs:
        cnt += 1
        print(f"{cnt}: Processing {bug_dir.name}")

        # 0: copy <bug_dir>/buggy_version_code/<target-file> to
        # <mbfl_gathered_dir>/buggy_code_file_per_bug_version/<target-file>
        copy_buggy_code_file(bug_dir, directories[0])

        # 1: copy <bug_dir>/buggy_line_key.txt to
        # <mbfl_gathered_dir>/buggy_line_key_per_bug_version/<bug_id>.buggy_line_key.txt
        copy_buggy_line_key(bug_dir, directories[1])

        # 2: copy files in <bug_dir>/testcase_info/ to
        # <mbfl_gathered_dir>/test_case_info_per_bug_version/<bug_id>/
        copy_test_case_info(bug_dir, directories[2])

        # 3: copy <bug_dir>/postprocessed_coverage_data/cov_data.csv to
        # <mbfl_gathered_dir/postprocessed_coverage_per_bug_version/<target-file>
        copy_postprocessed_cov(bug_dir, directories[3])


if __name__ == '__main__':
    prerequisite_dir_name = sys.argv[1]
    sbfl_dir_name = sys.argv[2]

    start_program(prerequisite_dir_name, sbfl_dir_name)
    