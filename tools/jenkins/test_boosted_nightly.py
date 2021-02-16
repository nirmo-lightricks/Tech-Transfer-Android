"""
This class responsible to run Boosted custom tests
"""
# Copyright (c) 2021 Lightricks. All rights reserved.
# Created by Yaakov Shahak
import sys
from gradle_build import execute_gradle
from build_for_pr import run_build_for_pr


def main():
    """
    main function which runs the pr logic
    """
    # pylint: disable=C0301
    gradle_arguments = ["-Pandroid.testInstrumentationRunnerArguments.annotation=com.lightricks.swish.utils.BoostedLargeTest",
     'swish:buildForPR']
    return execute_gradle(gradle_arguments, [])


if __name__ == "__main__":
    sys.exit(main())
