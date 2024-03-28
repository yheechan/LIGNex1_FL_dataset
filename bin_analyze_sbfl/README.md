# bin_analyze_sbfl
This bin directory is to contain python scripts to analyze SBFL feature dataset. SBFL feature dataset must be saved within ``<root-dir>/sbfl_datasets/`` directory.


## Commands
* input: SBFL feature dataset directory name (generated from SBFL dataset generating tool)

### ``validate_01.py <sbfl dataset path>``
* command to validate whether sbfl spectrum data includes a **single buggy line** as rows in its csv data file.

### ``rank_sbfl.py <sbfl dataset path> <output csv file name>``
* measures rank of each row to each SBFL formula (function level)


last updated on March 28, 2024
