#!/usr/bin/python3

# VALIDATE 03: VALIDATE THAT MBFL FEATURE CSV FILE ONLY CONTAIN 1 BUGGY LINE

import sys
from pathlib import Path
import subprocess as sp
import csv

script_path = Path(__file__).resolve()
bin_dir = script_path.parent
root_dir = bin_dir.parent

def custom_sort(bug_dir):
    return int(bug_dir.name[3:])

def check_measurement(mbfl_feature_csv):

    with open(mbfl_feature_csv, 'r') as f:
        reader = csv.DictReader(f)

        buggy_line_cnt = 0
        for row in reader:
            bug_stat = int(row['bug'])
            if bug_stat == 1:
                buggy_line_cnt += 1
        
        assert buggy_line_cnt == 1, f"buggy line count: {buggy_line_cnt} != 1"
            

def validate_04(mbfl_dir):
    sorted_bug_dir = sorted(mbfl_dir.iterdir(), key=custom_sort)

    invalid_bug_dir = []

    for bug_dir in sorted_bug_dir:
        mbfl_data_dir = bug_dir / 'mbfl_data'
        assert mbfl_data_dir.exists(), f"{mbfl_data_dir} does not exist"

        mbfl_feature_csv = mbfl_data_dir / 'mbfl_features.csv'
        assert mbfl_feature_csv.exists(), f"{mbfl_feature_csv} does not exist"

        check_measurement(mbfl_feature_csv)
        
        bug_id = bug_dir.name
        print(f"{bug_id} is valid")

    



if __name__ == "__main__":
    mbfl_dataset_dir_name = sys.argv[1]
    mbfl_dir = root_dir / 'mbfl_dataset_b4_gather' / mbfl_dataset_dir_name
    assert mbfl_dir.exists(), f"mbfl dataset {mbfl_dir} does not exist"

    validate_04(mbfl_dir)