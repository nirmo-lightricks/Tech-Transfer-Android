"""
This module decides which projects pr tests are run with gradle
"""
# Copyright (c) 2020 Lightricks. All rights reserved.
# Created by Geva Kipper.
import logging
import os
import re
import sys
from subprocess import run
from typing import Set
import networkx as nx  # type: ignore
from github import Github
from gradle_build import execute_gradle
from project_modules import get_application_dirs, get_module_dirs

logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)

# Environment variable for the repo name, in the format 'Lightricks/Repo'.
GHPRB_REPO_ENV = "ghprbGhRepository"

# Environment variable for the pull request ID.
GHPRB_PR_ID_ENV = "ghprbPullId"

# Environment variable holding the Github username.
GITHUB_USERNAME_ENV = "DANGER_GITHUB_API_USER"

# Environment variable holding the Github password.
GITHUB_PASSWORD_ENV = "DANGER_GITHUB_API_TOKEN"

# list of third party modules which shouldn't be checked
THIRD_PARTY_MODULES = {
    "botan",
    "gif_encoder",
    "protobuf-android",
    "opencv-android",
    "sdk",
    "facetune-android",
}

# list of modules that contain only assets.
# those module don't have any dependencies and don't need to be build
ASSET_MODULES = {
    "facetune_asset_packs"
}

GRADLE_PR_TASK_NAME = "buildForPR"


def _get_modified_dirs(
    username: str, password: str, repo_name: str, pr_id: str
) -> Set[str]:
    """
    Returns set of modified android directories in a given PR.
    """
    github = Github(username, password)
    logging.info("Fetching repo %s...", repo_name)
    repo = github.get_repo(repo_name)

    logging.info("Fetching PR #%s...", pr_id)
    pull = repo.get_pull(int(pr_id))

    files = pull.get_files()
    logging.info("Files changed in PR: %s", [f.filename for f in files])

    modified_dirnames = {
        f.filename.split(os.path.sep)[0] if os.path.sep in f.filename else "/"
        for f in files
    }
    logging.info("Directories changed in PR: %s", modified_dirnames)
    return modified_dirnames


def _get_module_dependencies(module: str) -> Set[str]:
    if module in ASSET_MODULES:
        return {}
    pattern = re.compile(r"--- :([\w-]+)")
    cmd = run(
        ["./gradlew", "-q", f"{module}:androidDependencies"],
        capture_output=True,
        text=True,
        check=True,
    )
    match_gen = (pattern.search(line) for line in cmd.stdout.splitlines())
    dependencies = {match.groups()[0] for match in match_gen if match} - {module}
    return dependencies


def _get_project_dependencies() -> nx.DiGraph:
    all_modules = set(get_module_dirs())
    project_dependencies = {
        module: _get_module_dependencies(module) for module in all_modules
    }
    graph = nx.DiGraph()
    graph.add_nodes_from(all_modules)
    dependencies_gen = (
        (module, dependency)
        for module in project_dependencies
        for dependency in project_dependencies[module]
    )
    graph.add_edges_from(dependencies_gen)
    return graph


def _get_modules_to_build(modified_dirs: Set[str]) -> Set[str]:
    application_dirs = set(get_application_dirs())
    if modified_dirs.issubset(application_dirs):
        return modified_dirs
    dependency_graph = _get_project_dependencies()
    all_modules = set(dependency_graph.nodes)
    # if there are non gradle directories we cannot know the impact of the change
    # so we run all modules
    if modified_dirs - all_modules:
        return all_modules
    modified_modules = set(dependency_graph.nodes) & modified_dirs
    logging.info("modified modules are %s", modified_modules)
    dependent_modules = {
        ancestor
        for modified_module in modified_modules
        for ancestor in nx.ancestors(dependency_graph, modified_module)
    }
    logging.info("dependent_modules are %s", dependent_modules)
    return dependent_modules | modified_modules


def modules_to_build() -> Set[str]:
    """
    This function decides which modules tests are run
    """
    username = os.environ[GITHUB_USERNAME_ENV]
    password = os.environ[GITHUB_PASSWORD_ENV]
    repo = os.environ[GHPRB_REPO_ENV]
    pr_id = os.environ[GHPRB_PR_ID_ENV]
    modified_dirs = _get_modified_dirs(username, password, repo, pr_id)
    return _get_modules_to_build(modified_dirs)


def main() -> int:
    modules = modules_to_build()

    build_tasks = [f":{module}:{GRADLE_PR_TASK_NAME}" for module in modules]
    if not build_tasks:
        logging.info("Nothing to execute")
        return 0
    # pylint: disable=C0301
    gradle_arguments = [
        "-Pandroid.testInstrumentationRunnerArguments.notAnnotation=androidx.test.filters.LargeTest",
        "clean",
    ] + build_tasks
    return execute_gradle(gradle_arguments, [])


if __name__ == "__main__":
    sys.exit(main())
