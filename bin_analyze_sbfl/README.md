# bin_analyze_sbfl
This bin directory is to contain python scripts to analyze SBFL feature dataset. SBFL feature dataset must be saved within ``<root-dir>/sbfl_datasets/`` directory.


## Commands
* input: SBFL feature dataset directory name (generated from SBFL dataset generating tool)

### ``rank_sbfl.py <sbfl dataset name> <output csv file name>``
* operation: measures the rank of each row to each SBFL formula (function level)
* output: the rank in csv file will be saved in ``output/`` directory


last updated on April 6, 2024
