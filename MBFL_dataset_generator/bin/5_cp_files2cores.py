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



def start_program(bash_filename, experiment_name, jsoncpp_template_path):
    machinecore2bug_dict = get_machinecore2bug_dict()
    template_path = jsoncpp_template_path

    original_version_code_dir = root_dir / 'original_code_files_on_jsoncpp/original_version'
    assert original_version_code_dir.exists(), f"{original_version_code_dir} does not exist"

    bash_file = bin_dir / bash_filename
    bash_file_fp = open(bash_file, 'w')
    bash_file_fp.write('date\n')

    # copy original_jsoncpp to each core
    limit_cnt = 0
    for machine in machinecore2bug_dict:
        for core in machinecore2bug_dict[machine]:
            bash_file_fp.write(f"ssh {machine} \"cp -r /home/yangheechan/{experiment_name}/{template_path.name} /home/yangheechan/{experiment_name}/{core}/jsoncpp_template\" &\n")

            limit_cnt += 1
            if limit_cnt % 5 == 0:
                bash_file_fp.write("sleep 1s\n")
                bash_file_fp.write("wait\n")
    
    
    # copy original version code file dir to each core
    for machine in machinecore2bug_dict:
        for core in machinecore2bug_dict[machine]:
            bash_file_fp.write(f"ssh {machine} \"cp -r /home/yangheechan/{experiment_name}/original_code_files/ /home/yangheechan/{experiment_name}/{core}/buggy_version_code_files\" &\n")

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
    jsoncpp_template_name = sys.argv[2]

    jsoncpp_template_path = root_dir / jsoncpp_template_name
    assert jsoncpp_template_path.exists(), f"{jsoncpp_template_path} does not exist"

    start_program('5_cp_files2cores.sh', experiment_name, jsoncpp_template_path)