#!/usr/bin/python3

import sys
from pathlib import Path
import subprocess as sp
import argparse
import csv

script_path = Path(__file__).resolve()
bin_dir = script_path.parent
root_dir = bin_dir.parent

def return_parser():
    parser = argparse.ArgumentParser(description='Combine FL scores')
    parser.add_argument(
        "-sbfl", "--sbfl",
        help="Directory name to target SBFL dataset",
        required=True,
        default=None
    )
    parser.add_argument(
        "-mbfl", "--mbfl",
        help="Directory name to target MBFL dataset",
        required=True,
        default=None
    )
    parser.add_argument(
        "-fl", "--fl",
        help="Directory name to target FL dataset",
        required=True,
        default=None
    )
    return parser

def custome_sort(bug_dir):
    bug_name = bug_dir.name
    return int(bug_name[3:])

def get_bug_versions(path):
    buggy_code_file_dir = path / 'buggy_code_file_per_bug_version'
    assert buggy_code_file_dir.exists(), f"Error: {buggy_code_file_dir} does not exist"

    bug_versions = sorted(buggy_code_file_dir.iterdir(), key=custome_sort)
    bug_versions = [bug_version.name for bug_version in bug_versions]

    return bug_versions

def get_feature_file(path, bug_id, feature_dir, feature_ext):
    feature_dir = path / feature_dir
    assert feature_dir.exists(), f"Error: {feature_dir} does not exist"

    filename = f"{bug_id}{feature_ext}"
    feature_file = feature_dir / filename
    assert feature_file.exists(), f"Error: {feature_file} does not exist"

    return feature_file

