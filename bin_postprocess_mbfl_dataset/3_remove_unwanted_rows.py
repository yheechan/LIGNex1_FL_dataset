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

def custome_sort(feature_csv):
    filename = feature_csv.name
    bug_id = filename.split('.')[0]
    return int(bug_id[3:])


# Funciton to get the buggy line from feature csv
# (because buggy line information was not saved before when making SBFL data)
def get_buggy_line(feature_csv):
    assert feature_csv.exists(), f"{feature_csv} does not exist"
    with open(feature_csv, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            bug_stat = int(row[11])
            if bug_stat == 1:
                # (ex) src/lib_json/json_writer.cpp # valuetoString() # 95
                buggy_line_key = row[0]
                return buggy_line_key
    return None

def remove_and_rewrite_csv(feature_csv):
    unwanted = ['jsontestrunner', 'test_lib_json', 'CMakeFiles']
    checked = ['jsontestrunner', 'test_lib_json', 'json', 'lib_json', 'CMakeFiles']

    feature_df = pd.read_csv(feature_csv)

    for index, row in feature_df.iterrows():
        key = row['key']
        curr_key_info = key.split('#')
        # curr_version = curr_key_info[0].strip()
        curr_target_file = curr_key_info[0].strip()
        curr_function_name = curr_key_info[1].strip()
        curr_line_num = int(curr_key_info[2].strip())

        target_dir = curr_target_file.split('/')[1]
        assert target_dir in checked, f"target_dir {target_dir} not in {checked}"

        if target_dir in unwanted:
            feature_df.drop(index, inplace=True)
    
    feature_df.to_csv(feature_csv, index=False)
        

def remove_unwanted_rows(sbfl_dataset_dir):

    feature_dir = sbfl_dataset_dir / 'mbfl_features_per_bug_version'
    assert feature_dir.exists(), f"{feature_dir} does not exist"

    feature_dir = sorted(list(feature_dir.iterdir()), key=custome_sort)

    cnt = 0
    for feature_csv in feature_dir:
        filename = feature_csv.name
        bug_id = filename.split('.')[0]
        
        buggy_line_key = get_buggy_line(feature_csv)
        assert buggy_line_key is not None, f"buggy_line_key is None for {feature_csv}"

        key_info = buggy_line_key.split('#')

        # bug_version = key_info[0].strip()
        bug_target_file = key_info[0].strip()
        bug_function_name = key_info[1].strip()
        bug_line_num = int(key_info[2].strip())

        cnt += 1
        print(f"{cnt}: {bug_id}: {buggy_line_key}")

        remove_and_rewrite_csv(feature_csv)
        



if __name__ == "__main__":
    # this is the name of the target mbfl dataset (ex. overall_24_02_20-v2)
    mbfl_dataset_dir_name = sys.argv[1]
    mbfl_dataset_dir = root_dir / 'mbfl_datasets' / mbfl_dataset_dir_name
    assert mbfl_dataset_dir.exists(), f"mbfl dataset {mbfl_dataset_dir} does not exist"

    remove_unwanted_rows(mbfl_dataset_dir)
