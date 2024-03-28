# tc2func_checker
This tool, ``tc2func_checker/bin``, is built to count the # of test cases that execute a target function.
  * test cases are from jsoncpp unit test cases (total 127 TCs)


## dependencies
1. [extractor](https://github.com/yheechan/LIGNex1_FL_dataset/tree/master/extractor)

## Execution step
### 0. enter ``bin`` directory
```
cd bin/
```

### 1. make jsoncpp template
```
./1_make_template.py jsoncpp_template
```

### 2. build jsoncpp with intermediate code for line-to-function information extraction
  * ``--save-temps`` option specificed in compile command
```
./2_build_jsoncpp.py jsoncpp_template
```

### 3. extract line-to-function information
  * line2function data is saved in ``output/line2function_data/line2function.json`` file
```
./3_extract_line2function.py jsoncpp_template
```

### 4. rebuild jsoncpp without intermediate code
  * jsoncpp when built with intermediate code (``--save-temps``), ``gcovr`` fails to measure coverage.
```
./4_rebuild_jsoncpp.py jsoncpp_template
```

### 5. get test suite from ``jsoncpp_test``
  * test suite information is saved in ``output/test_suite/test_suite.csv`` file
```
./5_get_test_suite.py
```

### 6. run the test suite and measure coverage for each test cases
  * the raw coverage data is saved in ``output/coverage/`` directory
  * when string other than ``gen_cov`` is given in the second input, coverage isn't measure
```
./6_run_test_suite.py jsoncpp_template gen_cov
```

### 7. post-process the raw coverage data (json formatted) to a csv format (line2tc)
  * the postprocessed coverage data is saved in ``output/pp_data.csv`` file
  * total line number: 6,675
```
7_postprocess_cov
```

### 8. merge lines to its assigned functions.
  * during merge TC that execute the line is merge to its assigned function
  * number of functions: 363
  * merged data is saved in ``output/pp_data-v2.csv`` file
```
./8_mergefunc.py
```


last updated on March 28, 2024
