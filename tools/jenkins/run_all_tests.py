"""
This class responsible to run Boosted custom tests
"""
# Copyright (c) 2021 Lightricks. All rights reserved.
# Created by Yaakov Shahak
import sys
from project_modules import get_project_modules, ModuleType, ProjectModule
from build_for_pr import run_build_for_pr

def main() -> int:
    """
    main function which run all tests
    """
    # pylint: disable=C0301
    modules = [module.name for module in get_project_modules()]
    run_build_for_pr(modules=modules, include_large_tests=True)


if __name__ == "__main__":
    sys.exit(main())
