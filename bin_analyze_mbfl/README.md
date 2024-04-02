# bin_analyze_mbfl
This bin directory is to contain python scripts to analyze MBFL feature dataset. MBFL feature dataset must be saved within ``<root-dir>/mbfl_datasets/`` directory.


## Commands

### ``make_summary.py <mbfl dataset path>``
* operation: make summary of mbfl feature dataset given the dataset path.
* output: the file will be saved in ``<mbfl dataset path>`` itself as ``statistic_summary.csv``
* purpose: analyze mbfl feature dataset (e.g., rank, mutant statistics, etc.)

### ``perline_f2p_one_bug.py <target_mbfl_dir_name> <target_bug_version>``
* operation: generates a csv containing the total f2p and p2f numbers for each line that contain generated mutants (for a single bug version).
* output: the files are saved in ``./output/`` directory as ``<bug-version>.perline_f2p.csv``
* purpose: anaylyze perline-mutants information

### ``line_mutants_one_bug.py <target_mbfl_dir_name> <target_bug_version> <target_file> <target_lineno>``
* operation: prints out the mutant information for a **single line** of a **single target source code file** of a **single bug version**.
* purpose: select a single line to investigate (mutants)


last updated on April 2, 2024
