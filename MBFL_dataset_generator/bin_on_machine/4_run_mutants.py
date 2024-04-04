#!/usr/bin/python3
import subprocess as sp
from pathlib import Path
import os
import sys

script_path = Path(os.path.realpath(__file__))
bin_dir = script_path.parent
main_dir = bin_dir.parent

def read_selected_mutants(core_dir):
    selected_mutants_file = core_dir / 'mbfl_data/selected_mutants/mutants_db.csv'
    assert selected_mutants_file.exists(), f'{selected_mutants_file} does not exist'

    selected_mutants_fp = open(selected_mutants_file, 'r')
    lines = selected_mutants_fp.readlines()
    selected_mutants_fp.close()

    selected_mutants = {}
    for line in lines[1:]:
        info = line.strip().split(',')
        # 0 jsoncpp source code file
        # 1 line number
        # 2 mutant id
        # 3 mutant name
        # 4 mutation operator
        # 5 before mutation
        # 6 after mutation
        target_file = info[0]
        line_key = 'line_{}'.format(info[1])

        if target_file not in selected_mutants:
            selected_mutants[target_file] = {}
        if line_key not in selected_mutants[target_file]:
            selected_mutants[target_file][line_key] = []
        
        selected_mutants[target_file][line_key].append({
            'target_file': info[0],
            'line_number': 'line_{}'.format(info[1]),
            'mutant_id': info[2],
            'mutant_name': info[3],
        })
    
    return selected_mutants

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

def copy_buggy_version_code_files(core_dir):
    # target files
    target_files = ['json_reader.cpp', 'json_value.cpp', 'json_writer.cpp']

    # copy buggy_version jsoncpp to jsoncpp_template
    buggy_version_code_files_dir = core_dir / 'buggy_version_code_files'
    template_lib_jsoncpp_dir = core_dir / 'jsoncpp_template/src/lib_json'

    # copy target files in original lib to template lib
    for target_file in target_files:
        buggy_target_file = buggy_version_code_files_dir / target_file
        assert buggy_target_file.exists(), f'{buggy_target_file} does not exist'

        template_target_file = template_lib_jsoncpp_dir / target_file
        assert template_target_file.exists(), f'{template_target_file} does not exist'

        res = sp.run(['cp', buggy_target_file, template_target_file])
        if res.returncode != 0:
            print(f'Failed to copy {buggy_target_file} to {template_target_file}')
            exit(1)

def copy_mutant2template(core_dir, target_file, mutant, mutant_dir):
    # copy mutant to template lib
    template_lib_jsoncpp_dir = core_dir / 'jsoncpp_template/src/lib_json'

    template_target_file = template_lib_jsoncpp_dir / target_file
    assert template_target_file.exists(), f'{template_target_file} does not exist'

    mutant_file = core_dir / 'mutations' / target_file / mutant
    assert mutant_file.exists(), f'{mutant_file} does not exist'

    # copy the mutant file to the template file
    res = sp.run(['cp', mutant_file, template_target_file])
    if res.returncode != 0:
        print(f'Failed to copy {mutant_file} to {template_target_file}')
        exit(1)
    
    # make a copy of the mutant file to the mutant dir
    mutant_src_dir = mutant_dir / 'mutant_source_code'
    if not mutant_src_dir.exists():
        os.makedirs(mutant_src_dir)
    
    mutant_src = mutant_src_dir / target_file
    res = sp.run(['cp', mutant_file, mutant_src])
    if res.returncode != 0:
        print(f'Failed to copy {mutant_file} to {mutant_src}')
        exit(1)

def check_jsoncpp_tester(build_dir):
    jsoncpp_tester = build_dir / 'src/test_lib_json/jsoncpp_test'
    assert jsoncpp_tester.exists(), f'{jsoncpp_tester} does not exist'
    
    cmd = [jsoncpp_tester, '--list-tests']
    process = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE, encoding='utf-8')

    tc_dict = {}
    tc_cnt = 1
    while True:
        line = process.stdout.readline()
        if line == '' and process.poll() is not None:
            break
        line = line.strip()
        if line == '':
            continue
        
        tc_dict['TC{}'.format(tc_cnt)] = line
        tc_cnt += 1
    
    if len(tc_dict) != 127:
        return -1
    
    return 0

def build_mutated_jsoncpp(core_dir, mutant_dir):
    build_res = 'build-success'
    res_num = 0

    build_dir = core_dir / 'jsoncpp_template' / 'build'
    assert build_dir.exists(), f'{build_dir} does not exist'

    cmd = ['make', '-j20']
    res = sp.run(cmd, cwd=build_dir)
    if res.returncode != 0:
        build_res = 'build-failed'
        res_num = 1
    
    jsoncpp_tester = check_jsoncpp_tester(build_dir)
    if jsoncpp_tester != 0:
        build_res = 'build-failed'
        res_num = 1

    # echo build_res string to build_result.txt
    cmd = f'echo {build_res} > build_result.txt'
    res = sp.run(cmd, shell=True, cwd=mutant_dir)
    if res.returncode != 0:
        print(f'Failed to write build result to {mutant_dir / "build_result.txt"}')
        exit(1)
    
    return res_num