def get_feature_per_line(feature_file):
    features_per_line = []
    with open(feature_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            features_per_line.append(row)
            # break

    return features_per_line


def write_fl_features(fl_feature_file, fl_features_per_line):
    with open(fl_feature_file, 'w') as f:
        fieldnames = [
            'key', 'ep', 'ef', 'np', 'nf',
            '# of totfailed_TCs', '# of mutants',
            'm1:f2p', 'm1:p2f', 'm2:f2p', 'm2:p2f', 'm3:f2p', 'm3:p2f',
            'm4:f2p', 'm4:p2f', 'm5:f2p', 'm5:p2f', 'm6:f2p', 'm6:p2f',
            'm7:f2p', 'm7:p2f', 'm8:f2p', 'm8:p2f', 'm9:f2p', 'm9:p2f',
            'm10:f2p', 'm10:p2f', 'm11:f2p', 'm11:p2f', 'm12:f2p', 'm12:p2f',
            'bug'
        ]

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in fl_features_per_line:
            filtered_row = {}
            for key in fieldnames:
                assert key in row, f"Error: {key} not in row"
                filtered_row[key] = row[key]
            
            writer.writerow(filtered_row)

def write_fl_features_with_susp_scores(fl_feature_file, fl_features_per_line):
    with open(fl_feature_file, 'w') as f:
        fieldnames = [
            'key', 'ep', 'ef', 'np', 'nf',
            '# of totfailed_TCs', '# of mutants',
            'm1:f2p', 'm1:p2f', 'm2:f2p', 'm2:p2f', 'm3:f2p', 'm3:p2f',
            'm4:f2p', 'm4:p2f', 'm5:f2p', 'm5:p2f', 'm6:f2p', 'm6:p2f',
            'm7:f2p', 'm7:p2f', 'm8:f2p', 'm8:p2f', 'm9:f2p', 'm9:p2f',
            'm10:f2p', 'm10:p2f', 'm11:f2p', 'm11:p2f', 'm12:f2p', 'm12:p2f',
            'bug',
            'muse susp. score', 'metallaxis susp. score'
        ]

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in fl_features_per_line:
            writer.writerow(row)


def start_program(sbfl, mbfl, fl):
    # check if the directory exists
    sbfl_path = root_dir / 'sbfl_datasets' / sbfl
    mbfl_path = root_dir / 'mbfl_datasets' / mbfl
    fl_path = root_dir / 'fl_datasets' / fl

    assert sbfl_path.exists(), f"Error: {sbfl} does not exist"
    assert mbfl_path.exists(), f"Error: {mbfl} does not exist"

    # initiate fl directory
    if fl_path.exists():
        sp.call(f"rm -rf {fl_path}", shell=True)
    fl_feature_dir = fl_path / 'FL_features_per_bug_version'
    fl_feature_dir.mkdir(parents=True, exist_ok=True)

    fl_feature_dir_with_susp_scores = fl_path / 'FL_features_per_bug_version_with_susp_scores'
    fl_feature_dir_with_susp_scores.mkdir(parents=True, exist_ok=True)

    # get the bug versions
    sbfl_bugs = get_bug_versions(sbfl_path)
    mbfl_bugs = get_bug_versions(mbfl_path)

    # VALIDATE that the number of bugs are the same
    assert len(sbfl_bugs) == len(mbfl_bugs), "Error: Number of bugs are not the same"

    cnt = 0

    # for each bug version
    for sbfl_bug, mbfl_bug in zip(sbfl_bugs, mbfl_bugs):
        # VALIDATE that the bug versions are the same
        assert sbfl_bug == mbfl_bug, "Error: Bug versions are not the same"

        # 1. current working bug_id
        bug_id = sbfl_bug
        fl_feature_file_name = f"{bug_id}.fl_features.csv"
        fl_feature_file = fl_feature_dir / fl_feature_file_name
        fl_feature_file_with_susp_scores_name = f"{bug_id}.fl_features_with_susp_scores.csv"
        fl_feature_file_with_susp_scores_file = fl_feature_dir_with_susp_scores / fl_feature_file_with_susp_scores_name

        cnt += 1
        print(f"{cnt}: processing {bug_id}")

        # 2. get the feature csv file
        sbfl_feature_file = get_feature_file(
            sbfl_path, bug_id,
            'sbfl_features_per_bug',
            '.sbfl_features.csv'
        )
        mbfl_feature_file = get_feature_file(
            mbfl_path, bug_id,
            'mbfl_features_per_bug_version',
            '.mbfl_features.csv'
        )

        # 3. get feature per lines
        sbfl_features_per_line = get_feature_per_line(sbfl_feature_file)
        mbfl_features_per_line = get_feature_per_line(mbfl_feature_file)

        # for each row of a bug version
        fl_features_per_line = []
        for sbfl_row, mbfl_row in zip(sbfl_features_per_line, mbfl_features_per_line):
            sbfl_key = sbfl_row['key']
            mfbl_key = mbfl_row['key']
            sbfl_bug_status = sbfl_row['bug']
            mbfl_bug_status = mbfl_row['bug']
            # VALIDATE that the keys are the same
            assert sbfl_key == mfbl_key, "Error: Keys are not the same"

            # VALIDATE that the bug status are the same
            assert sbfl_bug_status == mbfl_bug_status, "Error: Bug status are not the same"

            # 4. combine the features
            fl_row = {
                'key': sbfl_key,
                'ep': sbfl_row['ep'],
                'ef': sbfl_row['ef'],
                'np': sbfl_row['np'],
                'nf': sbfl_row['nf'],
                '# of totfailed_TCs': mbfl_row['# of totfailed_TCs'],
                '# of mutants': mbfl_row['# of mutants'],
                'm1:f2p': mbfl_row['m1:f2p'],
                'm1:p2f': mbfl_row['m1:p2f'],
                'm2:f2p': mbfl_row['m2:f2p'],
                'm2:p2f': mbfl_row['m2:p2f'],
                'm3:f2p': mbfl_row['m3:f2p'],
                'm3:p2f': mbfl_row['m3:p2f'],
                'm4:f2p': mbfl_row['m4:f2p'],
                'm4:p2f': mbfl_row['m4:p2f'],
                'm5:f2p': mbfl_row['m5:f2p'],
                'm5:p2f': mbfl_row['m5:p2f'],
                'm6:f2p': mbfl_row['m6:f2p'],
                'm6:p2f': mbfl_row['m6:p2f'],
                'm7:f2p': mbfl_row['m7:f2p'],
                'm7:p2f': mbfl_row['m7:p2f'],
                'm8:f2p': mbfl_row['m8:f2p'],
                'm8:p2f': mbfl_row['m8:p2f'],
                'm9:f2p': mbfl_row['m9:f2p'],
                'm9:p2f': mbfl_row['m9:p2f'],
                'm10:f2p': mbfl_row['m10:f2p'],
                'm10:p2f': mbfl_row['m10:p2f'],
                'm11:f2p': mbfl_row['m11:f2p'],
                'm11:p2f': mbfl_row['m11:p2f'],
                'm12:f2p': mbfl_row['m12:f2p'],
                'm12:p2f': mbfl_row['m12:p2f'],
                'bug': sbfl_bug_status,
                'muse susp. score': mbfl_row['muse susp. score'],
                'metallaxis susp. score': mbfl_row['met susp. score'],
            }

            # 5. append the row to the list
            fl_features_per_line.append(fl_row)
        
        # 6. write the features to a csv file
        write_fl_features(fl_feature_file, fl_features_per_line)
        write_fl_features_with_susp_scores(fl_feature_file_with_susp_scores_file, fl_features_per_line)


        # break



# example command: python3 combine_FL.py -sbfl sbfl -mbfl mbfl -fl fl
# ./1_combine_FL_features.py -sbfl sbfl_dataset-240410-v1 -mbfl mbfl_dataset-240409-v2 -fl fl_dataset-240413-v1

if __name__ == "__main__":
    parser = return_parser()
    args = parser.parse_args()

    start_program(args.sbfl, args.mbfl, args.fl)