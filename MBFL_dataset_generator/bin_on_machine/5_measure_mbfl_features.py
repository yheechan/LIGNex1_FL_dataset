#!/usr/bin/python3
import subprocess as sp
from pathlib import Path
import os
import sys
import csv
import math

script_path = Path(os.path.realpath(__file__))
bin_dir = script_path.parent
main_dir = bin_dir.parent

def get_lines_list(core_dir):
    cov_data_csv = core_dir / 'prerequisite_data/postprocessed_coverage_data/cov_data.csv'
    assert cov_data_csv.exists(), f'{cov_data_csv} does not exist'

    lines_list = []
    with open(cov_data_csv, 'r') as csv_fp:
        csv_reader = csv.reader(csv_fp)
        next(csv_reader)
        for row in csv_reader:
            lines_list.append(row[0])
    return lines_list

def get_mutant_dict(core_dir):
    mutant_db_csv = core_dir / 'mbfl_data/selected_mutants/mutants_db.csv'
    assert mutant_db_csv.exists(), f'{mutant_db_csv} does not exist'

    mutant_dict = {}
    with open(mutant_db_csv, 'r') as csv_fp:
        # csv_reader = csv.reader(csv_fp)
        # next(csv_reader)
        lines = csv_fp.readlines()

        # for row in csv_reader:
        for line in lines[1:]:
            info = line.strip().split(',')
            target_file = info[0]
            line_number = int(info[1])
            mutant_id = info[2]
            mutant_name = info[3]

            # using CSV (UPDATED: NOT USING CSV BECAUSE MUTANT TOKEN CONTAINS COMPILCATED COMMANS AND QUOTES)
            # target_file = row[0]
            # line_number = int(row[1])
            # mutant_id = row[2]
            # mutant_name = row[3]

            # not using
            # mutation_operator = row[4]
            # before_mutation = row[5]
            # after_mutation = row[6]

            if target_file not in mutant_dict:
                mutant_dict[target_file] = {}
            line_id = 'line_{}'.format(line_number)
            if line_id not in mutant_dict[target_file]:
                mutant_dict[target_file][line_id] = []
            mutant_dict[target_file][line_id].append({
                'mutant_id': mutant_id,
                'mutant_name': mutant_name,
            })
    return mutant_dict

def get_total_tc_results(core_dir):
    p2f = 0
    f2p = 0

    total_tc_results_csv = core_dir / 'mbfl_data/total_tc_results.csv'
    assert total_tc_results_csv.exists(), f'{total_tc_results_csv} does not exist'
    total_tc_results_fp = open(total_tc_results_csv, 'r')
    lines = total_tc_results_fp.readlines()
    total_tc_results_fp.close()

    info = lines[1].strip().split(',')
    p2f = int(info[0])
    f2p = int(info[1])

    return p2f, f2p


def check_build_results(mutant_dir):
    build_result_txt = mutant_dir / 'build_result.txt'
    assert build_result_txt.exists(), f'{build_result_txt} does not exist'

    build_result_fp = open(build_result_txt, 'r')
    lines = build_result_fp.readlines()
    build_result_fp.close()

    line = lines[0].strip()
    if line == 'build-failed':
        return False
    else:
        if line != 'build-success':
            print(f'Unexpected build result: {line}')
        return True

def get_per_mutant_tc_results(mutant_dir):
    p2f = 0
    f2p = 0
    p2p = 0
    f2f = 0

    tc_results_csv = mutant_dir / 'mutant_tc_results.csv'
    assert tc_results_csv.exists(), f'{tc_results_csv} does not exist'
    tc_results_fp = open(tc_results_csv, 'r')
    lines = tc_results_fp.readlines()
    tc_results_fp.close()

    line = lines[1].strip()
    info = line.split(',')
    p2f = int(info[0])
    f2p = int(info[1])
    p2p = int(info[2])
    f2f = int(info[3])

    return p2f, f2p, p2p, f2f

