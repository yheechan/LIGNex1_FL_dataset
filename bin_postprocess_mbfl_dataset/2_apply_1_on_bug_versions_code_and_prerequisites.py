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

def apply(past_data_name, new_data_name, dir_name, spec_name):
    past_filename = f"{spec_name}{past_data_name}"
    past_dir = root_dir / dir_name / past_filename
    assert past_dir.exists(), f"{past_dir} does not exist"

    new_filename = f"{spec_name}{new_data_name}"
    new_dir = root_dir / dir_name / new_filename
    assert not new_dir.exists(), f"{new_dir} already exists"
    new_dir.mkdir()

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
    
    return bug_cnt

def apply_prerequisites_dataset(past_data_name, new_data_name):
    past_dir = root_dir / 'prerequisites_dataset' / past_data_name



def remove_versions_and_copy(past_data_name, new_data_name):

    codes_cnt = apply(past_data_name, new_data_name, 'bug_versions_codes', 'bug_versions_')
    prerequisites_cnt = apply(past_data_name, new_data_name, 'prerequisite_dataset', 'prerequisite_dataset_')

    print(f">> {codes_cnt} codes are copied")
    print(f">> {prerequisites_cnt} prerequisites are copied")


        
    




def start_program(past_data_name, new_data_name):
    remove_versions_and_copy(past_data_name, new_data_name)







if __name__ == "__main__":
    past_data_name = sys.argv[1]
    new_data_name = sys.argv[2]

    start_program(past_data_name, new_data_name)
