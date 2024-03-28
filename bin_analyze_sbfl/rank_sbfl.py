#!/usr/bin/python3

from pathlib import Path
import sys
import csv
import pandas as pd

script_path = Path(__file__).resolve()
bin_dir = script_path.parent
root_dir = bin_dir.parent

# Funciton to get the buggy line from spectrum csv
# (because buggy line information was not saved before when making SBFL data)
def get_buggy_line(spect_csv):
    assert spect_csv.exists(), f"{spect_csv} does not exist"
    with open(spect_csv, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            bug_stat = int(row[13])
            if bug_stat == 1:
                # (ex) bug1 # src/lib_json/json_writer.cpp $ valuetoString() # 95
                buggy_line_key = row[0]
                return buggy_line_key
    return None

def get_rank_at_method_level(spect_csv, buggy_line_key, formula):
    assert spect_csv.exists(), f"{spect_csv} does not exist"
    key_info = buggy_line_key.split('#')
    bug_version = key_info[0].strip()
    bug_target_file = key_info[1].strip()
    bug_function_name = key_info[2].strip()
    bug_line_num = int(key_info[3].strip())

    sbfl_features_df = pd.read_csv(spect_csv)

    # 1. SET ALL BUGGY LINE OF BUGGY FUNCTION TO BUG1
    for index, row in sbfl_features_df.iterrows():
        key = row['lineNo']
        curr_key_info = key.split('#')
        curr_version = curr_key_info[0].strip()
        curr_target_file = curr_key_info[1].strip()
        curr_function_name = curr_key_info[2].strip()
        curr_line_num = int(curr_key_info[3].strip())

        sbfl_features_df.at[index, 'target_file'] = curr_target_file
        sbfl_features_df.at[index, 'function_name'] = curr_function_name
        sbfl_features_df.at[index, 'line_num'] = curr_line_num

        # set all buggy lines of buggy function to bug 1
        if curr_target_file == bug_target_file and \
            curr_function_name == bug_function_name:
            sbfl_features_df.at[index, 'bug'] = 1
        else:
            sbfl_features_df.at[index, 'bug'] = 0

    # 2. DROP THE LINENO COLUMN
    sbfl_features_df.drop(columns=['lineNo'])
    sbfl_features_df = sbfl_features_df[[
        'target_file', 'function_name', 'line_num',
        'ep', 'ef', 'np', 'nf',
        'Binary', 'GP13', 'Jaccard', 'Naish1',
        'Naish2', 'Ochiai', 'Russel+Rao', 'Wong1',
        'bug'
    ]]
    # sbfl_features_df.to_csv('new1.csv', index=False)


    # 3. GROUP ROWS BY SAME FUNCTION NAME AND
    # APPLY VALUE OF THE LINE WITH THE HIGHEST VALUE OF THE FORMULA
    sbfl_features_df = sbfl_features_df.groupby(
        ['target_file', 'function_name']).apply(
            lambda x: x.nlargest(1, formula)
        ).reset_index(drop=True)
    # sbfl_features_df.to_csv('new2.csv', index=False)

    

    # 4. SORT THE ROWS BY THE FORMULA VALUE
    sbfl_features_df = sbfl_features_df.sort_values(by=[formula], ascending=False).reset_index(drop=True)
    # sbfl_features_df.to_csv('new3.csv', index=False)


    
    # 5. ADD A RANK COLUMN TO THE DF
    # THE RANK IS IN THE STANDARD OF FORMULA COLUMN
    # IF THE RANK IS A TIE, THE RANK IS THE UPPER BOUND OF THE TIE
    sbfl_features_df['rank'] = sbfl_features_df[formula].rank(ascending=False, method='max').astype(int)
    # sbfl_features_df.to_csv('new4.csv', index=False)

    
    # 6. GET THE RANK OF THE BUGGY LINE
    # AND THE MINIMUM RANK OF THE FORMULA
    # AND THE SCORE
    func_n = sbfl_features_df.shape[0]
    total_num_of_func = 0
    best_rank = sys.maxsize
    best_score = None
    bug_rank = -1
    bug_score = None
    for index, row in sbfl_features_df.iterrows():
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
        if curr_target_file == bug_target_file and \
            curr_function_name == bug_function_name:
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
        f'rank of buggy function ({formula})': bug_rank,
        f'{formula} score of buggy function': bug_score
    }
    return data

def rank_sbfl_dataset(sbfl_dataset, wanted_name):
    SBFL = [
        'Binary', 'GP13', 'Jaccard', 'Naish1',
        'Naish2', 'Ochiai', 'Russel+Rao', 'Wong1'
    ]
    result_list = []

    spectrum_dir = sbfl_dataset / 'spectrum_feature_data_excluding_coincidentally_correct_tc_per_bug'
    assert spectrum_dir.exists(), f"{spectrum_dir} does not exist"

    cnt = 0
    for spect_csv in spectrum_dir.iterdir():
        buggy_line_key = get_buggy_line(spect_csv)
        assert buggy_line_key is not None, f"buggy line not found in {spect_csv}"

        key_info = buggy_line_key.split('#')
        bug_version = key_info[0].strip()
        bug_target_file = key_info[1].strip().split('/')[-1]
        assert bug_target_file in ['json_reader.cpp', 'json_value.cpp'], f"bug_target_file is not json_reader.cpp or json_writer.cpp"
        bug_function_name = key_info[2].strip()
        bug_line_num = int(key_info[3].strip())

        cnt += 1
        print(cnt, buggy_line_key)

        ranks = {}
        for formula in SBFL:
            rank_data = get_rank_at_method_level(spect_csv, buggy_line_key, formula)
            ranks[formula] = rank_data
        

        write_data = {
            'bug_version': bug_version,
            'bug_target_file': bug_target_file,
            'bug_function_name': bug_function_name,
        }
        for formula in SBFL:
            for key, value in ranks[formula].items():
                write_data[key] = value
        # print(write_data)
                
        result_list.append(write_data)
    
        # cnt += 1
        # print(cnt, spect_csv.name, buggy_line_key, "==================")
        # if cnt == 3:
        #     break
    
    file_name = 'sbfl_rank_{}.csv'.format(wanted_name)
    with open(file_name, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=result_list[0].keys())
        writer.writeheader()
        writer.writerows(result_list)

        



if __name__ == "__main__":
    # this is the name of target sbfl dataset (ex. overall_24_02_20-v2)
    sbfl_dataset_dir_name = sys.argv[1]
    wanted_name = sys.argv[2]
    sbfl_dataset_dir = root_dir / 'sbfl_datasets' / sbfl_dataset_dir_name
    assert sbfl_dataset_dir.exists(), f"sbfl dataset {sbfl_dataset_dir} does not exist"

    rank_sbfl_dataset(sbfl_dataset_dir, wanted_name)
