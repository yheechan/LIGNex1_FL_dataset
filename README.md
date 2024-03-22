# LIGNex1_FL_dataset

## Background directories
* ``sbfl_datasets``: contains SBFL dataset results from SBFL dataset generating tool.

## Commands
### ``bin_analyze_sbfl``
* **input**: SBFL feature dataset directory, from SBFL dataset generating tool.
* ``validate_01.py``: command to validate whether sbfl spectrum data includes a single buggy line as rows in its csv data file.
* ``rank_sbfl.py``: measures rank of each row to each SBFL formula


### ``bin_postprocess_sbfl_dataset``
* ``0_remove_unwanted_rows.py``: removes rows (lines) in SBFL spectrum dataset csv file for improving ``acc@5`` accuracy.
    ```
    unwanted = ['jsontestrunner', 'test_lib_json', 'CmakeFiles']
    checked = ['jsontestrunner', 'test_lib_json', 'json', 'lib_json', 'CMakeFiles']
    ```
