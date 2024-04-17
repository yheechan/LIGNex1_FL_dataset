# bin_valid_check_sbfl
This bin directory is to contain python scripts to check the validity of SBFL feature dataset. SBFL feature dataset must be saved within ``<root-dir>/sbfl_datasets/`` directory.


## Commands
* input: SBFL feature dataset directory name (generated from SBFL dataset generating tool)

### ``01_validate.py <sbfl dataset name>``
* command to validate whether sbfl spectrum data includes a **single buggy line** as rows in its csv data file.

### ``02_validate.py <sbfl dataset name>``
＊ VALIDATE 02: CHECK IF THE MUTANT CODE EXISTS IN ORIGIN BUG VERSION CODE

### ``03_validate.py <sbfl dataset name>``
＊ VALIDATE 03: CHECK IF ALL THE FAILING TEST CASES EXECUTE THE BUGGY LINE

### ``04_validate.py <sbfl dataset name>``
＊ VALIDATE 04: CHECK THAT SPECTRUM VALUES ADD UP TO THE SUM OF FAILING AND PASSING TEST CASES




last updated on April 17, 2024
