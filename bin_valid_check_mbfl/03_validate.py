#!/usr/bin/python3

# VALIDATE 03: VALIDATE THAT WITH EXISTING FEATURES SUSP. SCORE OF METALLAXIS AND MUSE CAN BE MEASURED
# IT ALSO VALIDATES THAT THE FAILING TC COUNT IN THE FEATURE CSV FILE IS CORRECT TO THE DATASET
import sys
from pathlib import Path
import subprocess as sp
import csv
import math

script_path = Path(__file__).resolve()
bin_dir = script_path.parent
root_dir = bin_dir.parent

def custom_sort(bug_file):
    bug_id = bug_file.name.split('.')[0]
    return int(bug_id[3:])

def get_bug_versions(mbfl_dir):
    mbfl_features_per_bug_dir = mbfl_dir / 'mbfl_features_per_bug_version'
    assert mbfl_features_per_bug_dir.exists(), f"{mbfl_features_per_bug_dir} does not exist"

    bug_versions = sorted(mbfl_features_per_bug_dir.iterdir(), key=custom_sort)
    bug_versions = [bug_version.name.split('.')[0] for bug_version in bug_versions
    ]
    return bug_versions


def measure_total_kill_cnt(mbfl_feature_csv, f2p_p2f_key_list):
    tot_failed_TCs = 0
    with open(mbfl_feature_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tot_failed_TCs = int(row['# of totfailed_TCs'])
            break
    
    total_p2f = 0
    total_f2p = 0
    with open(mbfl_feature_csv, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            for f2p_name, p2f_name in f2p_p2f_key_list:
                f2p = int(row[f2p_name])
                p2f = int(row[p2f_name])

                if f2p == -1:
                    assert p2f == -1
                    continue
                if p2f == -1:
                    assert f2p == -1
                    continue

                total_f2p += f2p
                total_p2f += p2f

                assert tot_failed_TCs == int(row['# of totfailed_TCs']), f"tot_failed_TCs: {tot_failed_TCs} != row['# of totfailed_TCs']: {row['# of totfailed_TCs']}"

    return total_f2p, total_p2f, tot_failed_TCs


def measure_metallaxis(line_data, f2p_p2f_key_list):
    total_failing_tc_count = int(line_data['# of totfailed_TCs'])

    met_score_list = []
    # per mutant
    cnt = 0
    for f2p_m, p2f_m in f2p_p2f_key_list:
        cnt += 1
        f2p = int(line_data[f2p_m])
        p2f = int(line_data[p2f_m])

        if f2p == -1:
            assert p2f == -1, f'{p2f} != -1'
            continue
        if p2f == -1:
            assert f2p == -1, f'{f2p} != -1'
            continue

        score = 0.0
        if f2p + p2f == 0:
            score = 0.0
        else:
            score = ((f2p) / math.sqrt(total_failing_tc_count * (f2p + p2f)))

        met_score_list.append(score)

    assert cnt == 12, f'{cnt} != 12'

    if len(met_score_list) == 0:
        return 0.0

    final_met_score = max(met_score_list)
    return final_met_score

def measure_muse(line_data, total_f2p, total_p2f, f2p_p2f_key_list):
    utilized_mutant_cnt = 0
    line_total_f2p = 0
    line_total_p2f = 0

    final_muse_score = 0.0

    cnt = 0
    for f2p_m, p2f_m in f2p_p2f_key_list:
        cnt += 1
        f2p = int(line_data[f2p_m])
        p2f = int(line_data[p2f_m])

        if f2p == -1:
            assert p2f == -1, f'{p2f} != -1'
            continue
        if p2f == -1:
            assert f2p == -1, f'{f2p} != -1'
            continue

        utilized_mutant_cnt += 1
        line_total_p2f += p2f
        line_total_f2p += f2p
    
    assert cnt == 12, f'{cnt} != 12'

    muse_1 = (1 / ((utilized_mutant_cnt + 1) * (total_f2p + 1)))
    muse_2 = (1 / ((utilized_mutant_cnt + 1) * (total_p2f + 1)))

    muse_3 = muse_1 * line_total_f2p
    muse_4 = muse_2 * line_total_p2f

    final_muse_score = muse_3 - muse_4

    return final_muse_score


def check_measurement(mbfl_feature_csv, fail_cnt):
    f2p_p2f_key_list = []
    for i in range(1, 13):
        f2p_name = f'm{i}:f2p'
        p2f_name = f'm{i}:p2f'
        f2p_p2f_key_list.append((f2p_name, p2f_name))

    # first measure total_p2f and total_f2p
    total_f2p, total_p2f, tot_failed_TCs_past = measure_total_kill_cnt(mbfl_feature_csv, f2p_p2f_key_list)

    assert tot_failed_TCs_past == fail_cnt, f"tot_failed_TCs_past: {tot_failed_TCs_past} != len(failing_tc_list): {len(failing_tc_list)}"

    with open(mbfl_feature_csv, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            tot_failed_TCs = int(row['# of totfailed_TCs'])
            assert tot_failed_TCs == tot_failed_TCs_past, f"tot_failed_TCs: {tot_failed_TCs} != tot_failed_TCs_past: {tot_failed_TCs_past}"

            met_score = measure_metallaxis(row, f2p_p2f_key_list)
            muse_score = measure_muse(row, total_f2p, total_p2f, f2p_p2f_key_list)

            assert met_score == float(row['met susp. score']), f"met_score: {met_score} != row['meta susp. score']: {float(row['meta susp. score'])}"
            assert muse_score == float(row['muse susp. score']), f"muse_score: {muse_score} != row['muse susp. score']: {float(row['muse susp. score'])}"

def get_tcs(mbfl_dir, bug_id, tc_type):

    filename = f"{tc_type}_testcases.csv"
    tc_csv = mbfl_dir / 'test_case_info_per_bug_version' / bug_id / filename
    assert tc_csv.exists(), f"{tc_csv} does not exist"

    tcs = {}
    with open(tc_csv, 'r') as f:
        lines = f.readlines()
        for line in lines[1:]:
            line = line.strip()
            info = line.split(',')
            tc_id = info[0]
            tc_name = info[1]
            assert tc_id not in tcs, f"test case id {tc_id} already exists"
            tcs[tc_id] = tc_name
    
    return tcs

def validate_03(mbfl_dir):
    bug_versions = get_bug_versions(mbfl_dir)

    invalid_bug_dir = []

    cnt = 0
    for bug_id in bug_versions:
        cnt += 1
        print(f"{cnt}: Validating {bug_id}")

        # get test cases
        failing_tcs = get_tcs(mbfl_dir, bug_id, 'failing')
        fail_cnt = len(failing_tcs)

        # get feature file
        mbfl_feature_filename = f"{bug_id}.mbfl_features.csv"
        mbfl_feature_csv = mbfl_dir / 'mbfl_features_per_bug_version' / mbfl_feature_filename
        assert mbfl_feature_csv.exists(), f"{mbfl_feature_csv} does not exist"


        check_measurement(mbfl_feature_csv, fail_cnt)
        
        print(f"{bug_id} is valid")

    



if __name__ == "__main__":
    mbfl_dataset_dir_name = sys.argv[1]
    mbfl_dir = root_dir / 'mbfl_datasets' / mbfl_dataset_dir_name
    assert mbfl_dir.exists(), f"mbfl dataset {mbfl_dir} does not exist"

    validate_03(mbfl_dir)