"""
This script runs tests for an app and all it's descendants
"""
import argparse
import logging
from typing import Set
from project_modules import get_project_modules, get_project_dependencies
from build_for_pr import run_build_for_pr

logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)

# dynamic dfs. If gradlew dependencies would have been fast i would have used networkx instead
def _get_all_modules_to_build(app: str) -> Set[str]:
    application_module = next(
        module for module in get_project_modules() if module.name == app
    )
    res = {application_module}
    stack = [application_module]
    while stack:
        current = stack.pop()
        dependencies = get_project_dependencies(current)
        for dependency in dependencies:
            if dependency not in res:
                res.add(dependency)
                stack.append(dependency)
    return {module.name for module in res}


def _run_tests(app: str) -> None:
    all_modules = _get_all_modules_to_build(app)
    logging.info("running tests of %s", all_modules)
    run_build_for_pr(
        modules=all_modules, include_large_tests=True, use_build_cache=True
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("app")
    args = parser.parse_args()
    _run_tests(args.app)
