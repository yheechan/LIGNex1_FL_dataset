#!/usr/bin/python3
import subprocess as sp
from pathlib import Path
import os
import sys
import time

script_file_path = Path(os.path.realpath(__file__))
bin_dir = script_file_path.parent
main_dir = bin_dir.parent

initial_build = bin_dir / '1_initial_build.py'
gen_mutations = bin_dir / '2_gen_mutations.py'
select_mutants = bin_dir / '3_select_mutants.py'
run_mutants = bin_dir / '4_run_mutants.py'
measure_mbfl_features = bin_dir / '5_measure_mbfl_features.py'

def initial_build_exec(core_id):
    # 1. initial build
    cmd = [initial_build, core_id]
    begin_time = time.time()
    print('0. start initial build')
    res = sp.call(cmd, cwd=bin_dir, stdout=sp.DEVNULL, stderr=sp.DEVNULL)

    if res != 0:
        curr_time = time.time()
        print('[{} {:.2f} secs] - Failed initial build: {}'.format(core_id, curr_time - begin_time, res))
        sys.exit(1)
    
    curr_time = time.time()
    print('[{} {:.2f} secs] - Success initial build: {}'.format(core_id, curr_time - begin_time, res))

def gen_mutations_exec(core_id, l_cnt):
    # 2. generate mutations
    cmd = [gen_mutations, core_id, l_cnt]
    begin_time = time.time()
    print('1. start generate mutations')
    res = sp.call(cmd, cwd=bin_dir, stdout=sp.DEVNULL, stderr=sp.DEVNULL)

    if res != 0:
        curr_time = time.time()
        print('[{} {:.2f} secs] - Failed generate mutations: {}'.format(core_id, curr_time - begin_time, res))
        sys.exit(1)
    
    curr_time = time.time()
    print('[{} {:.2f} secs] - Success generate mutations: {}'.format(core_id, curr_time - begin_time, res))

def select_mutants_exec(core_id, mutation_size):
    # 3. select mutants
    cmd = [select_mutants, core_id, mutation_size]
    begin_time = time.time()
    print('2. start select mutants')
    res = sp.call(cmd, cwd=bin_dir, stdout=sp.DEVNULL, stderr=sp.DEVNULL)

    if res != 0:
        curr_time = time.time()
        print('[{} {:.2f} secs] - Failed select mutants: {}'.format(core_id, curr_time - begin_time, res))
        sys.exit(1)
    
    curr_time = time.time()
    print('[{} {:.2f} secs] - Success select mutants: {}'.format(core_id, curr_time - begin_time, res))

def run_mutants_exec(core_id):
    # 4. run mutants
    cmd = [run_mutants, core_id]
    begin_time = time.time()
    print('3. start run mutants')
    res = sp.call(cmd, cwd=bin_dir, stdout=sp.DEVNULL, stderr=sp.DEVNULL)

    if res != 0:
        curr_time = time.time()
        print('[{} {:.2f} secs] - Failed run mutants: {}'.format(core_id, curr_time - begin_time, res))
        sys.exit(1)
    
    curr_time = time.time()
    print('[{} {:.2f} secs] - Success run mutants: {}'.format(core_id, curr_time - begin_time, res))

def measure_mbfl_features_exec(core_id):
    # 5. measure mbfl features
    cmd = [measure_mbfl_features, core_id]
    begin_time = time.time()
    print('4. start measure mbfl features')
    res = sp.call(cmd, cwd=bin_dir, stdout=sp.DEVNULL, stderr=sp.DEVNULL)

    if res != 0:
        curr_time = time.time()
        print('[{} {:.2f} secs] - Failed measure mbfl features: {}'.format(core_id, curr_time - begin_time, res))
        sys.exit(1)
    
    curr_time = time.time()
    print('[{} {:.2f} secs] - Success measure mbfl features: {}'.format(core_id, curr_time - begin_time, res))


if __name__ == "__main__":
    core_id = sys.argv[1]
    mutation_size = sys.argv[2]
    l_cnt = sys.argv[3]

    start_time = time.time()

    initial_build_exec(core_id)
    gen_mutations_exec(core_id, l_cnt)
    select_mutants_exec(core_id, mutation_size)
    run_mutants_exec(core_id)
    measure_mbfl_features_exec(core_id)

    end_time = time.time()
    print('Total time: {:.2f} secs'.format(end_time - start_time))
    