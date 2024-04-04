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



def start_program(bash_filename, experiment_name):
    machinecore2bug_dict = get_machinecore2bug_dict()

    bin_on_machine_dir = main_dir / 'bin_on_machine'
    assert bin_on_machine_dir.exists(), f"{bin_on_machine_dir} does not exist"

    bash_file = bin_dir / bash_filename
    bash_file_fp = open(bash_file, 'w')
    bash_file_fp.write('date\n')


    # send bin_on_machine_dir to machine
    limit_cnt = 0
    for machine in machinecore2bug_dict:
        bash_file_fp.write(f"scp -r {bin_on_machine_dir} {machine}:/home/yangheechan/{experiment_name} &\n")

        limit_cnt += 1
        if limit_cnt % 5 == 0:
            bash_file_fp.write("sleep 1s\n")
            bash_file_fp.write("wait\n")
    
    
    bash_file_fp.write("echo ssh done, waiting...\n")
    bash_file_fp.write("date\n")
    bash_file_fp.write("wait\n")
    bash_file_fp.write("date\n")

    sp.run(['chmod', '+x', bash_file])



if __name__ == "__main__":
    experiment_name = sys.argv[1]

    start_program('9_send_bin.sh', experiment_name)