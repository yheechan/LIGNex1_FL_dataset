#!/usr/bin/python3

# VALIDATE 01: CHECK IF ALL BUG DIRECTORIES HAVE MBFL_FEATURES.CSV (on mbfl_dataset_b4_gather)

import sys
from pathlib import Path
import subprocess as sp

script_path = Path(__file__).resolve()
bin_dir = script_path.parent
root_dir = bin_dir.parent

def custom_sort(bug_dir):
    return int(bug_dir.name[3:])

def validate_01(mbfl_dir):
    sorted_bug_dir = sorted(mbfl_dir.iterdir(), key=custom_sort)

    invalid_bug_dir = []

    for bug_dir in sorted_bug_dir:
        mbfl_data_dir = bug_dir / 'mbfl_data'
        assert mbfl_data_dir.exists(), f"{mbfl_data_dir} does not exist"

        mbfl_feature_csv = mbfl_data_dir / 'mbfl_features.csv'
        if not mbfl_feature_csv.exists():
            invalid_bug_dir.append(bug_dir)
            continue

        assert mbfl_feature_csv.exists(), f"{mbfl_feature_csv} does not exist"
    
    if invalid_bug_dir:
        print("Invalid bug directories:")
        for bug_dir in invalid_bug_dir:
            print(bug_dir)
    else:
        print("All bug directories are valid")

    



if __name__ == "__main__":
    mbfl_dataset_dir_name = sys.argv[1]
    mbfl_dir = root_dir / 'mbfl_dataset_b4_gather' / mbfl_dataset_dir_name
    assert mbfl_dir.exists(), f"mbfl dataset {mbfl_dir} does not exist"

    validate_01(mbfl_dir)