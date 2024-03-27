#!/usr/bin/python3

import subprocess as sp
from pathlib import Path
import json

script_path = Path(__file__).resolve()
bin_dir = script_path.parent
main_dir = bin_dir.parent
root_dir = main_dir.parent

def get_line2func_from_json():
    line2function_json = main_dir / 'output/line2function_data/line2function.json'
    assert line2function_json.exists(), f'{line2function_json} does not exist'
    
    json_data = {}
    with open(line2function_json, 'r') as json_file:
        json_data = json.load(json_file)
    return json_data

def get_test_suite_from_file():
    output_dir = main_dir / 'output'
    assert output_dir.exists(), f'{output_dir} does not exist'
    ts_dir = output_dir / 'test_suite'
    assert ts_dir.exists(), f'{ts_dir} does not exist'
    ts_path = ts_dir / 'test_suite.csv'
    assert ts_path.exists(), f'{ts_path} does not exist'
    # +++++++++++++++++++++++++++++++++++++++++++++

    ts_dict = {}
    with ts_path.open() as f:
        lines = f.readlines()
        for line in lines[1:]:
            tc_id, tc_name = line.strip().split(',')
            assert tc_id not in ts_dict, f'{tc_id} already exists in test suite'
            ts_dict[tc_id] = tc_name
    
    assert len(ts_dict.keys()) == 127, f'Expected 127 test cases, got {len(ts_dict.keys())}'
    return ts_dict

def return_fuction(fname, lnum, line2function_dict):
    endName = fname.split('/')[-1]
    useName = endName if endName == 'CMakeCXXCompilerId.cpp' else fname

    if useName in line2function_dict.keys():
        for funcData in line2function_dict[useName]:
            funcName = funcData[0]
            funcStart = funcData[1]
            funcEnd = funcData[2]

            if lnum >= funcStart and lnum <= funcEnd:
                return funcName
    return 'FUNCTIONNOTFOUND'

def add_key_data(cov_data, cov_json, line2func_dict):
    cov_data['col_data'].append('key')

    cnt = 0
    for file in cov_json['files']:
        filename = file['file']

        for line in file['lines']:
            line_number = line['line_number']
            function_name = return_fuction(filename, line_number, line2func_dict)
            row_name = filename+'#'+function_name+'#'+str(line_number)

            assert [row_name] not in cov_data['row_data'], f'{row_name} already exists in row data'
            if [row_name] not in cov_data['row_data']:
                cov_data['row_data'].append([row_name])
                cnt += 1
    # print('Added {} keys'.format(cnt))
    return cnt

def add_cov_of_tc(cov_data, cov_json, tc_id):
    cov_data['col_data'].append(tc_id)

    cnt = 0
    for file in cov_json['files']:
        filename = file['file']

        for i in range(len(file['lines'])):
            line = file['lines'][i]
            line_number = line['line_number']
            function_name = return_fuction(filename, line_number, line2func_dict)
            row_name = filename+'#'+function_name+'#'+str(line_number)

            assert row_name == cov_data['row_data'][cnt][0], f'{row_name} != {cov_data["row_data"][cnt][0]}'

            covered = 1 if line['count'] > 0 else 0
            cov_data['row_data'][cnt].append(covered)

            cnt += 1
    
    # print('Added {} coverage data for {}'.format(cnt, tc_id))
    return cnt

def write_postprocessed_data(cov_data):
    pp_data_csv = main_dir / 'output/pp_data-v1.csv'
    with pp_data_csv.open('w') as f:
        f.write(','.join(cov_data['col_data']) + '\n')

        for row in cov_data['row_data']:
            cnt = 0
            for cell in row:
                if cnt == 0:
                    f.write('\"{}\"'.format(cell))
                else:
                    f.write(',' + str(cell))
                cnt += 1
            f.write('\n')
    return

def start_postprocess(line2func_dict, ts_dict):
    cov_per_tc_dir = main_dir / 'output/coverage/coverage_per_tc'

    first = True
    cov_data = {
        'col_data': [],
        'row_data': []
    }
    tot_keys_cnt = -1
    for tc_id, tc_name in ts_dict.items():
        print(f'Processing {tc_id} - {tc_name}')

        cov_file_name = '{}.cov.json'.format(tc_id)
        cov_file_path = cov_per_tc_dir / cov_file_name
        cov_file_fp = open(cov_file_path, 'r')
        cov_json = json.load(cov_file_fp)
        cov_file_fp.close()

        if first:
            tot_key_cnt = add_key_data(cov_data, cov_json, line2func_dict)
            first = False
        
        coved_key_cnt = add_cov_of_tc(cov_data, cov_json, tc_id)
        assert tot_key_cnt == coved_key_cnt, f'{tot_key_cnt} != {coved_key_cnt}'
    
    write_postprocessed_data(cov_data)


if __name__ == '__main__':
    line2func_dict = get_line2func_from_json()
    ts_dict = get_test_suite_from_file()
    start_postprocess(line2func_dict, ts_dict)
