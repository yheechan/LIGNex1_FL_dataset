#!/usr/bin/python3

# VALIDATE 02: CHECK IF THE MUTANT CODE EXISTS IN ORIGIN BUG VERSION CODE

import sys
from pathlib import Path
import subprocess as sp

script_path = Path(__file__).resolve()
bin_dir = script_path.parent
root_dir = bin_dir.parent

def custom_sort(bug_dir):
    return int(bug_dir.name[3:])


def check_for_mutant(sbfl_dir, bug_id, target_code, line_num, after_mutation):
    code_file = sbfl_dir / 'buggy_code_file_per_bug_version' / bug_id / target_code
    assert code_file.exists(), f"{code_file} does not exist"

    file_fp = open(code_file, 'r')
    lines = file_fp.readlines()
    file_fp.close()


    mut_token = after_mutation.strip()
    bug_mut_token = lines[line_num-1].strip()

    a = mut_token not in bug_mut_token
    b = bug_mut_token not in mut_token

    if a and b:
        print(f"Invalid bug: {bug_id}")
        print(f"line_num: {line_num}")
        print(f"mut_token: {mut_token}")
        print(f"bug_mut_token: {bug_mut_token}")
        print("====================================")
        return 1

    return 0



def validate_02(sbfl_dir):
    mutantion_info_csv = sbfl_dir / "bug_version_mutation_info.csv"
    assert mutantion_info_csv.exists(), f"{mutantion_info_csv} does not exist"

    invalid_bugs = []

    with open(mutantion_info_csv, 'r') as f:
        lines = f.readlines()
        for line in lines[1:]:
            line = line.strip()
            info = line.split(',')
            
            if info[2] == '':
                print(f"excluding: {line}")
                continue

            bug_id = info[0]
            target_code = info[1]
            line_num = int(info[2])
            mut_op = info[3]
            before_mutation = info[4]
            after_mutation = info[5]

            result = check_for_mutant(sbfl_dir, bug_id, target_code, line_num, after_mutation)
            if result == 1:
                invalid_bugs.append(bug_id)
    


    if invalid_bugs:
        print("Invalid bugs:")
        for bug in invalid_bugs:
            print(bug)
    else:
        print("All bug are valid")

    



if __name__ == "__main__":
    sbfl_dataset_dir_name = sys.argv[1]
    sbfl_dir = root_dir / 'sbfl_datasets' / sbfl_dataset_dir_name
    assert sbfl_dir.exists(), f"sbfl dataset {sbfl_dir} does not exist"

    validate_02(sbfl_dir)