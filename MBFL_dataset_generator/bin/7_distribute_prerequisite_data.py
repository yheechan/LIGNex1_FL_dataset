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

def get_target_file(target_prereq_dir, bug_id):
    buggy_version_dir = target_prereq_dir / bug_id / 'prerequisite_data/buggy_code_file'

    target_file = None
    file_cnt = 0
    for file in buggy_version_dir.iterdir():
        file_cnt += 1
        if file.is_file():
            target_file = file
            assert target_file.name in ['json_reader.cpp', 'json_value.cpp']
            return target_file
    assert file_cnt == 1, f"file_cnt: {file_cnt}"
    assert target_file is not None
    exit(1)

def send_targets_prerequisites(
        machinecore2bug_dict,
        target_prereq_dir,
        experiment_name,
        bash_file_fp,
        send_target
):
    limit_cnt = 0
    for machine in machinecore2bug_dict:
        for core in machinecore2bug_dict[machine]:
            bug_id = machinecore2bug_dict[machine][core]

            target = target_prereq_dir / bug_id / 'prerequisite_data' / send_target
            assert target.exists(), f"{target} does not exist"

            bash_file_fp.write(f"scp -r {target} {machine}:/home/yangheechan/{experiment_name}/{core}/prerequisite_data/{send_target} &\n")

            limit_cnt += 1
            if limit_cnt % 5 == 0:
                bash_file_fp.write("sleep 1s\n")
                bash_file_fp.write("wait\n")

def start_program(bash_filename, target_prereq_dir, experiment_name):
    machinecore2bug_dict = get_machinecore2bug_dict()

    bash_file = bin_dir / bash_filename
    bash_file_fp = open(bash_file, 'w')
    bash_file_fp.write('date\n')


    send_targets_prerequisites(
        machinecore2bug_dict,
        target_prereq_dir,
        experiment_name,
        bash_file_fp,
        'coverage_data/lines_executed_by_failing_TC.txt'
    )

    send_targets_prerequisites(
        machinecore2bug_dict,
        target_prereq_dir,
        experiment_name,
        bash_file_fp,
        'coverage_data/lines_executed_by_passing_TC.txt'
    )

    send_targets_prerequisites(
        machinecore2bug_dict,
        target_prereq_dir,
        experiment_name,
        bash_file_fp,
        'postprocessed_coverage_data'
    )

    send_targets_prerequisites(
        machinecore2bug_dict,
        target_prereq_dir,
        experiment_name,
        bash_file_fp,
        'testcase_info'
    )

    send_targets_prerequisites(
        machinecore2bug_dict,
        target_prereq_dir,
        experiment_name,
        bash_file_fp,
        'version_summary.csv'
    )

    send_targets_prerequisites(
        machinecore2bug_dict,
        target_prereq_dir,
        experiment_name,
        bash_file_fp,
        'bug_version.txt'
    )

    send_targets_prerequisites(
        machinecore2bug_dict,
        target_prereq_dir,
        experiment_name,
        bash_file_fp,
        'buggy_line_key.txt'
    )

    bash_file_fp.write("echo ssh done, waiting...\n")
    bash_file_fp.write("date\n")
    bash_file_fp.write("wait\n")
    bash_file_fp.write("date\n")

    sp.run(['chmod', '+x', bash_file])



if __name__ == "__main__":
    target_prereq_name = sys.argv[1]
    target_prereq_dir = root_dir / 'prerequisite_dataset' / target_prereq_name
    assert target_prereq_dir.exists(), f"{target_prereq_dir} does not exist"

    experiment_name = sys.argv[2]

    start_program('7_distribute_prerequisite_data.sh', target_prereq_dir, experiment_name)