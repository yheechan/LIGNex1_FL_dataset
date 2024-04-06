#!/usr/bin/python3

import sys
from pathlib import Path
import subprocess as sp
import json
import csv
import pandas as pd

script_path = Path(__file__).resolve()
bin_dir = script_path.parent
root_dir = bin_dir.parent

def custom_sort(bug):
    return int(bug[3:])

def get_bugs(mbfl_dataset_dir):
    mbfl_features_per_bug_version = mbfl_dataset_dir / 'mbfl_features_per_bug_version'
    assert mbfl_features_per_bug_version.exists()

    bug_list = []
    for bug_dir in mbfl_features_per_bug_version.iterdir():
        bug_id= bug_dir.name.split('.')[0]
        bug_list.append(bug_id)

    bug_list.sort(key=custom_sort)

    return bug_list

def get_buggy_line_key(mbfl_dataset_dir, bug_id):
    # Get the buggy_line_key_per_bug_version directory
    buggy_line_key_per_bug_version = mbfl_dataset_dir / 'buggy_line_key_per_bug_version'
    assert buggy_line_key_per_bug_version.exists()

    # get the buggy_line_key_txt file for the bug_id
    filename = f'{bug_id}.buggy_line_key.txt'
    buggy_line_key_txt = buggy_line_key_per_bug_version / filename
    assert buggy_line_key_txt.exists()

    buggy_line_key = None
    # Read the buggy_line_key from the file
    with open(buggy_line_key_txt, 'r') as f:
        buggy_line_key = f.read().strip()
    assert buggy_line_key is not None, f'buggy_line_key is None for {bug_id}'
    
    return buggy_line_key

def get_lines_by_failing_TCs(mbfl_dataset_dir, bug_id):
    # Get the lines_executed_by_failing_TCs_per_bug_version directory
    lines_executed_by_failing_TCs_per_bug_version = mbfl_dataset_dir / 'lines_executed_by_failing_TCs_per_bug_version'
    assert lines_executed_by_failing_TCs_per_bug_version.exists()

    # get the lines_by_failing_TCs_json file for the bug_id
    filename = f'{bug_id}.lines_executed_by_failing_TCs.json'
    lines_executed_by_failing_TCs_json = lines_executed_by_failing_TCs_per_bug_version / filename
    assert lines_executed_by_failing_TCs_json.exists()

    lines_by_failing_TCs = None
    # Read the lines_by_failing_TCs from the file
    with open(lines_executed_by_failing_TCs_json, 'r') as f:
        lines_by_failing_TCs = json.load(f)
    assert lines_by_failing_TCs is not None, f'lines_by_failing_TCs is None for {bug_id}'
    
    return lines_by_failing_TCs

def get_failing_TCs(mbfl_dataset_dir, bug_id):
    # Get the failing_TCs_per_bug_version directory
    tc_info_dir = mbfl_dataset_dir / 'test_case_info_per_bug_version' / bug_id
    assert tc_info_dir.exists()

    # get the failing_TCs_txt file for the bug_id
    failing_TCs_csv = tc_info_dir / 'failing_testcases.csv'
    assert failing_TCs_csv.exists()

    failing_TCs = {}
    # Read the failing_TCs from the file
    with open(failing_TCs_csv, 'r') as f:
        lines = f.readlines()
        for line in lines[1:]:
            line = line.strip()
            info = line.split(',')
            tc_id = info[0]
            tc_name = info[1]

            assert tc_id not in failing_TCs, f'{tc_id} already in failing_TCs'
            failing_TCs[tc_id] = tc_name
    return failing_TCs

def check_compilation(mutant_dir):
    compile_log = mutant_dir / 'build_result.txt'
    assert compile_log.exists()

    with open(compile_log, 'r') as file:
        compile_result = file.readline().strip()
        if compile_result == 'build-success':
            return True
        else:
            return False