def get_mbfl_features(core_dir, lines_list, mutant_dict):
    # for a single bug version
    total_p2f, total_f2p = get_total_tc_results(core_dir)

    total_p2f_recalc = 0
    total_f2p_recalc = 0

    line_features = {}
    # for a target file of a bug version
    for target_file in mutant_dict.keys():
        if target_file not in line_features:
            line_features[target_file] = {}
        
        # for a target line of a target file
        for line_key in mutant_dict[target_file].keys():
            
            line2mutant_cnt = 0
            build_failed = 0

            if line_key not in line_features[target_file]:
                line_features[target_file][line_key] = []

            # for a mutant of a target line of a target file
            for mutant in mutant_dict[target_file][line_key]:

                mutant_id = mutant['mutant_id']
                mutant_name = mutant['mutant_name']

                # check build results and continue if build failed
                mutant_dir = core_dir / 'mbfl_data/per_mutant_data' / mutant_id
                # print('\tmutant_name: ', mutant_name)
                if check_build_results(mutant_dir):
                    line2mutant_cnt += 1
                else:
                    build_failed += 1
                    line_features[target_file][line_key].append({
                        'mutant_id': mutant_id,
                        'mutant_name': mutant_name,
                        'build_failed': True,
                        'p2f': -1, 'f2p': -1, 'p2p': -1, 'f2f': -1,
                    })
                    continue

                # get per mutant tc results
                p2f, f2p, p2p, f2f = get_per_mutant_tc_results(mutant_dir)

                

                # ACCUMULATE DATA ON EACH MUTANT OF EACH LINE OF EACH FILE
                line_features[target_file][line_key].append({
                    'mutant_id': mutant_id,
                    'mutant_name': mutant_name,
                    'build_failed': False,
                    'p2f': p2f, 'f2p': f2p, 'p2p': p2p, 'f2f': f2f
                })

                # accumulate p2f and f2p for recalculation assertion
                total_p2f_recalc += p2f
                total_f2p_recalc += f2p
        
            # append dummy mutant until each line get 12 mutants
            assert len(line_features[target_file][line_key]) <= 12, f'{linefeatures[target_file][line_key]} > 12'
            for i in range(12 - len(line_features[target_file][line_key])):
                line_features[target_file][line_key].append({
                    'mutant_id': -1,
                    'mutant_name': 'dummy',
                    'build_failed': False,
                    'p2f': -1, 'f2p': -1, 'p2p': -1, 'f2f': -1
                })
            assert len(line_features[target_file][line_key]) == 12, f'{len(line_features[target_file][line_key])} != 12'
        
    
    assert total_f2p == total_f2p_recalc, f'{total_f2p} != {total_f2p_recalc}'
    assert total_p2f == total_p2f_recalc, f'{total_p2f} != {total_p2f_recalc}'
    # print(f"total_f2p: {total_f2p_recalc}, total_f2p_recalc: {total_f2p}")
    # print(f"total_p2f: {total_p2f_recalc}, total_p2f_recalc: {total_p2f}")


    return line_features, total_p2f_recalc, total_f2p_recalc

    # for target_file in line_features.keys():
    #     for line_key in line_features[target_file].keys():
    #         for key in line_features[target_file][line_key].keys():
    #             print(f'{target_file}, {line_key}, {key}: {line_features[target_file][line_key][key]}')

def measure_metallaxis(line_data, f2p_p2f_key_list):
    total_failing_tc_count = line_data['# of totfailed_TCs']

    met_score_list = []
    # per mutant
    cnt = 0
    for f2p_m, p2f_m in f2p_p2f_key_list:
        cnt += 1
        f2p = line_data[f2p_m]
        p2f = line_data[p2f_m]

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
        f2p = line_data[f2p_m]
        p2f = line_data[p2f_m]

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
    
    muse_data = {
        '|mut(s)|': utilized_mutant_cnt,
        'total_f2p': total_f2p,
        'total_p2f': total_p2f,
        'line_total_f2p': line_total_f2p,
        'line_total_p2f': line_total_p2f,
        'muse_1': muse_1,
        'muse_2': muse_2,
        'muse_3': muse_3,
        'muse_4': muse_4,
        'muse susp. score': final_muse_score
    }

    return muse_data



