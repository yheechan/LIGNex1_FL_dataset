# SBFL_dataset_generator

### commone use
```
# SBFL_dataset_generator/bin
$ ./1_copy_prerequisites_local.py prerequisite_dataset_165bugs-240405-v1 sbfl_dataset-240410-v1
$ ./2_measure_sbfl_features_local.py sbfl_dataset-240410-v1

# bin_postprocess_sbfl_dataset
$ ./0_remove_unwanted_rows.py sbfl_dataset-240410-v1 sbfl_features_per_bug-all
$ ./0_remove_unwanted_rows.py sbfl_dataset-240410-v1 sbfl_features_per_bug

# bin_analyze_sbfl
$ ./rank_sbfl.py sbfl_dataset-240410-v1 240410-v1
# then manually copy and past the rank file from output/
```


### have been working on bin_on_machine
* stopped after realizing I can use prerequisite data coverage to measure SBFL features.