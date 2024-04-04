# bin_jsoncpp_clone
This bin directory is to contain python scripts to clone jsoncpp from git repository and change its version to selected version.


## Commands

### ``1_clone_jsoncpp.py <template name>``
* operation: clones jsoncpp and changes the version (bug free version)

### ``2_build_jsoncpp.py <template name>``
* operation: builds jsoncpp
    * with coverage instrumentation
    * no compilation command file

### ``3_reset_coverage.py <template name>``
* operation: deletes all ``*.gcda`` files within the jsoncpp project.

### ``4_get_html.py <template name>``
* operation: generates the html for visualizing coverage

### ``5_delete_jsoncpp.py <template name>``
* operation: delete jsoncpp project repository


last updated on April 4, 2024
