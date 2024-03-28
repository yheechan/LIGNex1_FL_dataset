#!/usr/bin/python3

import subprocess as sp
from pathlib import Path
import csv

script_path = Path(__file__).resolve()
bin_dir = script_path.parent
main_dir = bin_dir.parent
root_dir = main_dir.parent

def merge2func():
    pp_csv = main_dir / 'output/pp_data-v1.csv'
    unwanted = ['jsontestrunner', 'test_lib_json', 'CMakeFiles']
    checked = ['jsontestrunner', 'test_lib_json', 'json', 'lib_json', 'CMakeFiles']
    func_cov_dict = {}
    
    with open(pp_csv, 'r') as f:
        reader = csv.reader(f)
        next(reader)

        for row in reader:
            assert len(row) == 128, f'Expected 128 columns, got {len(row)}'
            key = row[0]
            key_info = key.split('#')
            target_file = key_info[0]
            function_name = key_info[1]
            line_number = key_info[2]

            # skip unwanted files
            target_dir = target_file.split('/')[1]
            assert target_dir in checked, f'{target_dir} not in {checked}'
            if target_dir in unwanted:
                continue

            func_key = '{}#{}'.format(target_file, function_name)

            # initiate the tc2func for target function
            if func_key not in func_cov_dict.keys():
                func_cov_dict[func_key] = row[1:]
                assert len(func_cov_dict[func_key]) == 127, f'Expected 127 columns, got {len(func_cov_dict[func_key])}'
            else:
                # if initiated
                # overwrite the coverage data
                # when the TC covers the function
                for i in range(1, 128):
                    if row[i] == '1':
                        func_cov_dict[func_key][i-1] = '1'
    
    col_data = ['key']
    for i in range(1, 128):
        col_data.append('TC{}'.format(i))
    
    with open(main_dir / 'output/pp_data-v2.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(col_data)
        
        for key in func_cov_dict.keys():
            row = [key]
            row.extend(func_cov_dict[key])
            writer.writerow(row)


if __name__ == '__main__':
    merge2func()
