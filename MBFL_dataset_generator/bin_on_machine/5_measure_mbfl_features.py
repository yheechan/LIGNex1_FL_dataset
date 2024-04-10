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
        csv_reader = csv.reader(csv_fp)
        next(csv_reader)
        for row in csv_reader:
            target_file = row[0]
            line_number = int(row[1])
            mutant_id = row[2]
            mutant_name = row[3]
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
    if line == 'build-success':
        return True
    else:
        return False

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

def measure_mbfl_features(core_dir, lines_list, mutant_dict):
    total_p2f, total_f2p = get_total_tc_results(core_dir)
    line_features = {}

    for target_file in mutant_dict.keys():
        if target_file not in line_features:
            line_features[target_file] = {}
        
        for line_key in mutant_dict[target_file].keys():
            
            line2mutant_cnt = 0
            line2met_1 = []
            line2met_2 = []
            line2met_3 = []
            line2met_4 = []
            
            muse_1 = 0
            muse_2 = 0
            muse_3 = 0
            muse_4 = 0
            muse_5 = 0
            muse_6 = 0
            # print('target_file: ', target_file)
            # print('line_key: ', line_key)
            # print('# of mutants: ', len(mutant_dict[target_file][line_key]))
            build_failed = 0
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
                    continue

                # get per mutant tc results
                p2f, f2p, p2p, f2f = get_per_mutant_tc_results(mutant_dir)

                # measuring metallaxis
                # killed(m) = p2f + f2p
                # notkilled(m) = p2p + f2f
                killed = p2f + f2p
                notkilled = p2p + f2f

                # only when mutant was killed
                if killed > 0:
                    met_1 = killed
                    
                    if killed == 0:
                        met_2 = 0
                    else:
                        met_2 = 1 / math.sqrt(killed)
                    met_3 = 1 / math.sqrt(killed + notkilled)
                    if killed == 0:
                        met_4 = 0
                    else:
                        met_4 = killed / math.sqrt(killed * (killed + notkilled))
                
                    line2met_1.append(met_1)
                    line2met_2.append(met_2)
                    line2met_3.append(met_3)
                    line2met_4.append(met_4)

                # measuring muse
                muse_2 += f2p
                muse_3 += p2f
            # print('# of build failed mutants: ', build_failed)
            if build_failed == len(mutant_dict[target_file][line_key]):
                continue

            if len(line2met_1) == 0:
                met_1 = 0
                met_2 = 0
                met_3 = 0
                met_4 = 0
            else:
                met_1 = max(line2met_1)
                met_2 = max(line2met_2)
                met_3 = max(line2met_3)
                met_4 = max(line2met_4)

            muse_1 = 1 / (line2mutant_cnt + 1)
            muse_4 = (1 / ((line2mutant_cnt + 1) * (total_f2p + 1))) * muse_2
            muse_5 = (1 / ((line2mutant_cnt + 1) * (total_p2f + 1))) * muse_3
            muse_6 = muse_4 - muse_5

            if line_key not in line_features[target_file]:
                line_features[target_file][line_key] = {}
            
            line_features[target_file][line_key] = {
                'met_1': met_1, 'met_2': met_2,
                'met_3': met_3, 'met_4': met_4,
                'muse_1': muse_1, 'muse_2': muse_2,
                'muse_3': muse_3, 'muse_4': muse_4,
                'muse_5': muse_5, 'muse_6': muse_6
            }
    return line_features

    for target_file in line_features.keys():
        for line_key in line_features[target_file].keys():
            for key in line_features[target_file][line_key].keys():
                print(f'{target_file}, {line_key}, {key}: {line_features[target_file][line_key][key]}')

def process2csv(core_dir, line_features, lines_list, buggy_line):
    default = {
        'met_1': 0, 'met_2': 0, 'met_3': 0, 'met_4': 0,
        'muse_1': 0, 'muse_2': 0, 'muse_3': 0, 'muse_4': 0, 'muse_5': 0, 'muse_6': 0, 'bug': 0
    }

    csv_file = core_dir / 'mbfl_data/mbfl_features.csv'
    
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=[
            'key', 'met_1', 'met_2', 'met_3', 'met_4',
            'muse_1', 'muse_2', 'muse_3', 'muse_4', 'muse_5', 'muse_6', 'bug'
        ])

        writer.writeheader()

        for line in lines_list:
            line_info = line.strip().split('#')
            file_path = line_info[0]
            line_number = int(line_info[-1])
            target_file = file_path.split('/')[-1]

            buggy_stat = 0
            if line == buggy_line:
                buggy_stat = 1

            if target_file in line_features:
                line_id = 'line_{}'.format(line_number)
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



if __name__ == "__main__":
    core_id = sys.argv[1]
    core_dir = main_dir / core_id

    lines_list = get_lines_list(core_dir)
    mutant_dict = get_mutant_dict(core_dir)
    line_features = measure_mbfl_features(core_dir, lines_list, mutant_dict)

    buggy_line = get_buggy_line(core_dir)
    print(buggy_line)
    assert buggy_line in lines_list
    process2csv(core_dir, line_features, lines_list, buggy_line)


