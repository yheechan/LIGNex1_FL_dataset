#!/usr/bin/python3

import sys
from pathlib import Path
import subprocess as sp
import argparse
import csv

script_path = Path(__file__).resolve()
bin_dir = script_path.parent
root_dir = bin_dir.parent

def return_parser():
    parser = argparse.ArgumentParser(description='Combine FL scores')
    parser.add_argument(
        "-sbfl", "--sbfl",
        help="Directory name to target SBFL dataset",
        required=True,
        default=None
    )
    parser.add_argument(
        "-mbfl", "--mbfl",
        help="Directory name to target MBFL dataset",
        required=True,
        default=None
    )
    parser.add_argument(
        "-fl", "--fl",
        help="Directory name to target FL dataset",
        required=True,
        default=None
    )
    return parser

def custome_sort(feature_file):
    bug_name = feature_file.name.split('.')[0]
    return int(bug_name[3:])

def get_bug_versions(path):
    buggy_code_file_dir = path / 'FL_features_per_bug_version'
    assert buggy_code_file_dir.exists(), f"Error: {buggy_code_file_dir} does not exist"

    bug_versions = sorted(buggy_code_file_dir.iterdir(), key=custome_sort)
    bug_versions = [bug_version.name.split('.')[0] for bug_version in bug_versions]

    return bug_versions

def init_dir(start_pos, target_dir):
    target_path = start_pos / target_dir
    if not target_path.exists():
        target_path.mkdir()
    else:
        sp.run(f'rm -rf {target_path}', shell=True)
        target_path.mkdir()
    return target_path

def initialize_directories_ALL(fl_dir):
    directories = [
        'buggy_code_file_per_bug_version',                  # 0
        'buggy_line_key_per_bug_version',                   # 1
        'test_case_info_per_bug_version',                   # 2
        'postprocessed_coverage_per_bug_version'            # 3
    ]

    directories_path = []
    for directory in directories:
        made_dir = init_dir(fl_dir, directory)
        directories_path.append(made_dir)

    return directories_path

def get_target_code_file(buggy_code_dir):
    target_code_files = list(buggy_code_dir.iterdir())
    assert len(target_code_files) == 1, f"More than 1 file in {buggy_code_dir}"
    assert target_code_files[0].exists(), f"{target_code_files[0]} does not exist"
    return target_code_files[0]

# 0
def copy_buggy_code_file(bug_id, target_dir, sbfl_path, mbfl_path):

    # 1. retrieve the target code file from sbfl and mbfl
    sbfl_code_dir = sbfl_path / 'buggy_code_file_per_bug_version' / bug_id
    sbfl_code_file = get_target_code_file(sbfl_code_dir)
    sbfl_code_filename = sbfl_code_file.name

    mbfl_code_dir = mbfl_path / 'buggy_code_file_per_bug_version' / bug_id
    mbfl_code_file = get_target_code_file(mbfl_code_dir)
    mbfl_code_filename = mbfl_code_file.name

    # VALIDATE that the files are the same
    assert sbfl_code_filename == mbfl_code_filename, f"Error: {sbfl_code_filename} != {mbfl_code_filename}"
    sp.call(f"diff {sbfl_code_file} {mbfl_code_file}", shell=True)



    # 2. initiate directory for buggy code file
    bug_dir = target_dir / bug_id
    assert not bug_dir.exists(), f"{bug_dir} already exists"
    bug_dir.mkdir(exist_ok=True)


    # 3. copy the target code file to the bug_dir
    sp.run(f'cp {sbfl_code_file} {bug_dir}', shell=True)
    buggy_code_file = bug_dir / sbfl_code_filename
    assert buggy_code_file.exists(), f"{buggy_code_file} does not exist"


# 1
def copy_buggy_line_key(bug_id, target_dir, sbfl_path, mbfl_path):

    # 1. retrieve the buggy line key file from sbfl and mbfl
    sbfl_buggy_line_key_txt = sbfl_path / 'buggy_line_key_per_bug_version' / f'{bug_id}.buggy_line_key.txt'
    assert sbfl_buggy_line_key_txt.exists(), f"{sbfl_buggy_line_key_txt} does not exist"

    mbfl_buggy_line_key_txt = mbfl_path / 'buggy_line_key_per_bug_version' / f'{bug_id}.buggy_line_key.txt'
    assert mbfl_buggy_line_key_txt.exists(), f"{mbfl_buggy_line_key_txt} does not exist"

    # VALIDATE that the files are the same
    sp.call(f"diff {sbfl_buggy_line_key_txt} {mbfl_buggy_line_key_txt}", shell=True)

    # 2. copy the buggy line key file to the target directory
    target_filename = f'{bug_id}.buggy_line_key.txt'
    target_file = target_dir / target_filename
    sp.run(f'cp {sbfl_buggy_line_key_txt} {target_file}', shell=True)
    assert target_file.exists(), f"{target_file} does not exist"


