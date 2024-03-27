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

            print(key)
            
            cnt = 0
            for tc_id in row[1:]:
                cnt += 1
                print('{} {}'.format(cnt, tc_id))

            break


if __name__ == '__main__':
    merge2func()