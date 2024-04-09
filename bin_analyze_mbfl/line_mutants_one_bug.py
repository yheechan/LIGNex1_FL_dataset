#!/usr/bin/python3

import sys
from pathlib import Path

script_path = Path(__file__).resolve()
bin_dir = script_path.parent
root_dir = bin_dir.parent
mbfl_datasets_dir = root_dir / "mbfl_datasets"
assert mbfl_datasets_dir.exists(), f"{mbfl_datasets_dir} does not exist"


def get_line2mutant_dict(mutants_data_dir):
    mutants_db_csv = mutants_data_dir / 'selected_mutants/mutants_db.csv'
    assert mutants_db_csv.exists(), f"{mutants_db_csv} does not exist"

    line2mutant_dict = {}
    with open(mutants_db_csv, 'r') as f:
        lines = f.readlines()
        for line in lines[1:]:
            line = line.strip()
            info = line.split(',')

            target_file = info[0]
            if target_file not in line2mutant_dict:
                line2mutant_dict[target_file] = {}
            
            line_no = int(info[1])
            mutant_id = info[2]

            if line_no not in line2mutant_dict[target_file]:
                line2mutant_dict[target_file][line_no] = []
            line2mutant_dict[target_file][line_no].append(mutant_id)
    
    for target_file in line2mutant_dict:
        for line_no in line2mutant_dict[target_file]:
            assert len(line2mutant_dict[target_file][line_no]) <= 12, f"len: {len(line2mutant_dict[target_file][line_no])}"
    
    return line2mutant_dict

def get_tc_results(mutant_tc_results_csv):
    assert mutant_tc_results_csv.exists(), f"{mutant_tc_results_csv} does not exist"

    p2f = 0
    f2p = 0
    p2p = 0
    f2f = 0

    with open(mutant_tc_results_csv, 'r') as f:
        lines = f.readlines()

        cnt = 0
        for line in lines[1:]:
            line = line.strip()
            info = line.split(',')

            p2f = int(info[0])
            f2p = int(info[1])
            p2p = int(info[2])
            f2f = int(info[3])
            
            assert cnt == 0, f"cnt: {cnt}"
            cnt += 1
    
    return p2f, f2p, p2p, f2f

def check_build_success(mutant_dir):
    build_result_txt = mutant_dir / 'build_result.txt'
    assert build_result_txt.exists(), f"{build_result_txt} does not exist"

    with open(build_result_txt, 'r') as f:
        line = f.readline().strip()
        if line == 'build-failed':
            return False
        elif line == 'build-success':
            return True

def get_mutants_info(per_mutant_dir, line2mutant_dict, target_file, target_lineno):
    mutants_dict = {}

    # for each jsoncpp target file
    for file in line2mutant_dict:
        if file != target_file:
            continue

        # for each line_no in the target file
        for line_no in line2mutant_dict[file]:
            if line_no != target_lineno:
                continue

            # for each mutant_id in the line_no
            for mutant_id in line2mutant_dict[file][line_no]:
                # get mutant_dir
                mutant_dir = per_mutant_dir / mutant_id
                assert mutant_dir.exists(), f"{mutant_dir} does not exist"

                # check if it is build-success
                if not check_build_success(mutant_dir):
                    mutants_dict[mutant_id] = {
                        'build status': 'failed',
                        'p2f': 'N/A',
                        'f2p': 'N/A',
                        'p2p': 'N/A',
                        'f2f': 'N/A'
                    }
                    continue

                # get mutant_tc_results.csv
                mutant_tc_results_csv = mutant_dir / 'mutant_tc_results.csv'

                p2f, f2p, p2p, f2f = get_tc_results(mutant_tc_results_csv)

                mutants_dict[mutant_id] = {
                    'build status': 'success',
                    'p2f': p2f,
                    'f2p': f2p,
                    'p2p': p2p,
                    'f2f': f2f
                }

    return mutants_dict


def start_program(mbfl_dir, bug_version, target_file, target_lineno):
    # get mutants_data_dir of bug version
    mutants_data_dir = mbfl_dir / 'mutants_data_per_bug_version' / bug_version
    assert mutants_data_dir.exists(), f"{mutants_data_dir} does not exist"

    per_mutant_dir = mbfl_dir / 'mutants_data_per_bug_version' / bug_version / 'per_mutant_data'
    assert per_mutant_dir.exists(), f"{per_mutant_dir} does not exist"

    # get line2mutant dict
    line2mutant_dict = get_line2mutant_dict(mutants_data_dir)

    # get mutants info
    mutants_dict = get_mutants_info(per_mutant_dir, line2mutant_dict, target_file, target_lineno)

    # print mutants_dict
    cnt = 0
    tot_f2p = 0
    tot_p2f = 0
    tot_utilized_mutants = 0
    print(f"target_file: {target_file}, target_lineno: {target_lineno}")
    for mutant_id in mutants_dict:
        print(f"mutant_id: {mutant_id}")
        for key in mutants_dict[mutant_id]:
            print(f"\t{key}: {mutants_dict[mutant_id][key]}")

            if key == 'f2p' and mutants_dict[mutant_id][key] != 'N/A':
                tot_f2p += mutants_dict[mutant_id][key]
            if key == 'p2f' and mutants_dict[mutant_id][key] != 'N/A':
                tot_p2f += mutants_dict[mutant_id][key]
            if key == 'build status' and mutants_dict[mutant_id][key] == 'success':
                tot_utilized_mutants += 1
        cnt += 1
    print(f"total f2p: {tot_f2p}")
    print(f"total p2f: {tot_p2f}")
    print(f"total utilized mutants: {tot_utilized_mutants}")
    print(f"total mutants: {cnt}")
    







if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python3 line_mutants_one_bug.py <target_mbfl_dir_name> <target_bug_version> <target_file> <target_lineno>")
        print("ex) ./line_mutants_one_bug.py mbfl_dataset-240331 bug15 json_writer.cpp 925")

        sys.exit(1)
    
    target_mbfl_dir_name = sys.argv[1]
    target_bug_version = sys.argv[2]
    target_file = sys.argv[3]
    target_lineno = int(sys.argv[4])

    target_mbfl_dir = mbfl_datasets_dir / target_mbfl_dir_name
    assert target_mbfl_dir.exists(), f"{target_mbfl_dir} does not exist"

    start_program(target_mbfl_dir, target_bug_version, target_file, target_lineno)
