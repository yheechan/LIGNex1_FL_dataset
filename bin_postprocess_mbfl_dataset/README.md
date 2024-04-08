# bin_postprocess_mbfl_dataset

This bin directory is to contain python scripts to postprocess (or massage) MBFL feature dataset. 
* for finalized MBFL dataset: MBFL feature dataset must be saved within ``<root-dir>/mbfl_datasets/`` directory
* for un-finalized MBFL datset (just retrieved from distributed machines): saved within ``<root-dir>/mbfl_dataset_b4_gather`` directory


## Commands
* input: MBDL feature dataset directory name (generated from MBDL dataset generating tool)

### ``0_gather_mbfl_dataset.py``
* gather mbfl dataset from  ``<root-dir>/mbfl_dataset_b4_gather`` for structure directory such that it is user friendly and ease for analysis


### ``1_remove_bug_with_muse_score_0.py <past mbfl dataset name> <new mbfl dataset name>``
* operation: massages the past mbfl dataset by cloning a new mbfl dataset without bug versions with muse score of 0 (indicated in ``versions2remove.txt`` file)
* output: ``<root-dir>/mbfl_dataset_b4_gather/<new mbfl dataset name>``
* purpose: massage to increase fault localization accuracy of the dataset

### ``2_apply_1_on_bug_versions_code_and_prerequisites.py <past name> <new name>``
* operation: massages the past data (bug version code and prerequisites) just like command ``1_remove_bug_wiuth_muse_score_0.py``
* purpose: enable execution of newly massaged bug versions on SBFL too.


## Usual command steps
```
# bin_postprocess_mbfl_dataset
$ ./1_remove_bug_with_muse_score_0.py mbfl_dataset-240405-v1 mbfl_dataset-240405-v2
$ ./2_apply_1_on_bug_versions_code_and_prerequisites.py 181bugs-240405 165bugs-240405-v1
$ ./0_gather_mbfl_dataset.py mbfl_dataset-240405-v2
# manually copy bug_version_mutation_info.csv

# bin_analyze_mbfl
$ ./rank_mbfl.py mbfl_dataset-240405-v2

# bin_valid_check_mbfl
$ ./01_validate.py mbfl_dataset-240405-v2
$ ./02_validate.py mbfl_dataset-240405-v2

# bin_postprocess_mbfl_dataset
# copy mbfl_dataset-240405-v2 to mbfl_dataset-240405-v3
# for excluding lines (rows) from unnecessary source code files (i.e., test code, CMakeFiles)
$ ./3_remove_unwanted_rows.py mbfl_dataset-240405-v3

# bin_analyze_mbfl
$ ./rank_mbfl.py mbfl_dataset-240405-v3
```



last updated on April 6, 2024
