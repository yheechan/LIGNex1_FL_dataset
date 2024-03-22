#!/usr/bin/python3

# THIS SCRIPT IS TO REMOVE UNWANTED ROWS FROM MEASURED (FINALIZED) SBFL DATASET
# TO IMPROVE ACC@5 SCORE

from pathlib import Path
import sys
import csv
import pandas as pd

script_path = Path(__file__).resolve()
bin_dir = script_path.parent
root_dir = bin_dir.parent

# Funciton to get the buggy line from spectrum csv
# (because buggy line information was not saved before when making SBFL data)
def get_buggy_line(spect_csv):
    assert spect_csv.exists(), f"{spect_csv} does not exist"
    with open(spect_csv, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            bug_stat = int(row[13])
            if bug_stat == 1:
                # (ex) bug1 # src/lib_json/json_writer.cpp $ valuetoString() # 95
                buggy_line_key = row[0]
                return buggy_line_key
    return None

def remove_and_rewrite_csv(spect_csv):
    unwanted = ['jsontestrunner', 'test_lib_json', 'CmakeFiles']
    checked = ['jsontestrunner', 'test_lib_json', 'json', 'lib_json', 'CMakeFiles']

    spect_df = pd.read_csv(spect_csv)

    for index, row in spect_df.iterrows():
        key = row['lineNo']
        curr_key_info = key.split('#')
        curr_version = curr_key_info[0].strip()
        curr_target_file = curr_key_info[1].strip()
        curr_function_name = curr_key_info[2].strip()
        curr_line_num = int(curr_key_info[3].strip())

        target_dir = curr_target_file.split('/')[1]
        assert target_dir in checked, f"target_dir {target_dir} not in {checked}"

        if target_dir in unwanted:
            spect_df.drop(index, inplace=True)
    
    spect_df.to_csv(spect_csv, index=False)
        

def remove_unwanted_rows(sbfl_dataset_dir):

    spectrum_dir = sbfl_dataset_dir / 'spectrum_feature_data_excluding_coincidentally_correct_tc_per_bug'
    assert spectrum_dir.exists(), f"{spectrum_dir} does not exist"

    cnt = 0
    for spect_csv in spectrum_dir.iterdir():
        buggy_line_key = get_buggy_line(spect_csv)
        key_info = buggy_line_key.split('#')
        bug_version = key_info[0].strip()
        bug_target_file = key_info[1].strip()
        bug_function_name = key_info[2].strip()
        bug_line_num = int(key_info[3].strip())

        cnt += 1
        print(f"{cnt}: {buggy_line_key}")

        remove_and_rewrite_csv(spect_csv)
        



if __name__ == "__main__":
    # this is the name of the target sbfl dataset (ex. overall_24_02_20-v2)
    sbfl_dataset_dir_name = sys.argv[1]
    sbfl_dataset_dir = root_dir / 'sbfl_datasets' / sbfl_dataset_dir_name
    assert sbfl_dataset_dir.exists(), f"sbfl dataset {sbfl_dataset_dir} does not exist"

    remove_unwanted_rows(sbfl_dataset_dir)