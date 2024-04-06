#!/usr/bin/python3

import sys
from pathlib import Path
import subprocess as sp
import json

script_path = Path(__file__).resolve()
bin_dir = script_path.parent
root_dir = bin_dir.parent

def custome_sort(bug_dir):
    return int(bug_dir.name[3:])

def make_target_gathered_directory(dir_name):
    mbfl_gathered_dir = root_dir / 'mbfl_datasets' / dir_name

    # remove if already exists (FOR NOW)
    if mbfl_gathered_dir.exists():
        print(f"{mbfl_gathered_dir} already exists")
        exit(1)
    
    assert not mbfl_gathered_dir.exists(), f"{mbfl_gathered_dir} already exists"
    mbfl_gathered_dir.mkdir()

    return mbfl_gathered_dir

def init_dir(start_pos, target_dir):
    target_path = start_pos / target_dir
    if not target_path.exists():
        target_path.mkdir()
    else:
        sp.run(f'rm -rf {target_path}', shell=True)
        target_path.mkdir()
    return target_path

def initialize_directories_ALL(mbfl_gathered_dir):
    directories = [
        'buggy_code_file_per_bug_version',                  # 0
        'buggy_line_key_per_bug_version',                   # 1
        'lines_executed_by_failing_TCs_per_bug_version',    # 2
        'mbfl_features_per_bug_version',                    # 3
        'mutants_data_per_bug_version',                     # 4
        'test_case_info_per_bug_version',                   # 5
        'total_p2f_f2p_per_bug_version',                    # 6
    ]

    directories_path = []
    for directory in directories:
        made_dir = init_dir(mbfl_gathered_dir, directory)
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
    buggy_code_dir = bug_dir / 'buggy_version_code'
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
    buggy_line_key_file = bug_dir / 'buggy_line_key.txt'
    assert buggy_line_key_file.exists(), f"{buggy_line_key_file} does not exist"

    # make target_dir/<bug_id> directory
    target_filename = f'{bug_id}.buggy_line_key.txt'
    target_file = target_dir / target_filename

    # copy buggy line key file to target_bug_dir
    sp.run(f'cp {buggy_line_key_file} {target_file}', shell=True)


