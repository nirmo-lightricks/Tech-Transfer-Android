"""
This class responsible to run Boosted custom tests
"""
# Copyright (c) 2021 Lightricks. All rights reserved.
# Created by Yaakov Shahak
from project_modules import get_project_modules
from build_for_pr import run_build_for_pr


def main() -> None:
    """
    main function which run all tests
    """
    # pylint: disable=C0301
    modules = [module.name for module in get_project_modules()]
    run_build_for_pr(modules=modules, include_large_tests=True, use_build_cache=True)


if __name__ == "__main__":
    main()
