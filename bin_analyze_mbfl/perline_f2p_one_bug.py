#!/usr/bin/python3

import sys
from pathlib import Path

script_path = Path(__file__).resolve()
bin_dir = script_path.parent
root_dir = bin_dir.parent
mbfl_datasets_dir = root_dir / "mbfl_datasets"
assert mbfl_datasets_dir.exists(), f"{mbfl_datasets_dir} does not exist"


def get_line2mutant_dict(mutant_info_dir):
    mutants_db_csv = mutant_info_dir / 'selected_mutants/mutants_db.csv'
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

def get_perline_f2p_dict(per_mutant_dir, line2mutant_dict):
    perline_f2p_dict = {}

    # for each jsoncpp target file
    for target_file in line2mutant_dict:
        perline_f2p_dict[target_file] = {}
        
        # for each line_no in the target file
        for line_no in line2mutant_dict[target_file]:
            perline_f2p_dict[target_file][line_no] = {
                '# of mutants': len(line2mutant_dict[target_file][line_no]),
            }

            total_p2f = 0
            total_f2p = 0
            total_mutants_with_f2p = 0
            build_failed = 0

            # for each mutant_id in the line_no
            for mutant_id in line2mutant_dict[target_file][line_no]:

                # get mutant_dir
                mutant_dir = per_mutant_dir / mutant_id
                assert mutant_dir.exists(), f"{mutant_dir} does not exist"

                # check if it is build-success
                if not check_build_success(mutant_dir):
                    build_failed += 1
                    continue

                # get mutant_tc_results.csv
                mutant_tc_results_csv = mutant_dir / 'mutant_tc_results.csv'

                p2f, f2p, p2p, f2f = get_tc_results(mutant_tc_results_csv)
                total_p2f += p2f
                total_f2p += f2p
                if f2p > 0:
                    total_mutants_with_f2p += 1
                # break
            assert total_mutants_with_f2p <= len(line2mutant_dict[target_file][line_no]), f"total_mutants_with_f2p: {total_mutants_with_f2p}, len: {len(line2mutant_dict[target_file][line_no])}"

            # save to perline_f2p_dict
            perline_f2p_dict[target_file][line_no]['build_failed'] = build_failed
            perline_f2p_dict[target_file][line_no]['total_p2f'] = total_p2f
            perline_f2p_dict[target_file][line_no]['total_f2p'] = total_f2p
            perline_f2p_dict[target_file][line_no]['total_mutants_with_f2p'] = total_mutants_with_f2p

            # break
        # break
    return perline_f2p_dict

def save_perline_f2p_dict(perline_f2p_dict, bug_version):
    output_dir = bin_dir / 'output'
    if not output_dir.exists():
        output_dir.mkdir()
    
    csv_filename = f"{bug_version}.perline_f2p.csv"
    csv_path = output_dir / csv_filename

    with open(csv_path, 'w') as f:
        f.write("target_file,line_no,# of mutants,built_failed,total_p2f,total_f2p,total_mutants_with_f2p\n")
        for target_file in perline_f2p_dict:
            for line_no in perline_f2p_dict[target_file]:
                f.write(f"{target_file},{line_no},{perline_f2p_dict[target_file][line_no]['# of mutants']},{perline_f2p_dict[target_file][line_no]['build_failed']},{perline_f2p_dict[target_file][line_no]['total_p2f']},{perline_f2p_dict[target_file][line_no]['total_f2p']},{perline_f2p_dict[target_file][line_no]['total_mutants_with_f2p']}\n")
    
    print(f"Saved to {csv_path}")


def start_program(mbfl_dir, bug_version):
    # get mutant_info_dir of bug version
    mutant_info_dir = mbfl_dir / 'mutant_info_per_bug_version' / bug_version
    assert mutant_info_dir.exists(), f"{mutant_info_dir} does not exist"

    per_mutant_dir = mbfl_dir / 'mutant_info_per_bug_version' / bug_version / 'per_mutant_data'
    assert per_mutant_dir.exists(), f"{per_mutant_dir} does not exist"

    # get line2mutant dict
    line2mutant_dict = get_line2mutant_dict(mutant_info_dir)

    # get perline_f2p_dict
    perline_f2p_dict = get_perline_f2p_dict(per_mutant_dir, line2mutant_dict)
    
    # save perline_f2p_dict to file
    save_perline_f2p_dict(perline_f2p_dict, bug_version)
    







if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <target_mbfl_dir_name> <target_bug_version>")
        print("ex) ./perline_f2p.py mbfl_dataset-240331 bug1")
        sys.exit(1)
    target_mbfl_dir_name = sys.argv[1]
    target_bug_version = sys.argv[2]

    target_mbfl_dir = mbfl_datasets_dir / target_mbfl_dir_name
    assert target_mbfl_dir.exists(), f"{target_mbfl_dir} does not exist"

    start_program(target_mbfl_dir, target_bug_version)