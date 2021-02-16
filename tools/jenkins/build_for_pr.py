"""
This module runs the buildForPr tasks
"""
import logging
from typing import Iterable, List, Set
from gradle_build import execute_gradle
from project_modules import get_project_modules, ModuleType


GRADLE_PR_TASK_NAME = "buildForPR"


def run_build_for_pr(modules: Iterable[str], include_large_tests: bool) -> None:
    """
    Runs build for pr for all modules
    """
    project_modules = get_project_modules()
    asset_modules = {
        module.name
        for module in project_modules
        if module.module_type == ModuleType.ASSET
    }
    gradle_arguments = _get_gradle_arguments(modules, include_large_tests, asset_modules)
    # if no gradle arguments are given i have nothing to run
    if gradle_arguments:
        execute_gradle(gradle_arguments, [])


def _get_gradle_arguments(
    modules: Iterable[str], include_large_tests: bool, asset_modules: Set[str]
) -> List[str]:
    buildable_modules = sorted(
        module for module in modules if module not in asset_modules
    )
    build_tasks = [f":{module}:{GRADLE_PR_TASK_NAME}" for module in buildable_modules]
    if not build_tasks:
        logging.info("Nothing to execute")
        return []
    # pylint: disable=C0301
    gradle_filters = (
        ["-Pandroid.testInstrumentationRunnerArguments.notAnnotation=com.lightricks.swish.utils.BoostedLargeTest"]
        if include_large_tests
        else [
            "-Pandroid.testInstrumentationRunnerArguments.notAnnotation=androidx.test.filters.LargeTest,com.lightricks.swish.utils.BoostedLargeTest"
        ]
    )
    return gradle_filters + ["clean"] + build_tasks