# 2
def copy_lines_exec_by_failing_tc(bug_dir, target_dir):
    bug_id = bug_dir.name

    # get file of lines executed by failing TCs
    lines_exec_by_failing_tc_file = bug_dir / 'lines_executed_by_failing_TC.txt'
    assert lines_exec_by_failing_tc_file.exists(), f"{lines_exec_by_failing_tc_file} does not exist"

    # change to json file
    line_dict = {}
    with open(lines_exec_by_failing_tc_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            info = line.split('$$')
            line_key = info[0]
            tcs_id = info[1][1:].split(',')

            assert line_key not in line_dict, f"{line_key} already exists"
            line_dict[line_key] = tcs_id

    # get target file
    filename = f"{bug_id}.lines_executed_by_failing_TCs.json"
    target_file = target_dir / filename
    
    # write to target file
    with open(target_file, 'w') as f:
        json.dump(line_dict, f, indent=2)
    assert target_file.exists(), f"{target_file} does not exist"


# 3
def copy_mbfl_features(bug_dir, target_dir):
    bug_id = bug_dir.name

    # get mbfl features file
    mbfl_features_file = bug_dir / 'mbfl_data' / 'mbfl_features.csv'
    assert mbfl_features_file.exists(), f"{mbfl_features_file} does not exist"

    # make target_dir/<bug_id> directory
    target_filename = f'{bug_id}.mbfl_features.csv'
    target_file = target_dir / target_filename

    # copy mbfl features file to target_bug_dir
    sp.run(f'cp {mbfl_features_file} {target_file}', shell=True)


# 4
def copy_mutants_data(bug_dir, target_dir):
    bug_id = bug_dir.name

    # make target_dir/<bug_id> directory
    target_bug_dir = target_dir / bug_id
    assert not target_bug_dir.exists(), f"{target_bug_dir} already exists"
    target_bug_dir.mkdir()


    # get per_mutant_data directory
    mutants_data_dir = bug_dir / 'mbfl_data' / 'per_mutant_data'
    assert mutants_data_dir.exists(), f"{mutants_data_dir} does not exist"

    # copy directory to target_bug_dir
    sp.run(f'cp -r {mutants_data_dir} {target_bug_dir}', shell=True)

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # get selected_mutants directory
    selected_mutants_dir = bug_dir / 'mbfl_data' / 'selected_mutants'
    assert selected_mutants_dir.exists(), f"{selected_mutants_dir} does not exist"

    # copy directory to target_bug_dir
    sp.run(f'cp -r {selected_mutants_dir} {target_bug_dir}', shell=True)


# 5
def copy_test_case_info(bug_dir, target_dir):
    bug_id = bug_dir.name

    # make target_dir/<bug_id> directory
    target_bug_dir = target_dir / bug_id
    assert not target_bug_dir.exists(), f"{target_bug_dir} already exists"
    target_bug_dir.mkdir()

    # get test_case_info directory
    test_case_info_dir = bug_dir / 'testcase_info'
    assert test_case_info_dir.exists(), f"{test_case_info_dir} does not exist"

    # copy files in test_case_info directory to target_bug_dir
    sp.run(f'cp -r {test_case_info_dir}/* {target_bug_dir}', shell=True)


# 6
def copy_total_tc_results(bug_dir, target_dir):
    bug_id = bug_dir.name

    # get total_tc_results file
    total_tc_results_file = bug_dir / 'mbfl_data' / 'total_tc_results.csv'
    assert total_tc_results_file.exists(), f"{total_tc_results_file} does not exist"

    # make target_dir/<bug_id> directory
    target_filename = f'{bug_id}.total_tc_results.csv'
    target_file = target_dir / target_filename

    # copy total_tc_results file to target_bug_dir
    sp.run(f'cp {total_tc_results_file} {target_file}', shell=True)


# 7
def write_tc_summary(bug_dir, tc_summary_fp):
    bug_id = bug_dir.name

    # get version_summary file
    version_summary_file = bug_dir / 'version_summary.csv'
    assert version_summary_file.exists(), f"{version_summary_file} does not exist"

    # read total_tc_results file
    with open(version_summary_file, 'r') as f:
        lines = f.readlines()
        line_cnt = 0
        for line in lines[1:]:
            line = line.strip()

            info = line.split(',')
            fail_tc = info[0]
            pass_tc = info[1]
            cctc = info[2]
            total_tc = info[3]

            fail_lines = info[4]
            pass_lines = info[5]
            total_lines_exec = info[6]
            total_lines = info[7]
            total_coverage = info[8]

            line_cnt += 1
            tc_summary_fp.write(f"{bug_id},{fail_tc},{pass_tc},{cctc},{total_tc},{fail_lines},{pass_lines},{total_lines_exec},{total_lines},{total_coverage}\n")
        
    assert line_cnt == 1, f"More than 1 line in {version_summary_file}"


def start_program(mbfl_dataset_dir_name):
    mbfl_b4_dir = root_dir / 'mbfl_dataset_b4_gather' / mbfl_dataset_dir_name
    assert mbfl_b4_dir.exists(), f"mbfl dataset {mbfl_b4_dir} does not exist"

    # make gathered directory
    mbfl_gathered_dir = make_target_gathered_directory(mbfl_dataset_dir_name)

    # initialize directories
    directories = initialize_directories_ALL(mbfl_gathered_dir)

    tc_summary_csv = mbfl_gathered_dir / 'bug_version_TCs_summary.csv'
    tc_summary_fp = open(tc_summary_csv, 'w')
    tc_summary_fp.write("bug_id, # of failing TCs,# of passing TCs,# of CCTCs,total # of TCs,# of lines executed by failing TCs,# of lines executed by passing TCs,total # of lines executed,total # of lines,total coverage\n")

    # gather all files for each bug version
    bug_dirs = sorted(mbfl_b4_dir.iterdir(), key=custome_sort)
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


        # 2: copy <bug_dir>/lines_executed_by_failing_TC.txt to
        # <mbfl_gathered_dir>/lines_executed_by_failing_TCs_per_bug_version/<bug_id>.lines_executed_by_failing_TCs.json
        copy_lines_exec_by_failing_tc(bug_dir, directories[2])


        # 3: copy <bug_dir>/mbfl_data/mbfl_features.csv to
        # <mbfl_gathered_dir>/mbfl_features_per_bug_version/<bug_id>.mbfl_features.csv
        copy_mbfl_features(bug_dir, directories[3])


        # 4: copy <bug_dir>/mbfl_data/per_mutant_data/ to
        # <mbfl_gathered_dir>/mutants_data_per_bug_version/<bug_id>/
        copy_mutants_data(bug_dir, directories[4])


        # 5: copy files in <bug_dir>/testcase_info/ to
        # <mbfl_gathered_dir>/test_case_info_per_bug_version/<bug_id>/
        copy_test_case_info(bug_dir, directories[5])


        # 6: copy <bug_dir>/mbfl_data/total_tc_results.csv to
        # <mbfl_gathered_dir>/total_p2f_f2p_per_bug_version/<bug_id>.total_tc_results.csv
        copy_total_tc_results(bug_dir, directories[6])


        # 7: write to tc_summary.csv
        write_tc_summary(bug_dir, tc_summary_fp)


    print(f">> Successfully gathered all files from total of {cnt} bug versions")
    tc_summary_fp.close()


if __name__ == "__main__":
    mbfl_dataset_dir_name = sys.argv[1]
    start_program(mbfl_dataset_dir_name)
