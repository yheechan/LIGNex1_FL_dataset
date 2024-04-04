# LIGNex1_FL_dataset

## Background directories
### bin: for executing scripts
* ``bin_analyze_mbfl``: directory containing executables to analyze MBFL feature dataset.
* ``bin_analyze_sbfl``: directory containing executables to analyze SBFL feature dataset.
* ``bin_cmd_machiens``: directory containing executables to handline commands in distributed machines with ease.
* ``bin_jsoncpp_clone``: directory containing executables to clone, build, and measure coverage of a target jsoncpp project.
* ``bin_postprocess_sbfl_data``: directory containing executables to postprocess (or massage) SBFL feature dataset.

### tool: tools to generate data (information)
* ``extractor``: directory containing source code and build script for line-to-function extraction.
* ``tc2func_checker``: functions to measure the number of TCs executing a target function.
* ``MBFL_dataset_generator``: repository of the project that generates MBFL feature dataset based on:
    * ``bug_versions_code``
    * ``prerequisite_data``

### dataset: generated dataset (ignored in git repository)
* ``mbfl_datasets``: contains MBFL dataset results from MBFL dataset generating tool.
* ``sbfl_datasets``: contains SBFL dataset results from SBFL dataset generating tool.

### prerequisites: data needed for generating certain dataset
* ``original_code_files_on_jsoncpp``: contains code files for original (bug free) jsoncpp source code.
* ``bug_versions_code``: code containing buggy source code file of bug versions (differentiated by dataset - pair with ``prerequisite_data``) (ignored in git repository)
* ``prerequisite_data``: dataset that contains prerequisite data such as **lines executed by failing TC** or **test case info (CCTCs)** of bug versions (differentiated by dataset - pair with ``bug_versions_code``) (ignored in git repository)


last update on April 4, 2024
