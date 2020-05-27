# Copyright (c) 2020 Lightricks. All rights reserved.
# Created by Geva Kipper.

import argparse
import os
from os.path import basename

from gradle_build import execute_gradle
from project_modules import get_module_dirs
from github import Github

# Environment variable for the repo name, in the format 'Lightricks/Repo'.
GHPRB_REPO_ENV = "ghprbGhRepository"

# Environment variable for the pull request ID.
GHPRB_PR_ID_ENV = "ghprbPullId"

# Environment variable holding the Github username.
GITHUB_USERNAME_ENV = "DANGER_GITHUB_API_USER"

# Environment variable holding the Github password.
GITHUB_PASSWORD_ENV = "DANGER_GITHUB_API_TOKEN"

# Whitelist of modules that nothing depends on
LEAF_MODULE_WHITELIST = {"pixaloop", "facetune", "swish", "quickshot", "videoleap",
                         "billing_playground", "wechat_playground"}

GRADLE_PR_TASK_NAME = "buildForPR"


def get_modified_dirs(workspace, username, password, repo, pr_id):
    """
    Returns set of modified android directories in a given PR.
    """
    modules = {basename(m) for m in get_module_dirs(workspace)}
    print(f"[+] Found modules: {modules}")
    assert modules, "Didn't find any build.gradle files in workspace!"
    github = Github(username, password)
    print("[+] Fetching repo %s..." % repo)
    repo = github.get_repo(repo)

    print("[+] Fetching PR #%s..." % pr_id)
    pull = repo.get_pull(int(pr_id))

    files = pull.get_files()
    print("[+] Files changed in PR: %s" % [f.filename for f in files])

    # This assumes that the leaf module directories are all directly under the root repository directory
    modified_dirnames = {f.filename.split(os.path.sep)[0] if os.path.sep in f.filename else "/" for f in files}
    print("[+] Directories changed in PR: %s" % modified_dirnames)

    return modified_dirnames


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('workspace_dir')
    args = parser.parse_args()
    workspace = args.workspace_dir
    username = os.environ[GITHUB_USERNAME_ENV]
    password = os.environ[GITHUB_PASSWORD_ENV]
    repo = os.environ[GHPRB_REPO_ENV]
    pr_id = os.environ[GHPRB_PR_ID_ENV]
    modified_dirs = get_modified_dirs(workspace, username, password, repo, pr_id)

    # When a single module is updated, that has no dependents, only compile and test that module
    tasks = ["clean"]
    excluded_tasks = []
    if modified_dirs.issubset(LEAF_MODULE_WHITELIST):
        for dir in modified_dirs:
            tasks.append(f":{dir}:{GRADLE_PR_TASK_NAME}")
    else:  # Build all modules for PR
        tasks.append(f"{GRADLE_PR_TASK_NAME}")
    return execute_gradle(tasks, excluded_tasks)


if __name__ == "__main__":
    exit(main())