# 2
def copy_test_case_info(bug_id, target_dir, sbfl_path, mbfl_path):
    tc_types = [ 'cc_testcases.csv', 'failing_testcases.csv', 'passing_testcases.csv' ]

    # 1. retrieve the test case info directory from sbfl and mbfl
    sbfl_test_case_info_dir = sbfl_path / 'test_case_info_per_bug_version' / bug_id
    assert sbfl_test_case_info_dir.exists(), f"{sbfl_test_case_info_dir} does not exist"

    mbfl_test_case_info_dir = mbfl_path / 'test_case_info_per_bug_version' / bug_id
    assert mbfl_test_case_info_dir.exists(), f"{mbfl_test_case_info_dir} does not exist"


    # VALIDATE that the files are the same
    for tc_type in tc_types:
        sbfl_test_case_file = sbfl_test_case_info_dir / tc_type
        assert sbfl_test_case_file.exists(), f"{sbfl_test_case_file} does not exist"
        mbfl_test_case_file = mbfl_test_case_info_dir / tc_type
        assert mbfl_test_case_file.exists(), f"{mbfl_test_case_file} does not exist"

        sp.call(f"diff {sbfl_test_case_file} {mbfl_test_case_file}", shell=True)
    
    # 2. initiate directory for test case info
    bug_dir = target_dir / bug_id
    assert not bug_dir.exists(), f"{bug_dir} already exists"
    bug_dir.mkdir(exist_ok=True)

    # 3. copy the test case info files to the bug_dir
    sp.run(f'cp -r {sbfl_test_case_info_dir}/* {bug_dir}', shell=True)

    # VALIDATE that the files are copied
    for tc_type in tc_types:
        target_test_case_file = bug_dir / tc_type
        assert target_test_case_file.exists(), f"{target_test_case_file} does not exist"


# 3
def copy_postprocessed_cov(bug_id, target_dir, sbfl_path):
    # 1. retrieve the coverage data from sbfl
    sbfl_cov_csv = sbfl_path / 'postprocessed_coverage_per_bug_version' / f'{bug_id}.cov_data.csv'
    assert sbfl_cov_csv.exists(), f"{sbfl_cov_csv} does not exist"

    # 3. copy the coverage data to the bug_dir
    sp.run(f'cp {sbfl_cov_csv} {target_dir}', shell=True)
    cov_data_file = target_dir / f'{bug_id}.cov_data.csv'
    assert cov_data_file.exists(), f"{cov_data_file} does not exist"


def start_program(sbfl, mbfl, fl):
    # check if the directory exists
    sbfl_path = root_dir / 'sbfl_datasets' / sbfl
    mbfl_path = root_dir / 'mbfl_datasets' / mbfl
    fl_path = root_dir / 'fl_datasets' / fl

    assert sbfl_path.exists(), f"Error: {sbfl} does not exist"
    assert mbfl_path.exists(), f"Error: {mbfl} does not exist"
    assert fl_path.exists(), f"Error: {fl} does not exist"

    # get the bug versions
    bug_versions = get_bug_versions(fl_path)
    
    # mkdir for target meta data
    directories = initialize_directories_ALL(fl_path)

    cnt = 0
    for bug_id in bug_versions:
        cnt += 1
        print(f"{cnt}: processing {bug_id}")

        # 0: copy <bug_dir>/buggy_version_code/<target-file> to
        # <mbfl_gathered_dir>/buggy_code_file_per_bug_version/<target-file>
        copy_buggy_code_file(bug_id, directories[0], sbfl_path, mbfl_path)


        # 1: copy <bug_dir>/buggy_line_key.txt to
        # <mbfl_gathered_dir>/buggy_line_key_per_bug_version/<bug_id>.buggy_line_key.txt
        copy_buggy_line_key(bug_id, directories[1], sbfl_path, mbfl_path)


        # 2: copy files in <bug_dir>/testcase_info/ to
        # <mbfl_gathered_dir>/test_case_info_per_bug_version/<bug_id>/
        copy_test_case_info(bug_id, directories[2], sbfl_path, mbfl_path)


        # 3: copy <bug_dir>/postprocessed_coverage_data/cov_data.csv to
        # <mbfl_gathered_dir/postprocessed_coverage_per_bug_version/<target-file>
        copy_postprocessed_cov(bug_id, directories[3], sbfl_path)

        # break



# example command: python3 combine_FL.py -sbfl sbfl -mbfl mbfl -fl fl
# ./combine_FL.py -sbfl sbfl_dataset-240410-v1 -mbfl mbfl_dataset-240409-v2 -fl fl_dataset-240413-v1

if __name__ == "__main__":
    parser = return_parser()
    args = parser.parse_args()

    start_program(args.sbfl, args.mbfl, args.fl)