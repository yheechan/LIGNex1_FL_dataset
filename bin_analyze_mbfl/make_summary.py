#!/usr/bin/python3
import subprocess as sp
from pathlib import Path
import os
import csv
import sys
import pandas as pd
import json

script_path = Path(os.path.realpath(__file__))
bin_dir = script_path.parent
main_dir = bin_dir.parent

def custom_sort(bug):
    return int(bug[3:])

def get_bugs(mbfl_features_dataset_dir_name):
    mbfl_features_dataset_dir = main_dir / 'mbfl_datasets' / mbfl_features_dataset_dir_name
    mbfl_features_per_bug_version = mbfl_features_dataset_dir / 'mbfl_features_per_bug_version'
    assert mbfl_features_per_bug_version.exists()

    bug_list = []
    for bug_dir in mbfl_features_per_bug_version.iterdir():
        bug_id= bug_dir.name.split('.')[0]
        bug_list.append(bug_id)
    bug_list.sort(key=custom_sort)
    return bug_list

def get_buggy_line_key(mbfl_features_dataset_dir, bug_id):
    bug_line_key_file_name = '{}.buggy_line_key.txt'.format(bug_id)
    bug_line_key_file = mbfl_features_dataset_dir / 'buggy_line_key_per_bug_version' / bug_line_key_file_name
    assert bug_line_key_file.exists()

    with open(bug_line_key_file, 'r') as file:
        buggy_line_key = file.readline().strip()
    return buggy_line_key

def get_line_by_failing_dict(mbfl_features_dataset_dir, bug_id):
    failing_line_file_name = '{}.lines_executed_by_failing_tc.json'.format(bug_id)
    failing_line_file_json = mbfl_features_dataset_dir / 'lines_executed_by_failing_tc_per_bug_version' / failing_line_file_name
    assert failing_line_file_json.exists()

    # read with json
    with open(failing_line_file_json, 'r') as file:
        line_by_failing_dict = json.load(file)
    return line_by_failing_dict

