# bin_postprocess_mbfl_dataset

This bin directory is to contain python scripts to postprocess (or massage) MBFL feature dataset. 
* for finalized MBFL dataset: MBFL feature dataset must be saved within ``<root-dir>/mbfl_datasets/`` directory
* for un-finalized MBFL datset (just retrieved from distributed machines): saved within ``<root-dir>/mbfl_dataset_b4_gather`` directory


## Commands
* input: MBDL feature dataset directory name (generated from MBDL dataset generating tool)

### ``0_gather_mbfl_dataset.py``
* gather mbfl dataset from  ``<root-dir>/mbfl_dataset_b4_gather`` for structure directory such that it is user friendly and ease for analysis



last updated on April 6, 2024
