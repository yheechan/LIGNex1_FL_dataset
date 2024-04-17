#!/usr/bin/python3

from pathlib import Path
import sys
import csv

script_path = Path(__file__).resolve()
bin_dir = script_path.parent
root_dir = bin_dir.parent

# 01: VALIDATE THE EXISTENCE OF BUGGY LINE IN EACH SPECTRUM FEATURE CSV FILE
# and that there is only one buggy line in each spectrum feature csv file
def validate_01(sbfl_dataset):
    # spectrum_dir = sbfl_dataset / 'sbfl_features_per_bug'
    spectrum_dir = sbfl_dataset / 'sbfl_features_per_bug'
    assert spectrum_dir.exists(), f"{spectrum_dir} does not exist"

    for spect_csv in spectrum_dir.iterdir():
        buggy_line_found = False
        buggy_line_cnt = 0
        with open(spect_csv, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                bug_stat = int(row[13])
                if bug_stat == 1:
                    buggy_line_found = True
                    buggy_line_cnt += 1
        assert buggy_line_found, f"buggy line not found in {spect_csv}"
        assert buggy_line_cnt == 1, f"buggy line count: {buggy_line_cnt} != 1 in {spect_csv}"

if __name__ == "__main__":
    # this is the name of target sbfl dataset (ex. overall_24_02_20-v2)
    sbfl_dataset_dir_name = sys.argv[1]
    sbfl_dataset_dir = root_dir / 'sbfl_datasets' / sbfl_dataset_dir_name
    assert sbfl_dataset_dir.exists(), f"sbfl dataset {sbfl_dataset_dir} does not exist"

    validate_01(sbfl_dataset_dir)