def get_mutant_data(mbfl_dataset_dir, bug_id, buggy_line_key):
    mutant_db_csv = mbfl_dataset_dir / 'mutants_data_per_bug_version' / bug_id / 'selected_mutants/mutants_db.csv'
    assert mutant_db_csv.exists(), f'{mutant_db_csv} does not exist'

    buggy_target_file = buggy_line_key.split('#')[0].split('/')[-1]
    buggy_line_num = int(buggy_line_key.split('#')[-1])

    line2mutants = {}
    number_of_mutants = 0
    number_of_uncompilable_mutants = 0
    number_of_mutants_on_buggy_line = 0
    number_of_uncompilable_mutants_on_buggy_line = 0
    number_of_compilable_mutants_on_buggy_line = 0

    # get the number of mutants from per mutant dir by counting the number of dirs
    per_mutant_dir = mbfl_dataset_dir / 'mutants_data_per_bug_version' / bug_id / 'per_mutant_data'
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
            mutant_dir = mbfl_dataset_dir / 'mutants_data_per_bug_version' / bug_id / 'per_mutant_data' / mutant_id
            assert mutant_dir.exists()

            # increment the number of mutants
            number_of_mutants += 1
            
            # add mutant to line2mutants
            if line_no not in line2mutants:
                line2mutants[line_no] = []
            line2mutants[line_no].append(mutant_id)

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
    
    # assert that db and per mutant dir have the same number of mutants
    assert num_of_mutants_from_db == num_of_mutants_in_per_mutant_dir, f'{num_of_mutants_from_db} != {num_of_mutants_in_per_mutant_dir}'

    data = {
        'number_of_mutants': number_of_mutants,
        'number_of_uncompilable_mutants': number_of_uncompilable_mutants,
        'number_of_mutants_on_buggy_line': number_of_mutants_on_buggy_line,
        'number_of_uncompilable_mutants_on_buggy_line': number_of_uncompilable_mutants_on_buggy_line,
        'number_of_compilable_mutants_on_buggy_line': number_of_compilable_mutants_on_buggy_line,
        'line2mutants': line2mutants
    }
    return data

def get_total_TC_results(mbfl_dataset_dir, bug_id):
    total_p2f = 0
    total_f2p = 0

    file_name = f"{bug_id}.total_tc_results.csv"
    tc_results_csv = mbfl_dataset_dir / 'total_p2f_f2p_per_bug_version' / file_name
    assert tc_results_csv.exists()

    with open(tc_results_csv, 'r') as file:
        lines = file.readlines()
        cnt = 0
        for line in lines[1:]:
            cnt += 1
            line = line.strip()
            info = line.split(',')
            p2f = int(info[0])
            f2p = int(info[1])
        
        assert cnt == 1, 'There should be only one row'
        total_p2f = p2f
        total_f2p = f2p
        return total_p2f, total_f2p


def get_susp_scores(mbfl_dataset_dir, bug_id, buggy_line_key):
    filename = f"{bug_id}.mbfl_features.csv"
    susp_scores_csv = mbfl_dataset_dir / 'mbfl_features_per_bug_version' / filename
    assert susp_scores_csv.exists(), f'{susp_scores_csv} does not exist'

    met_score = None
    muse_score = None

    data = None
    with open(susp_scores_csv, 'r') as file:
        reader = csv.reader(file)
        next(reader)

        for row in reader:
            line_key = row[0]
            met_score = float(row[1])
            muse_score = float(row[2])
            is_bug = row[11]

            if line_key == buggy_line_key:
                assert is_bug == '1', f'{buggy_line_key} is not a bug'
                data = {
                    'met_score': met_score,
                    'muse_score': muse_score
                }
                return data
    return data

