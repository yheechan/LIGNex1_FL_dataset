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

def make_target_b4_directory(dir_name):
    mbfl_gathered_dir = root_dir / 'mbfl_dataset_b4_gather' / dir_name

    # remove if already exists (FOR NOW)
    if mbfl_gathered_dir.exists():
        print(f"{mbfl_gathered_dir} already exists")
        exit(1)
    
    assert not mbfl_gathered_dir.exists(), f"{mbfl_gathered_dir} already exists"
    mbfl_gathered_dir.mkdir()

    return mbfl_gathered_dir


def get_versions2remove():
    versions2remove_txt = bin_dir / 'versions2remove.txt'
    assert versions2remove_txt.exists(), f"{versions2remove_txt} does not exist"

    versions2remove = []
    with open(versions2remove_txt, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            versions2remove.append(line)
    return versions2remove

def remove_versions_and_copy(past_dir, new_dir):
    versions2remove = get_versions2remove()
    
    past_bug_dirs = sorted(past_dir.iterdir(), key=custome_sort)
    bug_cnt = 0
    for past_bug_dir in past_bug_dirs:

        past_bug_id = past_bug_dir.name
        if past_bug_id in versions2remove:
            continue


        bug_cnt += 1
        new_bug_id = f"bug{bug_cnt}"
        
        print(f"{bug_cnt}: processing {past_bug_id} to {new_bug_id}")

        new_bug_dir = new_dir / new_bug_id
        new_bug_dir.mkdir()

        # copy all data in past_bug_dir to new_bug_dir
        sp.run(f'cp -r {past_bug_dir}/* {new_bug_dir}', shell=True)
    
    print(f">> total {bug_cnt} bugs are processed")
        

def change_mutations_info(past_mbfl_dir_name):
    mutation_info_csv = root_dir / 'mbfl_datasets' / past_mbfl_dir_name / 'bug_version_mutation_info.csv'
    assert mutation_info_csv.exists(), f"{mutation_info_csv} does not exist"

    versions2remove = get_versions2remove()

    new_mutatinos_info_csv = bin_dir / 'bug_version_mutation_info.csv'
    new_fp = open(new_mutatinos_info_csv, 'w')
    new_fp.write("bug_id,jsoncpp source code file,mutated line,mut_op,before mutation,after mutation\n")

    with open(mutation_info_csv, 'r') as f:
        lines = f.readlines()
        bug_cnt = 0

        for line in lines[1:]:
            line = line.strip()
            info = line.split(',')
            past_bug_id = info[0]

            if past_bug_id in versions2remove:
                continue

            bug_cnt += 1
            new_bug_id = f"bug{bug_cnt}"

            print(f"{bug_cnt}: processing {past_bug_id} to {new_bug_id}")

            new_fp.write(f"{new_bug_id},{info[1]},{info[2]},{info[3]},{info[4]},{info[5]}\n")

    new_fp.close()
    print(f">> total {bug_cnt} bugs are processed")
        


        
    




def start_program(past_mbfl_dir_name, new_mbfl_dir_name):
    past_dir = root_dir / 'mbfl_dataset_b4_gather' / past_mbfl_dir_name
    assert past_dir.exists(), f"mbfl dataset {past_dir} does not exist"

    new_dir = make_target_b4_directory(new_mbfl_dir_name)

    remove_versions_and_copy(past_dir, new_dir)
    change_mutations_info(past_mbfl_dir_name)





if __name__ == "__main__":
    past_mbfl_dir_name = sys.argv[1]
    new_mbfl_dir_name = sys.argv[2]

    start_program(past_mbfl_dir_name, new_mbfl_dir_name)
