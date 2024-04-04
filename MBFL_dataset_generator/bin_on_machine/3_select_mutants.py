#!/usr/bin/python3
import subprocess as sp
from pathlib import Path
import os
import sys
import random

script_path = Path(os.path.realpath(__file__))
bin_dir = script_path.parent
main_dir = bin_dir.parent

def get_lines_by_failing(core_dir):
    accepted_files = ['json_reader.cpp', 'json_value.cpp', 'json_writer.cpp']

    lines_by_failing_file = core_dir / 'prerequisite_data/coverage_data/lines_executed_by_failing_TC.txt'
    assert lines_by_failing_file.exists(), f'{lines_by_failing_file} does not exist'

    lines_by_failing_fp = open(lines_by_failing_file, 'r')
    lines = lines_by_failing_fp.readlines()
    lines_by_failing_fp.close()

    files_lines_dict = {}

    for line in lines:
        line = line.strip()
        info = line.split('$$')
        key = info[0]

        target_file = key.split('#')[0].split('/')[-1]
        lineNo = int(key.split('#')[-1])

        # only record accepted files: json_reader.cpp, json_value.cpp, json_writer.cpp
        if target_file not in accepted_files:
            continue

        if target_file not in files_lines_dict:
            files_lines_dict[target_file] = []
        # assert lineNo not in files_lines_dict[target_file]
            
        files_lines_dict[target_file].append(lineNo)
        # print(target_file, lineNo)
    
    return files_lines_dict

def select_mutants(core_dir, files_lines_dict, mutation_size=6):
    prohibited_mut_op = {
        "STRI",
        "DirVarAriNeg", "DirVarBitNeg", "DirVarLogNeg", "DirVarIncDec",
        "DirVarRepReq", "DirVarRepCon", "DirVarRepPar", "DirVarRepGlo", 
        "DirVarRepExt", "DirVarRepLoc", "IndVarAriNeg", "IndVarBitNeg", 
        "IndVarLogNeg", "IndVarIncDec", "IndVarRepReq", "IndVarRepCon", 
        "IndVarRepPar", "IndVarRepGlo", "IndVarRepExt", "IndVarRepLoc"
    }

    mutations_dir = core_dir / 'mutations'

    files_mutants_dict = {}
    total_mutants_cnt = 0
    for target_file in files_lines_dict.keys():
        
        # initiate dict for target_file2lineno
        if target_file not in files_mutants_dict:
            files_mutants_dict[target_file] = {}
            for lineNo in files_lines_dict[target_file]:
                files_mutants_dict[target_file]['line_{}'.format(lineNo)] = []
        
        # get mutation dir of target file
        file_mutations_dir = mutations_dir / target_file
        assert file_mutations_dir.exists(), f'{file_mutations_dir} does not exist'

        # get mutation db csv
        file_name = target_file.split('.')[0]
        csv_file_name = file_name + '_mut_db.csv'
        csv_file = file_mutations_dir / csv_file_name
        assert csv_file.exists(), f'{csv_file} does not exist'

        # read csv file
        csv_fp = open(csv_file, 'r')
        csv_lines = csv_fp.readlines()
        csv_fp.close()

        # remove first two lines of csv_lines
        csv_lines = csv_lines[2:]

        # shuffle csv_lines at random (inplace)
        random.shuffle(csv_lines)

        # select 6 mutants per executed lines per target file
        for line in csv_lines:
            # 0 Mutant Filename
            # 1 Mutation Operator
            # 2 Start Line#
            # 3 Start Col#
            # 4 End Line#
            # 5 End Col#
            # 6 Target Token
            # 7 Start Line#
            # 8 Start Col#
            # 9 End Line#
            # 10 End Col#
            # 11 Mutated Token
            # 12 Extra Info
            info = line.strip().split(',')
            mutant_filename = info[0]
            before_mutation = info[6]
            after_mutation = info[11]
            mutation_operator = info[1]


            # if the mutation operator is in prohibited_mut_op, skip
            if mutation_operator in prohibited_mut_op: continue

            # if the line number of original and mutant is different, skip
            start_line_og = int(info[2])
            start_line_mutant = int(info[7])
            if start_line_og != start_line_mutant: continue

            # if the line number is not executed by failing test case, skip
            line_key = 'line_{}'.format(start_line_og)
            if line_key not in files_mutants_dict[target_file]:
                continue

            # select the mutant if the number of selected mutant for this line is less than mutation_size
            if len(files_mutants_dict[target_file][line_key]) < mutation_size:
                files_mutants_dict[target_file][line_key].append({
                    'jsoncpp_source_code_file': target_file,
                    'line_number': start_line_og,
                    'mutant_filename': mutant_filename,
                    'mutation_operator': mutation_operator,
                    'before_mutation': before_mutation,
                    'after_mutation': after_mutation
                })
                total_mutants_cnt += 1
                # print(target_file, line_key, mutant_filename)
    
    print('Total mutants selected:', total_mutants_cnt)
    return files_mutants_dict

def custom_sort(mutant_dict):
    target_file = mutant_dict['jsoncpp_source_code_file']
    line_number = mutant_dict['line_number']
    mutant_file_name = mutant_dict['mutant_filename']
    file_number = int(mutant_file_name.split('.')[1][3:])
    return (target_file, line_number, file_number)

def sort_selected_mutants(selected_mutants):
    mutant_list = []
    for target_file in selected_mutants.keys():
        for line_key in selected_mutants[target_file].keys():
            for mutant in selected_mutants[target_file][line_key]:
                mutant_list.append(mutant)
    
    sorted_mutants = sorted(mutant_list, key=custom_sort)
    return sorted_mutants

def write_selcted_mutants(core_dir, selected_mutants):
    mbfl_data_dir = core_dir / 'mbfl_data'
    if not mbfl_data_dir.exists():
        os.mkdir(mbfl_data_dir)
    
    selected_mutants_dir = mbfl_data_dir / 'selected_mutants'
    if not selected_mutants_dir.exists():
        os.mkdir(selected_mutants_dir)
    
    selected_mutants_file = selected_mutants_dir / 'mutants_db.csv'
    with open(selected_mutants_file, 'w') as f:
        f.write('jsoncpp source code, line number, mutant id, mutant name (from MUSICUP), mutation operator, before mutation, after mutation\n')

        # sort selected_mutants by target_file, line_key, and mutants
        sorted_mutants = sort_selected_mutants(selected_mutants)

        cnt = 0
        for mutant in sorted_mutants:
            cnt += 1
            jsoncpp_source_code_file = mutant['jsoncpp_source_code_file']
            line_number = mutant['line_number']
            mutant_id = 'mutant_{}'.format(cnt)
            mutant_filename = mutant['mutant_filename']
            mutation_operator = mutant['mutation_operator']
            before_mutation = mutant['before_mutation']
            after_mutation = mutant['after_mutation']
            f.write(f'{jsoncpp_source_code_file},{line_number},{mutant_id},{mutant_filename},{mutation_operator},{before_mutation},{after_mutation}\n')


if __name__ == "__main__":
    core_id = sys.argv[1]
    mutation_size = int(sys.argv[2])
    core_dir = main_dir / core_id
    jsoncpp_dir = core_dir / 'jsoncpp_template'

    executed_lines_per_file_dict = get_lines_by_failing(core_dir)
    past_selected_mutants_per_file_dict = select_mutants(core_dir, executed_lines_per_file_dict, mutation_size=mutation_size)
    write_selcted_mutants(core_dir, past_selected_mutants_per_file_dict)