def get_rank_at_method_level(mbfl_dataset_dir, bug_id, buggy_line_key, formula):
    filename = f"{bug_id}.mbfl_features.csv"
    features_csv = mbfl_dataset_dir / 'mbfl_features_per_bug_version' / filename
    assert features_csv.exists(), f'{features_csv} does not exist'

    buggy_target_file = buggy_line_key.split('#')[0].split('/')[-1]
    buggy_function_name = buggy_line_key.split('#')[1]
    buggy_line_num = int(buggy_line_key.split('#')[-1])

    mbfl_features_df = pd.read_csv(features_csv)

    # 1. SET ALL BUGGY LINE OF BUGGY FUNCTION TO 1
    for index, row in mbfl_features_df.iterrows():
        key = row['key']
        target_file = key.split('#')[0].split('/')[-1]
        function_name = key.split('#')[1]
        line_num = int(key.split('#')[-1])

        # split key to target_file, function_name, line_num (individual column)
        mbfl_features_df.at[index, 'target_file'] = target_file
        mbfl_features_df.at[index, 'function_name'] = function_name
        mbfl_features_df.at[index, 'line_num'] = line_num

        # check if the row is one of the buggy lines of the buggy function
        if target_file == buggy_target_file and function_name == buggy_function_name:
            mbfl_features_df.at[index, 'bug'] = 1
        else:
            mbfl_features_df.at[index, 'bug'] = 0
    

    # 2. DROP THE KEY COLUMN
    mbfl_features_df = mbfl_features_df.drop(columns=['key'])
    mbfl_features_df = mbfl_features_df[[
        'target_file', 'function_name', 'line_num',
        'met_1', 'met_2', 'met_3', 'met_4',
        'muse_1', 'muse_2', 'muse_3', 'muse_4', 'muse_5', 'muse_6',
        'bug'
    ]]


    # 3. GROUP ROWS BY THE SAME FUNCTION NAME AND
    # APPLY THE VALUE OF THE LINE WITH THE HIGHEST MUSE_6 SCORE
    mbfl_features_df = mbfl_features_df.groupby(
        ['target_file', 'function_name']).apply(
            lambda x: x.nlargest(1, formula)
        ).reset_index(drop=True)
    

    # 4. SORT THE ROWS BY THE FORMULA VALUE
    mbfl_features_df = mbfl_features_df.sort_values(by=[formula], ascending=False).reset_index(drop=True)

    
    # 5. ADD A RANK COLUMN TO THE DF
    # THE RANK IS BASED ON FORMULA VALUE
    # IF THE RANK IS A TIE, THE RANK IS THE UPPER BOUND OF THE TIERS
    mbfl_features_df['rank'] = mbfl_features_df[formula].rank(method='max', ascending=False).astype(int)
    # sbfl_features_df.to_csv('ranked.csv', index=False)


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
        curr_score = row[formula]

        # assign the best rank number
        if curr_rank < best_rank:
            best_rank = curr_rank
            best_score = curr_score
        
        if curr_rank == best_rank:
            assert curr_score == best_score, f"score is not the same"


        # assign the rank of the buggy line
        if curr_target_file == buggy_target_file and \
            curr_function_name == buggy_function_name:
            bug_rank = curr_rank
            bug_score = curr_score
            assert row['bug'] == 1, f"bug is not 1"
        
    assert best_rank != 0, f"min_rank is 0"
    assert best_rank != sys.maxsize, f"min_rank is sys.maxsize"
    assert best_score is not None, f"best_score is None"

    assert bug_rank != -1, f"rank_bug is -1"
    assert bug_score is not None, f"bug_score is None"

    assert func_n == total_num_of_func, f"func_n != total_num_of_func"

    # print(formula, best_rank, best_score, bug_rank, bug_score)
    data = {
        f'total # of functions': total_num_of_func,
        f'# of functions with same highest {formula} score': best_rank,
        f'{formula} score of highest rank': best_score,
        f'rank of buggy function ({formula}, functino level)': bug_rank,
        f'{formula} score of buggy function': bug_score
    }
    return data