def get_failing_dict(mbfl_features_dataset_dir, bug_id):
    failing_testcases_csv = mbfl_features_dataset_dir / 'test_case_info_per_bug_version' / bug_id / 'failing_testcases.csv'
    assert failing_testcases_csv.exists()

    failing_tc = {}
    with open(failing_testcases_csv, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            tc_id = row[0]
            tc_name = row[1]
            assert tc_id not in failing_tc
            failing_tc[tc_id] = tc_name
    return failing_tc

def check_compilation(mutant_dir):
    compile_log = mutant_dir / 'build_result.txt'
    assert compile_log.exists()

    with open(compile_log, 'r') as file:
        compile_result = file.readline().strip()
        if compile_result == 'build-success':
            return True
        else:
            return False

def get_mutated_line_data(mbfl_features_dataset_dir, bug_id, buggy_line_key):
    mutant_db_csv = mbfl_features_dataset_dir / 'mutant_info_per_bug_version' / bug_id / 'selected_mutants/mutants_db.csv'
    assert mutant_db_csv.exists()

    buggy_target_file = buggy_line_key.split('#')[0].split('/')[-1]
    buggy_line_num = int(buggy_line_key.split('#')[-1])

    line2mutants = {}
    number_of_mutants = 0
    number_of_uncompilable_mutants = 0
    number_of_mutants_on_buggy_line = 0
    number_of_uncompilable_mutants_on_buggy_line = 0
    number_of_compilable_mutants_on_buggy_line = 0

    # get the number of mutants from per mutant dir by counting the number of dirs
    per_mutant_dir = mbfl_features_dataset_dir / 'mutant_info_per_bug_version' / bug_id / 'per_mutant_data'
    assert per_mutant_dir.exists()
    num_of_mutants_in_per_mutant_dir = 0
    for mutant_dir in per_mutant_dir.iterdir():
        num_of_mutants_in_per_mutant_dir += 1


    # get the number of mutants from db by reading line by line
    num_of_mutants_from_db = 0
    with open(mutant_db_csv, 'r') as file:
        lines = file.readlines()
        for line in lines[1:]:
            num_of_mutants_from_db += 1

            info = line.strip().split(',')
            target_file = info[0]
            line_no = int(info[1])
            mutant_id = info[2]

            # 3. validate that the mutant dir exists
            mutant_dir = mbfl_features_dataset_dir / 'mutant_info_per_bug_version' / bug_id / 'per_mutant_data' / mutant_id
            assert mutant_dir.exists()

            # increment the number of mutants
            if line_no not in line2mutants:
                line2mutants[line_no] = []
            line2mutants[line_no].append(mutant_id)
            number_of_mutants += 1

            # check the number of uncompilable mutants
            compiled = check_compilation(mutant_dir)
            if not compiled:
                number_of_uncompilable_mutants += 1
            
            # check mutants on buggy line
            if target_file == buggy_target_file and line_no == buggy_line_num:
                number_of_mutants_on_buggy_line += 1
                if not compiled:
                    number_of_uncompilable_mutants_on_buggy_line += 1
                else:
                    number_of_compilable_mutants_on_buggy_line += 1
    

    assert num_of_mutants_from_db == num_of_mutants_in_per_mutant_dir, f'{num_of_mutants_from_db} != {num_of_mutants_in_per_mutant_dir}'

    # with open(mutant_db_csv, 'r') as file:
    #     reader = csv.reader(file)
    #     next(reader)

    #     for row in reader:
    #         target_file = row[0]
    #         line_no = int(row[1])
    #         mutant_id = row[2]

    #         # 3. validate that the mutant dir exists
    #         mutant_dir = mbfl_features_dataset_dir / 'mutant_info_per_bug_version' / bug_id / 'per_mutant_data' / mutant_id
    #         assert mutant_dir.exists()

    #         # increment the number of mutants
    #         if line_no not in line2mutants:
    #             line2mutants[line_no] = []
    #         line2mutants[line_no].append(mutant_id)
    #         number_of_mutants += 1

    #         # check the number of uncompilable mutants
    #         compiled = check_compilation(mutant_dir)
    #         if not compiled:
    #             number_of_uncompilable_mutants += 1
            
    #         # check mutants on buggy line
    #         if target_file == buggy_target_file and line_no == buggy_line_num:
    #             number_of_mutants_on_buggy_line += 1
    #             if not compiled:
    #                 number_of_uncompilable_mutants_on_buggy_line += 1
    #             else:
    #                 number_of_compilable_mutants_on_buggy_line += 1
                
    
    data = {
        'number_of_mutants': number_of_mutants,
        'number_of_uncompilable_mutants': number_of_uncompilable_mutants,
        'number_of_mutants_on_buggy_line': number_of_mutants_on_buggy_line,
        'number_of_uncompilable_mutants_on_buggy_line': number_of_uncompilable_mutants_on_buggy_line,
        'number_of_compilable_mutants_on_buggy_line': number_of_compilable_mutants_on_buggy_line,
        'line2mutants': line2mutants
    }
    return data

def get_susp_scores(mbfl_features_dataset_dir, bug_id, buggy_line_key):
    feature_file_name = '{}.mbfl_features.csv'.format(bug_id)
    susp_scores_csv = mbfl_features_dataset_dir / 'mbfl_features_per_bug_version' / feature_file_name
    assert susp_scores_csv.exists()

    met_score = 0.0
    muse_score = 0.0

    with open(susp_scores_csv, 'r') as file:
        reader = csv.reader(file)
        next(reader)

        for row in reader:
            line_key = row[0]
            met_score = float(row[4])
            muse_score = float(row[10])
            is_bug = row[11]

            if line_key == buggy_line_key:
                # 3. validate that the buggy line has a bug
                assert is_bug == '1'
                data = {
                    'met_score': met_score,
                    'muse_score': muse_score
                }
                return data
    return {}
def get_total_tc_results(mbfl_features_dataset_dir, bug_id):
    total_p2f = 0
    total_f2p = 0

    file_name = '{}.total_tc_results.csv'.format(bug_id)
    tc_results_csv = mbfl_features_dataset_dir / 'total_p2f_f2p_per_bug_version' / file_name
    assert tc_results_csv.exists()

    with open(tc_results_csv, 'r') as file:
        reader = csv.reader(file)
        next(reader)

        cnt = 0
        for row in reader:
            p2f = int(row[0])
            f2p = int(row[1])

            total_p2f = p2f
            total_f2p = f2p
            assert cnt == 0, 'There should be only one row'
            cnt += 1
            
    return total_p2f, total_f2p

def get_rank(mbfl_features_dataset_dir, bug_id, buggy_line_key):
    mbfl_features_csv = mbfl_features_dataset_dir / 'mbfl_features_per_bug_version' / '{}.mbfl_features.csv'.format(bug_id)
    assert mbfl_features_csv.exists()

    # include/json/reader.h#CharReader::~CharReader()#247
    buggy_target_file = buggy_line_key.split('#')[0].split('/')[-1]
    buggy_function_name = buggy_line_key.split('#')[1]
    buggy_line_num = int(buggy_line_key.split('#')[-1])
    # print('Buggy Line:', buggy_target_file, buggy_function_name, buggy_line_num)

    mbfl_features_df = pd.read_csv(mbfl_features_csv)
    # 1. SET ALL BUGGY LINE OF BUGGY FUNCTION TO BUG1
    for index, row in mbfl_features_df.iterrows():
        # split the 'key' column by '#'
        key = row['key']
        target_file = key.split('#')[0].split('/')[-1]
        function_name = key.split('#')[1]
        line_num = int(key.split('#')[-1])

        # drop 'key' column and add target_file, function_name, line_num as columns
        mbfl_features_df.at[index, 'target_file'] = target_file
        mbfl_features_df.at[index, 'function_name'] = function_name
        mbfl_features_df.at[index, 'line_num'] = line_num


        # check if the row is the buggy line
        if target_file == buggy_target_file and function_name == buggy_function_name:
            # print('Buggy Line found:', target_file, function_name, line_num)
            # set the 'bug' column as 1
            mbfl_features_df.at[index, 'bug'] = 1
        else:
            # set the 'bug' column as 0
            mbfl_features_df.at[index, 'bug'] = 0
    
    # 2. DROP THE LINENO COLUMN
    mbfl_features_df = mbfl_features_df.drop(columns=['key'])
    mbfl_features_df = mbfl_features_df[[
        'target_file', 'function_name', 'line_num',
        'met_1', 'met_2', 'met_3', 'met_4',
        'muse_1', 'muse_2', 'muse_3', 'muse_4', 'muse_5', 'muse_6',
        'bug'
    ]]

    # 3. GROUP ROWS BY SAME FUNCTION NAME AND
    # APPLY VALUE OF THE LINE WITH THE HIGHEST VALUE OF THE FORMULA
    mbfl_features_df = mbfl_features_df.groupby(['target_file', 'function_name']).apply(lambda x: x.nlargest(1, 'muse_6')).reset_index(drop=True)

    # 4. SORT THE ROWS BY THE FORMULA VALUE
    mbfl_features_df = mbfl_features_df.sort_values(by='muse_6', ascending=False).reset_index(drop=True)
    
    # 5. ADD A RANK COLUMN TO THE DF
    # THE RANK IS IN THE STANDARD OF FORMULA COLUMN
    # IF THE RANK IS A TIE, THE RANK IS THE UPPER BOUND OF THE TIE
    mbfl_features_df['rank'] = mbfl_features_df['muse_6'].rank(ascending=False, method='max').astype(int)

    # 6. GET THE RANK OF THE BUGGY LINE
    # AND THE MINIMUM RANK OF THE FORMULA
    # AND THE SCORE
    func_n = mbfl_features_df.shape[0]
    total_num_of_func = 0
    best_rank = sys.maxsize
    best_score = None
    bug_rank = -1
    bug_score = None
    for index, row in mbfl_features_df.iterrows():
        total_num_of_func += 1
        curr_rank = row['rank']
        curr_target_file = row['target_file']
        curr_function_name = row['function_name']
        curr_score = row['muse_6']

        # assign the best rank number
        if curr_rank < best_rank:
            best_rank = curr_rank
            best_score = curr_score
        
        if curr_rank == best_rank:
            assert curr_score == best_score, f'{curr_score} != {best_score}'
        
        # assign the rank of the buggy line
        if curr_target_file == buggy_target_file and \
            curr_function_name == buggy_function_name:
            assert bug_rank == -1, 'The buggy line is found more than once'
            bug_rank = curr_rank
            bug_score = curr_score
            assert row['bug'] == 1, 'The buggy line is not marked as bug'
    
    # rank = mbfl_features_df[mbfl_features_df['bug'] == 1].index[0] + 1
    # write csv
    # mbfl_features_df.to_csv('tmp.csv', index=False)

    # print('Rank:', rank)

    # return rank
    return bug_rank

def make_summary_csv(mbfl_features_dataset_dir_name, bug_isd):
    mbfl_features_dataset_dir = main_dir / 'mbfl_datasets' / mbfl_features_dataset_dir_name
    # summary_csv = mbfl_features_dataset_dir / 'summary.csv'

    bug_list = []
    cnt = 0
    for bug_id in bug_ids:
        cnt += 1
        print('{} Processing bug_id: {}'.format(cnt, bug_id))

        buggy_line_key = get_buggy_line_key(mbfl_features_dataset_dir, bug_id)
        line_by_failing_dict = get_line_by_failing_dict(mbfl_features_dataset_dir, bug_id)

        # 1. validate the buggy line is executed by failing tc
        assert buggy_line_key in line_by_failing_dict
        print(buggy_line_key)

        failing_tc_dict = get_failing_dict(mbfl_features_dataset_dir, bug_id)

        # 2. validate that all failing tc executes the buggy line
        for tc_id in failing_tc_dict:
            assert tc_id in line_by_failing_dict[buggy_line_key]
        
        mutated_line_data = get_mutated_line_data(mbfl_features_dataset_dir, bug_id, buggy_line_key)
        # validate the number of mutants on buggy line
        assert mutated_line_data['number_of_mutants_on_buggy_line'] == mutated_line_data['number_of_uncompilable_mutants_on_buggy_line'] + mutated_line_data['number_of_compilable_mutants_on_buggy_line']

        total_p2f, total_f2p = get_total_tc_results(mbfl_features_dataset_dir, bug_id)
        

        susp_scores = get_susp_scores(mbfl_features_dataset_dir, bug_id, buggy_line_key)
        assert susp_scores is not {}

        rank = get_rank(mbfl_features_dataset_dir, bug_id, buggy_line_key)
        print('rank (muse_6): {}'.format(rank))

        # write to summary.csv
        bug_list.append({
            'bug_id': bug_id,
            'buggy_line_key': buggy_line_key,

            'total # of failing TCs': len(failing_tc_dict),

            'total # of lines executed by failing TCs': len(line_by_failing_dict),
            'total # of mutants': mutated_line_data['number_of_mutants'],
            'total # of uncompilable mutants': mutated_line_data['number_of_uncompilable_mutants'],
            
            'total # of mutants on buggy line': mutated_line_data['number_of_mutants_on_buggy_line'],
            'total # of uncompilable mutants on buggy line': mutated_line_data['number_of_uncompilable_mutants_on_buggy_line'],
            'total # of compilable mutants on buggy line': mutated_line_data['number_of_compilable_mutants_on_buggy_line'],

            'total p2f': total_p2f,
            'total f2p': total_f2p,

            'metallaxis score': susp_scores['met_score'],
            'muse score': susp_scores['muse_score'],

            'rank (function level)': rank
        })
    
    file_name = mbfl_features_dataset_dir / 'statistics_summary.csv'
    with open(file_name, 'w') as file:
        writer = csv.DictWriter(file, fieldnames=bug_list[0].keys())
        writer.writeheader()
        writer.writerows(bug_list)



if __name__ == "__main__":
    mbfl_features_dataset_dir_name = sys.argv[1]
    bug_ids = get_bugs(mbfl_features_dataset_dir_name)
    make_summary_csv(mbfl_features_dataset_dir_name, bug_ids)
