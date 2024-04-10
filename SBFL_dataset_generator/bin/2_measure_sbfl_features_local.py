#!/usr/bin/python3

from pathlib import Path
import sys
import csv
import math

script_path = Path(__file__).resolve()
bin_dir = script_path.parent
main_dir = bin_dir.parent
root_dir = main_dir.parent

def get_tc(prerequisite_dir):
    testcase_info_dir = prerequisite_dir / 'testcase_info'
    assert testcase_info_dir.exists(), f"{testcase_info_dir} does not exist"

    failing_csv = testcase_info_dir / 'failing_testcases.csv'
    assert failing_csv.exists(), f"{failing_csv} does not exist"
    passing_csv = testcase_info_dir / 'passing_testcases.csv'
    assert passing_csv.exists(), f"{passing_csv} does not exist"
    cc_csv = testcase_info_dir / 'cc_testcases.csv'
    assert cc_csv.exists(), f"{cc_csv} does not exist"

    failing_dict = {}
    with open(failing_csv, 'r') as f:
        lines = f.readlines()
        for line in lines[1:]:
            tc_id, tc_name = line.strip().split(',')
            assert tc_id not in failing_dict
            failing_dict[tc_id] = tc_name
    
    passing_dict = {}
    with open(passing_csv, 'r') as f:
        lines = f.readlines()
        for line in lines[1:]:
            tc_id, tc_name = line.strip().split(',')
            assert tc_id not in passing_dict
            passing_dict[tc_id] = tc_name
    
    cc_dict = {}
    with open(cc_csv, 'r') as f:
        lines = f.readlines()
        for line in lines[1:]:
            tc_id, tc_name = line.strip().split(',')
            assert tc_id not in cc_dict
            cc_dict[tc_id] = tc_name
    
    fail_cnt = len(failing_dict)
    pass_cnt = len(passing_dict)
    cc_cnt = len(cc_dict)

    assert fail_cnt + pass_cnt + cc_cnt == 127

    return failing_dict, passing_dict

def get_buggy_line_key(prerequisite_dir):
    buggy_line_key_txt = prerequisite_dir / 'buggy_line_key.txt'
    assert buggy_line_key_txt.exists(), f"{buggy_line_key_txt} does not exist"

    with open(buggy_line_key_txt, 'r') as f:
        buggy_line_key = f.readline().strip()
        return buggy_line_key

def validate_tc(total_tc, row_keys):
    tc_pack = []

    for key in row_keys:
        if key == 'key' or key == '': continue
        tc_pack.append(key)
    
    assert len(total_tc) == len(tc_pack)
    for tc_id in total_tc:
        assert tc_id in tc_pack
    for tc_id in tc_pack:
        assert tc_id in total_tc