def run_test_suite_on_mutant(core_dir, tc_dict, mutant_dir, tc_changes):
    # run the test cases
    jsoncpp_test_exe = core_dir / 'jsoncpp_template/build/src/test_lib_json/jsoncpp_test'
    mutant_failed_tc = {}
    mutant_passed_tc = {}

    # initiate file to save test case results
    testcase_info_dir = mutant_dir / 'testcase_info'
    if not testcase_info_dir.exists():
        os.makedirs(testcase_info_dir)
    
    failing_csv = testcase_info_dir / 'failing_testcases.csv'
    failing_fp =  open(failing_csv, 'w')
    failing_fp.write('tc_id,tc_name\n')
    passing_csv = testcase_info_dir / 'passing_testcases.csv'
    passing_fp =  open(passing_csv, 'w')
    passing_fp.write('tc_id,tc_name\n')

    # initiate for overall results
    tc_result_csv = mutant_dir / 'mutant_tc_results.csv'
    tc_result_fp = open(tc_result_csv, 'w')
    tc_result_fp.write('p2f,f2p,p2p,f2f\n')
    p2f = 0
    f2p = 0
    p2p = 0
    f2f = 0

    for tc_type in tc_dict.keys():
        type_name = tc_type.split('_')[0]
        # print(f'Running {type_name} test cases')

        for tc_info in tc_dict[tc_type]:
            tc_id = tc_info[0]
            tc_name = tc_info[1]

            # print(f'Running {tc_id} : {tc_name}')
            cmd = ['timeout', '2s', jsoncpp_test_exe, '--test', tc_name]
            res = sp.call(cmd, stdout=sp.PIPE, stderr=sp.STDOUT, encoding='utf-8')
            if res != 0: # when it fails
                failing_fp.write(f'{tc_id},{tc_name}\n')
                mutant_failed_tc[tc_id] = tc_name

                if type_name == 'passing': # when it is originally passing
                    tc_changes['p2f'] += 1
                    p2f += 1
                    # print(f'Test originally passed > failed: {tc_id} {tc_name}')
                else:
                    f2f += 1
            else: # when it passes
                passing_fp.write(f'{tc_id},{tc_name}\n')
                mutant_passed_tc[tc_id] = tc_name
                
                if type_name == 'failing': # when it is originally failing
                    tc_changes['f2p'] += 1
                    f2p += 1
                    # print(f'Test originally failed > passed: {tc_id} {tc_name}')
                else:
                    p2p += 1
    
    failing_fp.close()
    passing_fp.close()
    tc_result_fp.write(f'{p2f},{f2p},{p2p},{f2f}\n')
    tc_result_fp.close()


def begin_program(core_dir, selected_mutants, tc_dict):
    per_mutant_dir = core_dir / 'mbfl_data/per_mutant_data'
    if not per_mutant_dir.exists():
        os.makedirs(per_mutant_dir)
    
    tc_changes = {
        'p2f': 0,
        'f2p': 0
    }
    # run test cases for each mutant
    for target_file in selected_mutants.keys():
        # copy original jsoncpp to jsoncpp_template
        copy_buggy_version_code_files(core_dir)

        # for each line of a target file
        for line_key in selected_mutants[target_file].keys():
            
            # for each mutant of a line
            for mutant_dict in selected_mutants[target_file][line_key]:
                target_src_file = mutant_dict['target_file']
                assert target_src_file == target_file, f'{target_src_file} != {target_file}'

                line_number = mutant_dict['line_number']
                mutant_id = mutant_dict['mutant_id']
                mutant_name = mutant_dict['mutant_name']

                # make individual directory for each mutant
                mutant_dir = per_mutant_dir / mutant_id
                if not mutant_dir.exists():
                    os.makedirs(mutant_dir)
                
                # copy mutant to template lib
                copy_mutant2template(core_dir, target_src_file, mutant_name, mutant_dir)

                # build with new mutant
                res = build_mutated_jsoncpp(core_dir, mutant_dir)
                if res != 0:
                    print('Failed to build on {}'.format(mutant_name))
                    continue

                # run the test cases
                run_test_suite_on_mutant(core_dir, tc_dict, mutant_dir, tc_changes)
    
    tc_results = core_dir / 'mbfl_data/total_tc_results.csv'
    tc_results_fp = open(tc_results, 'w')
    tc_results_fp.write('p2f,f2p\n')
    tc_results_fp.write(f'{tc_changes["p2f"]},{tc_changes["f2p"]}\n')
    tc_results_fp.close()

if __name__ == "__main__":
    core_id = sys.argv[1]
    core_dir = main_dir / core_id
    jsoncpp_dir = core_dir / 'jsoncpp_template'

    selected_mutants = read_selected_mutants(core_dir)
    tc_dict = get_tc_dict(core_dir)
    begin_program(core_dir, selected_mutants, tc_dict)