def start_program(mbfl_dataset_dir_name):
    mbfl_dataset_dir = root_dir / 'mbfl_datasets' / mbfl_dataset_dir_name
    assert mbfl_dataset_dir.exists(), f'{mbfl_dataset_dir} does not exist'

    bug_lists = []
    bug_ids = get_bugs(mbfl_dataset_dir)
    cnt = 0
    for bug_id in bug_ids:
        cnt += 1
        print(f"{cnt}: Processing {bug_id}")

        # get buggy line key
        buggy_line_key = get_buggy_line_key(mbfl_dataset_dir, bug_id)
        print(f"\tbuggy_line_key: {buggy_line_key}")

        # get lines executed by failing TCs dict {line key: [TCs]}
        lines_by_failing_TCs = get_lines_by_failing_TCs(mbfl_dataset_dir, bug_id)

        # 1. validate that buggy line key is in lines by failing TCs
        assert buggy_line_key in lines_by_failing_TCs, f'{buggy_line_key} not in lines_by_failing_TCs'

        # get failing TCs
        failing_TCs = get_failing_TCs(mbfl_dataset_dir, bug_id)

        # 2. validate that all failing TCs execute the buggy line
        for tc_id in failing_TCs:
            assert tc_id in lines_by_failing_TCs[buggy_line_key], f'{tc_id} does not execute the buggy line'
        
        # get mutant data
        mutant_data = get_mutant_data(mbfl_dataset_dir, bug_id, buggy_line_key)
        assert mutant_data['number_of_mutants_on_buggy_line'] == mutant_data['number_of_uncompilable_mutants_on_buggy_line'] + mutant_data['number_of_compilable_mutants_on_buggy_line']

        # get total p2f and f2p
        total_p2f, total_f2p = get_total_TC_results(mbfl_dataset_dir, bug_id)

        # get susp_scores
        susp_scores = get_susp_scores(mbfl_dataset_dir, bug_id, buggy_line_key)
        assert susp_scores is not None

        # get rank
        formulas = ['met_4', 'muse_6']
        ranks = {}
        for formula in formulas:
            rank_data = get_rank_at_method_level(mbfl_dataset_dir, bug_id, buggy_line_key, formula)
            ranks[formula] = rank_data
            # data = {
            #     f'total # of functions': total_num_of_func,
            #     f'# of functions with same highest {formula} score': best_rank,
            #     f'{formula} score of highest rank': best_score,
            #     f'rank of buggy function ({formula}, functino level)': bug_rank,
            #     f'{formula} score of buggy function': bug_score
            # }
        
        assert ranks['met_4']['total # of functions'] == ranks['muse_6']['total # of functions']
        print(f"\tmet_4 rank: {ranks['met_4']['rank of buggy function (met_4, functino level)']}")
        print(f"\tmuse_6 rank: {ranks['muse_6']['rank of buggy function (muse_6, functino level)']}")
        
        # append to bug_lists
        bug_lists.append({
            'bug_id': bug_id,
            'buggy_line_key': buggy_line_key,

            '# of failing TCs': len(failing_TCs),

            '# of lines executed by failing TCs': len(lines_by_failing_TCs),
            '# of mutants': mutant_data['number_of_mutants'],
            '# of uncompilable mutants': mutant_data['number_of_uncompilable_mutants'],

            '# of mutants on buggy line': mutant_data['number_of_mutants_on_buggy_line'],
            '# of uncompilable mutants on buggy line': mutant_data['number_of_uncompilable_mutants_on_buggy_line'],
            '# of compilable mutants on buggy line': mutant_data['number_of_compilable_mutants_on_buggy_line'],

            'total p2f (all mutants of bug version)': total_p2f,
            'total f2p (all mutants of bug version)': total_f2p,

            '# of functions': ranks['met_4']['total # of functions'],
            '# of functions with same highest met_4 score': ranks['met_4']['# of functions with same highest met_4 score'],
            'met_4 score of highest rank': ranks['met_4']['met_4 score of highest rank'],
            'rank of buggy function (met_4, function level)': ranks['met_4']['rank of buggy function (met_4, functino level)'],
            'met_4 score of buggy function': ranks['met_4']['met_4 score of buggy function'],

            '# of functions with same highest muse_6 score': ranks['muse_6']['# of functions with same highest muse_6 score'],
            'muse_6 score of highest rank': ranks['muse_6']['muse_6 score of highest rank'],
            'rank of buggy function (muse_6, function level)': ranks['muse_6']['rank of buggy function (muse_6, functino level)'],
            'muse_6 score of buggy function': ranks['muse_6']['muse_6 score of buggy function'],
        })
    
    # write to csv
    file = mbfl_dataset_dir / 'rank_summary.csv'
    with open(file, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=bug_lists[0].keys())
        writer.writeheader()
        for data in bug_lists:
            writer.writerow(data)


if __name__ == "__main__":
    mbfl_dataset_dir_name = sys.argv[1]
    start_program(mbfl_dataset_dir_name)