def get_cov_info(prerequisite_dir, failing_tc, passing_tc, buggy_line_key):
    postprocessed_cov_data_dir = prerequisite_dir / 'postprocessed_coverage_data'
    assert postprocessed_cov_data_dir.exists(), f"{postprocessed_cov_data_dir} does not exist"

    cov_data_csv = postprocessed_cov_data_dir / 'cov_data.csv'
    assert cov_data_csv.exists(), f"{cov_data_csv} does not exist"

    total_tc_id = list(failing_tc.keys()) + list(passing_tc.keys())

    cov_per_line = []
    check_tc_col = True
    buggy_line_exists = False
    with open(cov_data_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            line_key = row['key']

            # [1] validate that the postprocessed coverage data has information for the buggy line
            if line_key == buggy_line_key:
                buggy_line_exists = True
            
            cov_per_line.append(row)

            # [2] validate that the postprocessed coverage data has all the test cases referred
            if check_tc_col:
                check_tc_col = False
                validate_tc(total_tc_id, row.keys())
    
    assert buggy_line_exists, f"{buggy_line_key} does not exist in {cov_data_csv}"
    
    return cov_per_line

def calculate_base_spectrum(line, tc_dict):
    executed = 0
    not_executed = 0

    for tc_id, tc_name in tc_dict.items():
        if line[tc_id] == '1':
            executed += 1
        else:
            not_executed += 1
    
    return executed, not_executed


def init_spectrum_dict(cov_per_line, failing_tc, passing_tc, buggy_line_key):
    spectrum_per_line = []

    buggy_line_cnt = 0
    for line in cov_per_line:
        line_key = line['key']

        bug_stat = 0
        if line_key == buggy_line_key:
            # [3] validate that the buggy line is only once in the postprocessed coverage data
            assert buggy_line_cnt == 0
            buggy_line_cnt += 1
            bug_stat = 1

        # calculate ef, nf for each line
        ef, nf = calculate_base_spectrum(line, failing_tc)
        ep, np = calculate_base_spectrum(line, passing_tc)

        # [4] validate that the sum of all ef, nf, ep, np is equal to the total number of test cases
        fail_cnt = len(failing_tc)
        pass_cnt = len(passing_tc)
        assert ef + nf + ep + np == fail_cnt + pass_cnt

        spectrum_per_line.append({
            'key': line_key,
            'ep': ep, 'ef': ef, 'np': np, 'nf': nf,
            'bug': bug_stat
        })
    
    return spectrum_per_line

def sbfl(e_p, e_f, n_p, n_f, formula="Ochiai"):
    if formula == "Jaccard":
        denominator = e_f + n_f + e_p
        if denominator == 0:
            return 0
        return e_f / denominator
    elif formula == "Binary":
        if 0 < n_f:
            return 0
        elif n_f == 0:
            return 1
    elif formula == "GP13":
        denominator = 2*e_p + e_f
        if denominator == 0:
            return 0
        return e_f + (e_f / denominator)
    elif formula == "Naish1":
        if 0 < n_f:
            return -1
        elif 0 == n_f:
            return n_p
    elif formula == "Naish2":
        x = e_p / (e_p + n_p + 1)
        return e_f - x
    elif formula == "Ochiai":
        denominator = math.sqrt((e_f + n_f) * (e_f + e_p))
        if denominator == 0:
            return 0
        return e_f / denominator
    elif formula == "Russel+Rao":
        return e_f/(e_p + n_p + e_f + n_f)
    elif formula == "Wong1":
        return e_f
    else:
        raise Exception(f"Unknown formula: {formula}")


def measure_total_sbfl(spectrum_per_line):
    SBFL_formulas = [
        'Binary', 'GP13', 'Jaccard', 'Naish1',
        'Naish2', 'Ochiai', 'Russel+Rao', 'Wong1'
    ]
    
    for line_info in spectrum_per_line:
        ep = line_info['ep']
        ef = line_info['ef']
        np = line_info['np']
        nf = line_info['nf']

        for formula in SBFL_formulas:
            sbfl_value = sbfl(ep, ef, np, nf, formula)
            line_info[formula] = sbfl_value
    
    return spectrum_per_line

def write_spectrum(sbfl_dir, bug_id, spectrum_per_line):
    all_dir = sbfl_dir / 'sbfl_features_per_bug-all'
    only_dir = sbfl_dir / 'sbfl_features_per_bug'

    filename = f"{bug_id}.sbfl_features.csv"
    all_file = all_dir / filename
    only_file = only_dir / filename

    with open(all_file, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'key', 'ep', 'ef', 'np', 'nf',
            'Binary', 'GP13', 'Jaccard', 'Naish1',
            'Naish2', 'Ochiai', 'Russel+Rao', 'Wong1',
            'bug'
        ])
        writer.writeheader()

        for line_info in spectrum_per_line:
            writer.writerow(line_info)
    
    with open(only_file, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'key', 'ep', 'ef', 'np', 'nf', 'bug'
        ])
        writer.writeheader()

        for line_info in spectrum_per_line:
            writer.writerow({
                'key': line_info['key'],
                'ep': line_info['ep'],
                'ef': line_info['ef'],
                'np': line_info['np'],
                'nf': line_info['nf'],
                'bug': line_info['bug']
            })

def custome_sort(bug_path):
    return int(bug_path.name[3:])

def gen_sbfl_for_bug(sbfl_dir, bug_dir):
    prerequisite_dir = bug_dir / 'prerequisite_data'
    assert prerequisite_dir.exists(), f"{prerequisite_dir} does not exist"

    # get test case info {tc_id: tc_name}
    failing_tc, passing_tc = get_tc(prerequisite_dir)

    # get buggy line key
    buggy_line_key = get_buggy_line_key(prerequisite_dir)

    # get coverage data as dict format {key, tc1, tc2, ...}
    cov_per_line = get_cov_info(prerequisite_dir, failing_tc, passing_tc, buggy_line_key)

    # initialize spectrum per line {key, ep, ef, np, nf}
    spectrum_per_line = init_spectrum_dict(cov_per_line, failing_tc, passing_tc, buggy_line_key)

    # calculate total sbfl for each line
    spectrum_per_line = measure_total_sbfl(spectrum_per_line)

    write_spectrum(sbfl_dir, bug_dir.name, spectrum_per_line)

    # for line_info in spectrum_per_line:
    #     line_key = line_info['key']
    #     if line_key == buggy_line_key:
    #         print(line_info)
    #         break
    
def start_program(prequisite_dir_name, sbfl_dir_name):
    prerequisite_dir = root_dir / 'prerequisite_dataset' / prequisite_dir_name
    assert prerequisite_dir.exists(), f"{prerequisite_dir} does not exist"

    sbfl_dir = root_dir / 'sbfl_datasets' / sbfl_dir_name
    assert not sbfl_dir.exists(), f"{sbfl_dir} already exists"
    sbfl_dir.mkdir()

    all_dir = sbfl_dir / 'sbfl_features_per_bug-all'
    assert not all_dir.exists(), f"{all_dir} already exists"
    all_dir.mkdir()

    only_dir = sbfl_dir / 'sbfl_features_per_bug'
    assert not only_dir.exists(), f"{only_dir} already exists"
    only_dir.mkdir()

    bug_dirs = sorted(prerequisite_dir.iterdir(), key=custome_sort)
    cnt = 0
    for bug_dir in bug_dirs:
        cnt += 1
        print(f"{cnt}: processing {bug_dir.name}")

        gen_sbfl_for_bug(sbfl_dir, bug_dir)

        # break

    








if __name__ == '__main__':
    prerequisite_dir_name = sys.argv[1]
    sbfl_dir_name = sys.argv[2]

    start_program(prerequisite_dir_name, sbfl_dir_name)
    