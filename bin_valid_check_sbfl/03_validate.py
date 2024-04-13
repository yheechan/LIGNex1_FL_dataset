#!/usr/bin/python3

# VALIDATE 03: CHECK IF ALL THE FAILING TEST CASES EXECUTE THE BUGGY LINE

import sys
from pathlib import Path
import subprocess as sp
import csv

script_path = Path(__file__).resolve()
bin_dir = script_path.parent
root_dir = bin_dir.parent

def custom_sort(bug_file):
    bug_id = bug_file.name.split('.')[0]
    return int(bug_id[3:])


def get_bug_versions(sbfl_dir):
    sbfl_features_per_bug_dir = sbfl_dir / 'sbfl_features_per_bug'
    assert sbfl_features_per_bug_dir.exists(), f"{sbfl_features_per_bug_dir} does not exist"

    bug_versions = sorted(sbfl_features_per_bug_dir.iterdir(), key=custom_sort)
    bug_versions = [bug_version.name.split('.')[0] for bug_version in bug_versions
    ]
    return bug_versions


def get_buggy_line_key(sbfl_dir, bug_id):
    filename = f"{bug_id}.buggy_line_key.txt"
    buggy_line_key_txt = sbfl_dir / 'buggy_line_key_per_bug_version' / filename
    assert buggy_line_key_txt.exists(), f"{buggy_line_key_txt} does not exist"

    buggy_line_key = None
    with open(buggy_line_key_txt, 'r') as f:
        buggy_line_key = f.readline().strip()
    assert buggy_line_key is not None, f"buggy line key not found in {buggy_line_key_txt}"

    return buggy_line_key


def get_tcs(sbfl_dir, bug_id, tc_type):

    filename = f"{tc_type}_testcases.csv"
    tc_csv = sbfl_dir / 'test_case_info_per_bug_version' / bug_id / filename
    assert tc_csv.exists(), f"{tc_csv} does not exist"

    tcs = {}
    with open(tc_csv, 'r') as f:
        lines = f.readlines()
        for line in lines[1:]:
            line = line.strip()
            info = line.split(',')
            tc_id = info[0]
            tc_name = info[1]
            assert tc_id not in tcs, f"test case id {tc_id} already exists"
            tcs[tc_id] = tc_name
    
    return tcs

def check_failing_executions(sbfl_dir, bug_id, buggy_line_key, failing_tcs):
    filename = f"{bug_id}.cov_data.csv"
    cov_data_csv = sbfl_dir / 'postprocessed_coverage_per_bug_version' / filename
    assert cov_data_csv.exists(), f"{cov_data_csv} does not exist"

    with open(cov_data_csv, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            line_key = row['key']

            if line_key != buggy_line_key:
                continue

            for tc_id, tc_name in failing_tcs.items():
                tc_cov = row[tc_id]
                assert tc_cov == '1', f"test case {tc_name} does not execute the buggy line in {cov_data_csv}"
                print(f"\t{tc_name} executes the buggy line")


def validate_03(sbfl_dir):

    bug_versions = get_bug_versions(sbfl_dir)
    
    cnt = 0
    for bug_id in bug_versions:
        cnt += 1
        print(f"{cnt}: processing {bug_id}")
        
        # get buggy line key 
        buggy_line_key = get_buggy_line_key(sbfl_dir, bug_id)

        # get failing test cases
        failing_tcs = get_tcs(sbfl_dir, bug_id, 'failing')
        
        check_failing_executions(sbfl_dir, bug_id, buggy_line_key, failing_tcs)

    



if __name__ == "__main__":
    sbfl_dataset_dir_name = sys.argv[1]
    sbfl_dir = root_dir / 'sbfl_datasets' / sbfl_dataset_dir_name
    assert sbfl_dir.exists(), f"sbfl dataset {sbfl_dir} does not exist"

    validate_03(sbfl_dir)