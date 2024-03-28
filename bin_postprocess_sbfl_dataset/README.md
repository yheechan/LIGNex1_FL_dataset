# bin_postprocess_sbfl_dataset
This bin directory is to contain python scripts to postprocess (or massage) SBFL feature dataset. SBFL feature dataset must be saved within ``<root-dir>/sbfl_datsets/`` directory


## Commands
* input: SBFL feature dataset directory name (generated from SBFL dataset generating tool)

### ``0_remove_unwanted_rows.py <sbfl dataset path>``
* removes rows (lines) in SBFL feature dataset csv file for improving ``acc@5`` performance.
* specifically removes irrelevant source code files (i.e., test code)
```
unwanted = ['jsontestrunner', 'test_lib_json', 'CMakeFiles']
checked = ['jsontestrunner', 'test_lib_json', 'json', 'lib_json', 'CMakeFiles']
```



last updated on March 28, 2024