def measure_mbfl_features(line_features, total_p2f, total_f2p, total_failing_tc_count):
    measured_features = {}

    recalc_total_p2f = 0
    recalc_total_f2p = 0

    for target_file in line_features.keys():
        if target_file not in measured_features:
            measured_features[target_file] = {}
        
        for line_key in line_features[target_file].keys():
            if line_key not in measured_features[target_file]:
                measured_features[target_file][line_key] = {}
            
            measured_features[target_file][line_key]['# of totfailed_TCs'] = total_failing_tc_count
            
            cnt = 0
            f2p_p2f_key_list = []
            for mutant in line_features[target_file][line_key]:
                mutant_id = mutant['mutant_id']
                
                p2f = mutant['p2f']
                f2p = mutant['f2p']
                p2p = mutant['p2p']
                f2f = mutant['f2f']

                mutant_name = mutant['mutant_name']
                build_failed = mutant['build_failed']

                # VALIDATION
                if build_failed or mutant_name == 'dummy':
                    assert p2f == -1 and f2p == -1, f'{p2f} != -1 or {f2p} != -1'
                
                if p2f == -1:
                    assert build_failed or (mutant_name == 'dummy')
                    assert f2p == -1, f'{f2p} != -1'
                if f2p == -1:
                    assert build_failed or (mutant_name == 'dummy')
                    assert p2f == -1, f'{p2f} != -1'

                    
                cnt += 1
                f2p_name = f"m{cnt}:f2p"
                p2f_name = f"m{cnt}:p2f"

                assert f2p_name not in measured_features[target_file][line_key]
                assert p2f_name not in measured_features[target_file][line_key]
                f2p_p2f_key_list.append((f2p_name, p2f_name))

                measured_features[target_file][line_key][f2p_name] = f2p
                measured_features[target_file][line_key][p2f_name] = p2f

                if p2f != -1 or f2p != -1:
                    recalc_total_p2f += p2f
                    recalc_total_f2p += f2p

            assert cnt == 12, f'{cnt} != 12'
            measured_features[target_file][line_key]['# of mutants'] = cnt

            met_score = measure_metallaxis(measured_features[target_file][line_key], f2p_p2f_key_list)
            measured_features[target_file][line_key]['met susp. score'] = met_score

            muse_data = measure_muse(measured_features[target_file][line_key], total_f2p, total_p2f, f2p_p2f_key_list)
            for key, value in muse_data.items():
                assert key not in measured_features[target_file][line_key]
                measured_features[target_file][line_key][key] = value

            # print(f'{target_file}, {line_key}, met: {met_score}')
            # print(f'{target_file}, {line_key}, muse: {muse_data["muse susp. score"]}')
    
    assert total_f2p == recalc_total_f2p, f'{total_f2p} != {recalc_total_f2p}'
    assert total_p2f == recalc_total_p2f, f'{total_p2f} != {recalc_total_p2f}'
    return measured_features


