# CI utils

## Running tests
Unit tests for dependency fetching etc. can be run as following

1. `cd` to the root dir of the project
2. run:

```bash
python3 -m unittest discover -s tools/jenkins
```

## Other components

* build_for_pr.py - This is the script that gets executed when running CI. Among the component it eventually runs:
  * parse_lint.py - This is the script that parses static analysis results and displays them in the final report.
  * BuildReport.py - Creates a "nice" build report for the build result.
  * build_modified_modules_v2 - extracts the modified modules during build
  * gradle_build - Calls a Gradle build for each module

_TBD: Others_

