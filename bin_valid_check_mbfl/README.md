# bin_valid_check_mbfl
This bin directory is to contain python scripts to check the validity of MBFL feature dataset. MBFL feature dataset must be saved within ``<root-dir>/mbfl_datasets/`` directory.


## Commands
* input: MBFL feature dataset directory name (generated from MBFL dataset generating tool)

### ``01_validate.py <mbfl dataset name>``
* operation: validate that all bugs retrieved from distributed machines contain mbfl feature dataset csv file.

### ``02_validate.py <mbfl dataset name>``
* operation: validate that the mutation token exists in the buggy code file

### ``03_validate.py <mbfl dataset name>``
* VALIDATE 03: VALIDATE THAT:
    * (1/((muse_a+1)*(muse_b+1))) * (muse_2) = muse_4
    * (1/((muse_a+1)*(muse_c+1))) * (muse_3) = muse_5
    * muse_4 - muse_5 = muse_6

### ``04_validate.py <mbfl dataset name>``
* VALIDATE 03: VALIDATE THAT MBFL FEATURE CSV FILE ONLY CONTAIN 1 BUGGY LINE


last updated on April 6, 2024
