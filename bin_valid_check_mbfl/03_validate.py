#!/usr/bin/python3

# VALIDATE 03: VALIDATE THAT
# (1/((muse_a+1)*(muse_b+1))) * (muse_2) = muse_4
# (1/((muse_a+1)*(muse_c+1))) * (muse_3) = muse_5
# muse_4 - muse_5 = muse_6

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

        for row in reader:
            muse_a = float(row['muse_a'])
            muse_b = float(row['muse_b'])
            muse_c = float(row['muse_c'])

            muse_2 = float(row['muse_2'])
            muse_3 = float(row['muse_3'])
            muse_4 = float(row['muse_4'])
            muse_5 = float(row['muse_5'])
            muse_6 = float(row['muse_6'])

            check_muse_4 = ((1/((muse_a+1)*(muse_b+1))) * muse_2)
            check_muse_5 = ((1/((muse_a+1)*(muse_c+1))) * muse_3)
            check_muse_6 = muse_4 - muse_5

            assert check_muse_4 == muse_4, f"check_muse_4: {check_muse_4} != muse_4: {muse_4}"
            assert check_muse_5 == muse_5, f"check_muse_5: {check_muse_5} != muse_5: {muse_5}"
            assert check_muse_6 == muse_6, f"check_muse_6: {check_muse_6} != muse_6: {muse_6}"

def validate_03(mbfl_dir):
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

    validate_03(mbfl_dir)