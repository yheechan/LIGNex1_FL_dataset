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

    func_cov_dict = {}

    unwanted = ['jsontestrunner', 'test_lib_json', 'CMakeFils']
    
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

            unwanted_dir = target_file.split('/')[1]

            func_key = '{}#{}'.format(target_file, function_name)

            if func_key not in func_cov_dict.keys():
                func_cov_dict[func_key] = []
        
        print(len(func_cov_dict.keys()))


if __name__ == '__main__':
    merge2func()