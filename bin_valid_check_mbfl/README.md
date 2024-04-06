# bin_valid_check_mbfl
This bin directory is to contain python scripts to check the validity of MBFL feature dataset. MBFL feature dataset must be saved within ``<root-dir>/mbfl_datasets/`` directory.


## Commands
* input: MBFL feature dataset directory name (generated from MBFL dataset generating tool)

### ``01_validate.py <mbfl dataset name>``
* operation: validate that all bugs retrieved from distributed machines contain mbfl feature dataset csv file.

### ``02_validate.py <mbfl dataset name>``
* operation: validate that the mutation token exists in the buggy code file



last updated on April 6, 2024
