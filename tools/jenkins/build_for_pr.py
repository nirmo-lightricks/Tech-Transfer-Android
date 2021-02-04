"""
This module runs the buildForPr tasks
"""
import logging
from typing import Iterable
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
    buildable_modules = (module for module in modules if module not in asset_modules)
    build_tasks = [f":{module}:{GRADLE_PR_TASK_NAME}" for module in buildable_modules]
    if not build_tasks:
        logging.info("Nothing to execute")
        return
    # pylint: disable=C0301
    if include_large_tests:
        gradle_arguments = ["clean"] + build_tasks
    else:
        gradle_arguments = [
            "-Pandroid.testInstrumentationRunnerArguments.notAnnotation=androidx.test.filters.LargeTest",
            "clean",
        ] + build_tasks
    execute_gradle(gradle_arguments, [])