def process2csv(core_dir, line_features, lines_list, buggy_line, total_failing_tc_count):
    # default = {
    #     'met_1': 0, 'met_2': 0, 'met_3': 0, 'met_4': 0,
    #     'muse_a': 0, 'muse_b': 0, 'muse_c': 0,
    #     'muse_1': 0, 'muse_2': 0, 'muse_3': 0, 'muse_4': 0, 'muse_5': 0, 'muse_6': 0, 'bug': 0
    # }

    

    csv_file = core_dir / 'mbfl_data/mbfl_features.csv'

    f2p_p2f_key_default_dict = {}
    for i in range(1, 13):
        f2p_name = f'm{i}:f2p'
        p2f_name = f'm{i}:p2f'
        f2p_p2f_key_default_dict[f2p_name] = -1
        f2p_p2f_key_default_dict[p2f_name] = -1
    
    default = {
        '# of totfailed_TCs': total_failing_tc_count,
        '# of mutants': len(f2p_p2f_key_default_dict) // 2,
        '|mut(s)|': 0, 'total_f2p': 0, 'total_p2f': 0,
        'line_total_f2p': 0, 'line_total_p2f': 0,
        'muse_1': 0, 'muse_2': 0, 'muse_3': 0, 'muse_4': 0,
        'muse susp. score': 0.0, 'met susp. score': 0.0, 'bug': 0,
        **f2p_p2f_key_default_dict
    }
    
    # write to csv file
    with open(csv_file, mode='w', newline='') as file:
        # writer = csv.DictWriter(file, fieldnames=[
        #     'key', 'met_1', 'met_2', 'met_3', 'met_4',
        #     'muse_a', 'muse_b', 'muse_c',
        #     'muse_1', 'muse_2', 'muse_3', 'muse_4', 'muse_5', 'muse_6', 'bug'
        # ])

        fieldnames = ['key', '# of totfailed_TCs', '# of mutants'] + list(f2p_p2f_key_default_dict.keys()) + [
            '|mut(s)|', 'total_f2p', 'total_p2f',
            'line_total_f2p', 'line_total_p2f',
            'muse_1', 'muse_2', 'muse_3', 'muse_4',
            'muse susp. score', 'met susp. score', 'bug'
        ]

        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()

        for line in lines_list:
            line_info = line.strip().split('#')
            file_path = line_info[0]
            line_number = int(line_info[-1])
            target_file = file_path.split('/')[-1]

            buggy_stat = 0
            # Change buggy_stat to 1 if the line is buggy line
            if line == buggy_line:
                buggy_stat = 1

            if target_file in line_features:
                line_id = 'line_{}'.format(line_number)
                
                # if the line is in the line_features
                # else use default values
                if line_id in line_features[target_file]:
                    line_features[target_file][line_id]['bug'] = buggy_stat
                    writer.writerow({
                        'key': line, **line_features[target_file][line_id]
                    })
                else:
                    default['bug'] = buggy_stat
                    writer.writerow({
                        'key': line, **default
                    })
            else:
                default['bug'] = buggy_stat
                writer.writerow({
                    'key': line, **default
                })


def get_buggy_line(core_dir):
    buggy_line_key_txt = core_dir / 'prerequisite_data/buggy_line_key.txt'
    assert buggy_line_key_txt.exists(), f'{buggy_line_key_txt} does not exist'

    buggy_line_key_fp = open(buggy_line_key_txt, 'r')
    lines = buggy_line_key_fp.readlines()
    buggy_line_key_fp.close()

    buggy_line_key = lines[0].strip()
    info = buggy_line_key.split('#')
    assert len(info) == 3

    return buggy_line_key

def get_tc_dict(core_dir):
    tc_dict = {
        'failing_testcases.csv': [],
        'passing_testcases.csv': []
    }

    testcase_info_dir = core_dir / 'prerequisite_data/testcase_info'
    for tc_type in tc_dict.keys():
        tc_file = testcase_info_dir / tc_type
        assert tc_file.exists(), f'{tc_file} does not exist'

        tc_fp = open(tc_file, 'r')
        lines = tc_fp.readlines()
        tc_fp.close()

        for line in lines[1:]:
            info = line.strip().split(',')
            tc_id = info[0]
            tc_name = info[1]
            tc_dict[tc_type].append([tc_id, tc_name])
    
    return tc_dict


if __name__ == "__main__":
    core_id = sys.argv[1]
    core_dir = main_dir / core_id

    lines_list = get_lines_list(core_dir)
    mutant_dict = get_mutant_dict(core_dir)
    tc_dict = get_tc_dict(core_dir)
    total_failing_tc_count = len(tc_dict['failing_testcases.csv'])

    # get pre-required mbfl feature before susp. score measurement
    line_features, total_p2f, total_f2p = get_mbfl_features(core_dir, lines_list, mutant_dict)

    # measure susp. score
    measure_features_per_line = measure_mbfl_features(line_features, total_p2f, total_f2p, total_failing_tc_count)

    buggy_line = get_buggy_line(core_dir)
    print(buggy_line)
    assert buggy_line in lines_list
    process2csv(core_dir, measure_features_per_line, lines_list, buggy_line, total_failing_tc_count)


