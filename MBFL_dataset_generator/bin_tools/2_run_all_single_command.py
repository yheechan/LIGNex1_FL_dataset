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



def start_program(bash_filename, experiment_name, target_command, args):
    machinecore2bug_dict = get_machinecore2bug_dict()


    bash_file = bin_dir / bash_filename
    bash_file_fp = open(bash_file, 'w')
    bash_file_fp.write('date\n')

    concatenated_args = ' '.join(args)


    # send bin_on_machine_dir to machine
    limit_cnt = 0
    for machine in machinecore2bug_dict:
        for core in machinecore2bug_dict[machine]:
            bash_file_fp.write(f"ssh {machine} \"cd {experiment_name}/bin_on_machine && ./{target_command} {core} {concatenated_args} > {target_command}.output.{core}.0 2>&1\" &\n")

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
    experiment_name = sys.argv[1]
    target_command = sys.argv[2]
    args = sys.argv[3:]

    start_program('2_run_all_single_command.sh', experiment_name, target_command, args)