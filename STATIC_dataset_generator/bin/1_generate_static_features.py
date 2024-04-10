#!/usr/bin/python3

from pathlib import Path
import sys
import subprocess as sp
import csv


script_path = Path(__file__).resolve()
bin_dir = script_path.parent
main_dir = bin_dir.parent
root_dir = main_dir.parent

metrix_py = '\"/home/yangheechan/metrixplusplus/metrix++.py\"'

# example of getting static information
# python "/home/yangheechan/metrixplusplus/metrix++.py" collect --std.code.lines.code -- json_valueiterator.cpp
# python "/home/yangheechan/metrixplusplus/metrix++.py" view -- json_valueiterator.cpp
# python "/home/yangheechan/metrixplusplus/metrix++.py" export --db-file=metrixpp.db > tmp.csv

features_list = [
    '--std.general.size',
    '--std.code.length.total',
    '--std.code.filelines.total',
    '--std.code.lines.total',
    '--std.code.filelines.code',
    '--std.code.lines.code',
    '--std.code.filelines.preprocessor',
    '--std.code.lines.preprocessor',
    '--std.code.filelines.comments',
    '--std.code.lines.comments',
    '--std.code.ratio.comments',
    '--std.code.complexity.cyclomatic',
    '--std.code.complexity.cyclomatic_switch_case_once',
    '--std.code.complexity.maxindent',
    '--std.code.magic.numbers',
    '--std.code.todo.comments',
    '--std.general.proctime',
    '--std.suppress',
    '--std.general.procerrors',
    '--std.code.maintindex.simple'
]

metrix_features = ' '.join(features_list)

def change_inl2cpp(target_file):
    filename = target_file.name.split('/')[-1].split('.')[0]
    new_filename = filename+'.cpp'
    new_target_file = target_file.parent / new_filename

    sp.run(f"cp {target_file} {new_target_file}", shell=True)

    return new_target_file


def change_cpp2inl(csv_file):
    
    new_rows = []
    with open(csv_file, 'r') as f:
        csvreader = csv.reader(f)

        fields = next(csvreader)

        for row in csvreader:
            filename = row[0]
            without_ext = ''.join(filename.split('.')[:-1])
            row[0] = '.'+without_ext+'.inl'
            
            new_rows.append(row)
        
    with open(csv_file, 'w') as f:
        header = ','.join(fields)
        f.write(header+'\n')

        for row in new_rows:
            row_str = ','.join(row)
            f.write(row_str+'\n')
    
    old_filename = csv_file.name
    first_seg = old_filename.split('.')[0]
    second_seg = '.'.join(old_filename.split('.')[2:])
    new_filename = first_seg + '.inl.' + second_seg
    new_csvfile = csv_file.parent / new_filename
    
    sp.run(f"mv {csv_file} {new_csvfile}", shell=True)


def get_static_features(dataset_dir, target_file):
    extension = target_file.name.split('.')[-1]
    if extension == 'inl':
        target_file = change_inl2cpp(target_file)
    
    target_filename = target_file.name
    file_path = target_file.parent
    
    # measure static feature data with metrix
    sp.run(f"python {metrix_py} collect {metrix_features} -- {target_file.name}", shell=True, cwd=file_path)

    db_file = bin_dir / 'metrixpp.db'
    csv_filename = f"{target_filename}.static_features.csv"
    csv_file = dataset_dir / csv_filename

    # save static feature to csv file
    sp.run(f"python {metrix_py} export --db-file={db_file.name} > {csv_file}", shell=True, cwd=file_path)

    if extension == 'inl':
        change_cpp2inl(csv_file)
    


def start_program(dataset_name, json_template_name):
    dataset_dir = root_dir / 'static_datasets' / dataset_name
    if not dataset_dir.exists():
        dataset_dir.mkdir()
    else:
        sp.run(f"rm -rf {dataset_dir}", shell=True)
        dataset_dir.mkdir()
    assert dataset_dir.exists(), f"{dataset_dir} does not exist"

    jsoncpp_dir = root_dir / json_template_name
    assert jsoncpp_dir.exists(), f"{jsoncpp_dir} does not exist"

    target_files = [
        "include/json/reader.h",
        "include/json/value.h",
        "include/json/writer.h",
        "src/lib_json/json_reader.cpp",
        "src/lib_json/json_tool.h",
        "src/lib_json/json_value.cpp",
        "src/lib_json/json_valueiterator.inl",
        "src/lib_json/json_writer.cpp",
    ]

    for target_file in target_files:
        target_file = jsoncpp_dir / target_file
        assert target_file.exists(), f"{target_file} does not exist"
        
        get_static_features(dataset_dir, target_file)

        # break


if __name__ == "__main__":
    dataset_name = sys.argv[1]
    json_template_name = sys.argv[2]

    start_program(dataset_name, json_template_name)