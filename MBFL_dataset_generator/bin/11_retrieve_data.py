#!/usr/bin/python3

import subprocess as sp
from pathlib import Path
import sys

script_path = Path(__file__).resolve()
bin_dir = script_path.parent
main_dir = bin_dir.parent
root_dir = main_dir.parent



def get_machinecore2bug_dict():
    machinecore2bug_txt = main_dir / 'machinecore2bug.txt'
    assert machinecore2bug_txt.exists(), f"{machinecore2bug_txt} does not exist"

    machinecore2bug_dict = {}
    with open(machinecore2bug_txt, 'r') as f:
        lines = f.readlines()
    for line in lines:
        machine, core, bug_id = line.strip().split('-')
        if machine not in machinecore2bug_dict:
            machinecore2bug_dict[machine] = {}
        machinecore2bug_dict[machine][core] = bug_id
    return machinecore2bug_dict

def get_bug2file_dict():
    bug2file_txt = main_dir / 'bug2file.txt'
    assert bug2file_txt.exists(), f"{bug2file_txt} does not exist"

    bug2file_dict = {}
    with open(bug2file_txt, 'r') as f:
        lines = f.readlines()
    for line in lines:
        bug_id, filename = line.strip().split('-')
        bug2file_dict[bug_id] = filename
    return bug2file_dict


def start_program(bash_filename, experiment_name, dataset_name):
    machinecore2bug_dict = get_machinecore2bug_dict()
    bug2file_dict = get_bug2file_dict()

    # assert that the directory for mbfl dataset from machines exists
    mbfl_b4_gather_dir = root_dir / 'mbfl_dataset_b4_gather'
    assert mbfl_b4_gather_dir.exists(), f"{mbfl_b4_gather_dir} does not exist"

    # make the target directory for mbfl dataset from machines
    new_dataset_dir = mbfl_b4_gather_dir / dataset_name
    if new_dataset_dir.exists():
        sp.run(['rm', '-rf', new_dataset_dir])
    if not new_dataset_dir.exists():
        new_dataset_dir.mkdir()
    
    # make directory for each bug version
    for machine in machinecore2bug_dict:
        for core in machinecore2bug_dict[machine]:
            bug_id = machinecore2bug_dict[machine][core]
            bug_dir = new_dataset_dir / bug_id
            if not bug_dir.exists():
                bug_dir.mkdir(parents=True)
            
            buggy_version_code_dir = bug_dir / 'buggy_version_code'
            assert buggy_version_code_dir.exists() == False, f"{buggy_version_code_dir} already exists"
            buggy_version_code_dir.mkdir()





    bash_file = bin_dir / bash_filename
    bash_file_fp = open(bash_file, 'w')
    bash_file_fp.write('date\n')


    # retrieve mbfl_data from each core of each machines
    limit_cnt = 0
    for machine in machinecore2bug_dict:
        for core in machinecore2bug_dict[machine]:
            bug_id = machinecore2bug_dict[machine][core]
            bug_dir = new_dataset_dir / bug_id
            assert bug_dir.exists(), f"{bug_dir} does not exist"

            bash_file_fp.write(f"scp -r {machine}:/home/yangheechan/{experiment_name}/{core}/mbfl_data {bug_dir} & \n")

            limit_cnt += 1
            if limit_cnt % 5 == 0:
                bash_file_fp.write("sleep 1s\n")
                # bash_file_fp.write("wait\n")
    
    # retrieve prerequisite_data/testcase_info/ from each core of each machines
    limit_cnt = 0
    for machine in machinecore2bug_dict:
        for core in machinecore2bug_dict[machine]:
            bug_id = machinecore2bug_dict[machine][core]
            bug_dir = new_dataset_dir / bug_id
            assert bug_dir.exists(), f"{bug_dir} does not exist"

            bash_file_fp.write(f"scp -r {machine}:/home/yangheechan/{experiment_name}/{core}/prerequisite_data/testcase_info {bug_dir} & \n")

            limit_cnt += 1
            if limit_cnt % 5 == 0:
                bash_file_fp.write("sleep 1s\n")
                # bash_file_fp.write("wait\n")


    # retrieve prerequisite_data/buggy_line_key.txt from each core of each machines
    limit_cnt = 0
    for machine in machinecore2bug_dict:
        for core in machinecore2bug_dict[machine]:
            bug_id = machinecore2bug_dict[machine][core]
            bug_dir = new_dataset_dir / bug_id
            assert bug_dir.exists(), f"{bug_dir} does not exist"

            bash_file_fp.write(f"scp -r {machine}:/home/yangheechan/{experiment_name}/{core}/prerequisite_data/buggy_line_key.txt {bug_dir} & \n")

            limit_cnt += 1
            if limit_cnt % 5 == 0:
                bash_file_fp.write("sleep 1s\n")
                # bash_file_fp.write("wait\n")
    
    # retrieve prerequisite_data/coverage_data/lines_executed_by_failing_TC.txt from each core of each machines
    limit_cnt = 0
    for machine in machinecore2bug_dict:
        for core in machinecore2bug_dict[machine]:
            bug_id = machinecore2bug_dict[machine][core]
            bug_dir = new_dataset_dir / bug_id
            assert bug_dir.exists(), f"{bug_dir} does not exist"

            bash_file_fp.write(f"scp -r {machine}:/home/yangheechan/{experiment_name}/{core}/prerequisite_data/coverage_data/lines_executed_by_failing_TC.txt {bug_dir} & \n")

            limit_cnt += 1
            if limit_cnt % 5 == 0:
                bash_file_fp.write("sleep 1s\n")
                # bash_file_fp.write("wait\n")
    
    # retrieve prerequisite_data/version_summary.csv from each core of each machines
    limit_cnt = 0
    for machine in machinecore2bug_dict:
        for core in machinecore2bug_dict[machine]:
            bug_id = machinecore2bug_dict[machine][core]
            bug_dir = new_dataset_dir / bug_id
            assert bug_dir.exists(), f"{bug_dir} does not exist"

            bash_file_fp.write(f"scp -r {machine}:/home/yangheechan/{experiment_name}/{core}/prerequisite_data/version_summary.csv {bug_dir} & \n")

            limit_cnt += 1
            if limit_cnt % 5 == 0:
                bash_file_fp.write("sleep 1s\n")
                # bash_file_fp.write("wait\n")
    
    # retrieve /buggy_version_code_files/{filename} from each core of each machines
    limit_cnt = 0
    for machine in machinecore2bug_dict:
        for core in machinecore2bug_dict[machine]:
            bug_id = machinecore2bug_dict[machine][core]
            bug_dir = new_dataset_dir / bug_id
            assert bug_dir.exists(), f"{bug_dir} does not exist"

            filename = bug2file_dict[bug_id]

            bash_file_fp.write(f"scp -r {machine}:/home/yangheechan/{experiment_name}/{core}/buggy_version_code_files/{filename} {bug_dir}/buggy_version_code/ & \n")

            limit_cnt += 1
            if limit_cnt % 5 == 0:
                bash_file_fp.write("sleep 1s\n")
                # bash_file_fp.write("wait\n")
    
    
    bash_file_fp.write("echo ssh done, waiting...\n")
    bash_file_fp.write("date\n")
    bash_file_fp.write("wait\n")
    bash_file_fp.write("date\n")

    sp.run(['chmod', '+x', bash_file])



if __name__ == "__main__":
    experiment_name = sys.argv[1]   # mbfl_12mts_181bugs-240405-t1
    dataset_name = sys.argv[2]      # mbfl_dataset-240405-v1

    start_program('11_retrieve_data.sh', experiment_name, dataset_name)