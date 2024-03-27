#!/usr/bin/python3

import subprocess as sp
from pathlib import Path
import sys
import json

script_path = Path(__file__).resolve()
bin_dir = script_path.parent
main_dir = bin_dir.parent
root_dir = main_dir.parent

clangPP = Path('/usr/bin/clang++-13')
extractor = root_dir / 'extractor/extractor'

def check_extractor():
    if not extractor.exists():
        extractor_dir = extractor.parent
        cmd = ['make', '-j20']
        res = sp.call(cmd, cwd=extractor_dir)
        if res != 0:
            print('Failed to build extractor')
            sys.exit(1)
    
    assert extractor.exists(), f'{extractor} does not exist'

# these are the ii files found in jsoncpp
# ./src/jsontestrunner/main.ii
# ./src/lib_json/json_value.ii
# ./src/lib_json/json_reader.ii
# ./src/lib_json/json_writer.ii
# ./src/test_lib_json/jsontest.ii
# ./src/test_lib_json/main.ii
# ./src/test_lib_json/fuzz.ii
# ./CMakeFiles/3.10.2/CompilerIdCXX/CMakeCXXCompilerId.ii
def get_ii_files(build_dir):
    cmd = ['find', '.', '-type', 'f', '-name', '*.ii']
    process = sp.Popen(cmd, cwd=build_dir, stdout=sp.PIPE, stderr=sp.STDOUT, encoding='utf-8')

    ii_files = []
    while True:
        line = process.stdout.readline()
        if line == '' and process.poll() is not None:
            break
        line = line.strip()
        if line == '':
            continue
        ii_files.append(line)
    return ii_files

# these are the cpp files changed from ii files
# ./src/jsontestrunner/main.ii.cpp
# ./src/lib_json/json_value.ii.cpp
# ./src/lib_json/json_reader.ii.cpp
# ./src/lib_json/json_writer.ii.cpp
# ./src/test_lib_json/jsontest.ii.cpp
# ./src/test_lib_json/main.ii.cpp
# ./src/test_lib_json/fuzz.ii.cpp
# ./CMakeFiles/3.10.2/CompilerIdCXX/CMakeCXXCompilerId.ii.cpp
def ii2cpp(build_dir, ii_files):
    cmd = ['mv']
    cpp_files = []

    # if not yet changed
    if len(ii_files) != 0:
        for file in ii_files:
            cmd.append(file)
            cpp_file_name = file+'.cpp'
            cmd.append(cpp_file_name)

            res = sp.call(cmd, cwd=build_dir)
            if res != 0:
                print('Failed to rename {} to {}'.format(file, cpp_file_name))
                exit(1)
            cpp_files.append(cpp_file_name)

            cmd.pop()
            cmd.pop()
    else:
        cmd = ['find', '.', '-type', 'f', '-name', '*ii.cpp']
        process = sp.Popen(cmd, cwd=build_dir, stdout=sp.PIPE, stderr=sp.STDOUT, encoding='utf-8')

        while True:
            line = process.stdout.readline()
            if line == '' and process.poll() is not None:
                break
            line = line.strip()
            if line == '':
                continue
            cpp_files.append(line)
    return cpp_files

def extract_line2function(build_dir, cpp_files):
    check_extractor()
    cmd = [extractor]

    perFile_data = {}
    for file in cpp_files:
        file_path = Path(file)
        target_cpp = build_dir / file_path
        cmd.append(target_cpp)

        process = sp.Popen(
            cmd, stdout=sp.PIPE, stderr=sp.STDOUT,
            encoding='utf-8'
        )

        while True:
            line = process.stdout.readline()
            if line == '' and process.poll() != None:
                break
            line = line.strip()
            if line == '':
                continue

            data = line.split("##")
            # print("class: \t{}".format(data[0]))
            class_name = data[0]
            # print("function: \t{}".format(data[1]))
            function_name = data[1]
            # print("start line: \t{}".format(data[2]))
            start_line = data[2]
            # print("end line: \t{}".format(data[3]))
            end_line = data[3]
            # print("origin file: \t{}".format(data[4]))
            originated_file = data[4]

            file_data = originated_file.split(':')[0]
            route_data = file_data.split('/')
            mark = 0
            for i in range(len(route_data)-1, -1, -1):
                if route_data[i] in ['src', 'build', 'include']:
                    mark = i
                    break
                # if route_data[i] in ['a']:
                #     mark = i
                #     break
            marked_path = '/'.join(route_data[mark:])
            # print("marked file: {}".format(marked_path))
            # print("targeted file: \t{}".format(data[5]))
            # print("***************\n")


            if not marked_path in perFile_data.keys():
                perFile_data[marked_path] = []
            
            full_function = class_name+'::'+function_name if class_name != 'None' else function_name
            data = (full_function, int(start_line), int(end_line))
            if not data in perFile_data[marked_path]:
                perFile_data[marked_path].append(data)
        
        print('>> extracted line2function from {}'.format(file))
        cmd.pop()
    
    return perFile_data

def write_line2function(perFile_line2function_data):
    output_dir = main_dir / 'output'
    if not output_dir.exists():
        output_dir.mkdir()
    line2function_dir = output_dir / 'line2function_data'
    if not line2function_dir.exists():
        line2function_dir.mkdir()
    
    file_name = 'line2function.json'
    file = line2function_dir / file_name
    with open(file, 'w') as line2function_fp:
        json.dump(perFile_line2function_data, line2function_fp, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: 1_make_template.py <template_name>')
        sys.exit(1)

    template_name = sys.argv[1]
    project_dir = root_dir / template_name
    assert project_dir.exists(), f'{project_dir} does not exist'
    build_dir = project_dir / 'build'

    ii_files = get_ii_files(build_dir)
    cpp_files = ii2cpp(build_dir, ii_files)
    perFile_line2function_data = extract_line2function(build_dir, cpp_files)
    write_line2function(perFile_line2function_data)

