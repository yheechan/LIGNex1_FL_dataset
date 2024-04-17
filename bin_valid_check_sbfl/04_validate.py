#!/usr/bin/python3

# VALIDATE 04: CHECK THAT SPECTRUM VALUES ADD UP TO THE SUM OF FAILING AND PASSING TEST CASES

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


def check_spectrum_counts(sbfl_dir, bug_id, fail_cnt, pass_cnt):
    filename = f"{bug_id}.sbfl_features.csv"
    spect_csv = sbfl_dir / 'sbfl_features_per_bug' / filename
    assert spect_csv.exists(), f"{spect_csv} does not exist"

    with open(spect_csv, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            ep = int(row['ep'])
            ef = int(row['ef'])
            np = int(row['np'])
            nf = int(row['nf'])

            assert ef+nf == fail_cnt, f"sum of failing test cases does not match with ef+nf in {spect_csv}"
            assert ep+np == pass_cnt, f"sum of passing test cases does not match with ep+np in {spect_csv}"
            assert ep+ef+np+nf == fail_cnt+pass_cnt, f"sum of spectrum values does not match with total test cases in {spect_csv}"



def validate_04(sbfl_dir):

    bug_versions = get_bug_versions(sbfl_dir)
    
    cnt = 0
    for bug_id in bug_versions:
        cnt += 1
        print(f"{cnt}: Validating {bug_id}")

        # get test cases
        failing_tcs = get_tcs(sbfl_dir, bug_id, 'failing')
        passing_tcs = get_tcs(sbfl_dir, bug_id, 'passing')
        cc_tcs = get_tcs(sbfl_dir, bug_id, 'cc')

        fail_cnt = len(failing_tcs)
        pass_cnt = len(passing_tcs)
        cc_cnt = len(cc_tcs)
        assert fail_cnt+pass_cnt+cc_cnt == 127, f"total test cases is not 127 in {bug_id}"

        check_spectrum_counts(sbfl_dir, bug_id, fail_cnt, pass_cnt)

    



if __name__ == "__main__":
    sbfl_dataset_dir_name = sys.argv[1]
    sbfl_dir = root_dir / 'sbfl_datasets' / sbfl_dataset_dir_name
    assert sbfl_dir.exists(), f"sbfl dataset {sbfl_dir} does not exist"

    validate_04(sbfl_dir)