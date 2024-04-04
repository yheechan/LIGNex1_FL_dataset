#!/usr/bin/python3

import sys
from pathlib import Path

script_path = Path(__file__).resolve()
bin_dir = script_path.parent
main_dir = bin_dir.parent
root_dir = main_dir.parent

def custom_sort(dir):
    return int(dir.name[3:])

def get_available_machines():
    machine_txt = Path('/home/yangheechan/.hosts/mbfl_servers')
    assert machine_txt.exists(), f"{machine_txt} does not exist"

    with open(machine_txt, 'r') as f:
        machines = f.readlines()
    machines = [machine.strip() for machine in machines]
    return machines

def start_program(target_prereq_dir):

    machines = get_available_machines()
    print(f"Available machines: {len(machines)}")

    # sort by bug number
    target_prereq_dir_list = sorted(target_prereq_dir.iterdir(), key=custom_sort)

    # for each bug, assign to a machine
    # each core has 8 cores
    machinecore2bug_path = main_dir / 'machinecore2bug.txt'
    machinecore2bug_fp = open(machinecore2bug_path, 'w')

    machine_core = 8
    bug_idx = 0
    utilizied_machines = []
    stop = False
    for machine in machines:
        for core in range(machine_core):
            if bug_idx >= len(target_prereq_dir_list):
                stop = True
                break
            bug_id = target_prereq_dir_list[bug_idx].name
            map_str = f"{machine}-core{core}-{bug_id}"

            # record the mapping in machinecore2bug.txt
            machinecore2bug_fp.write(map_str + '\n')
            bug_idx += 1

            # overwrite the bug_version.txt with map_str
            buggy_version_txt = target_prereq_dir / bug_id / 'prerequisite_data/bug_version.txt'
            assert buggy_version_txt.exists(), f"{buggy_version_txt} does not exist"

            with open(buggy_version_txt, 'w') as f:
                f.write(map_str)
        utilizied_machines.append(machine)
        if stop: break

    machinecore2bug_fp.close()
    print(f"Utilized machines: {len(utilizied_machines)}")
            


if __name__ == "__main__":
    prereq_dir_name = sys.argv[1]
    target_prereq_dir = root_dir / 'prerequisite_dataset' / prereq_dir_name
    assert target_prereq_dir.exists(), f"{target_prereq_dir} does not exist"

    start_program(target_prereq_dir)