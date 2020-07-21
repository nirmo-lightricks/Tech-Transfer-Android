#  Copyright (c) 2019 Lightricks. All rights reserved.
#  Created by Geva Kipper.

# This script is intended to message a PR when it has lint errors
# It also returns 1 in that case, enabling Jenkins to fail the build if we want.

import argparse
from github import Github
import os
import sys

# Environment variable for the repo name, in the format 'Lightricks/Repo'.
GHPRB_REPO_ENV = "ghprbGhRepository"

# Environment variable for the pull request commit SHA.
GHPRB_PR_SHA_ENV = "PULL_REQUEST_SHA"

# Environment variable holding the Github username.
GITHUB_USERNAME_ENV = "DANGER_GITHUB_API_USER"

# Environment variable holding the Github password.
GITHUB_PASSWORD_ENV = "DANGER_GITHUB_API_TOKEN"


def github_post_or_edit_status(username, password, repo_name, pr_sha, context, description, state, details_url):
    github = Github(username, password)
    repo = github.get_repo(repo_name)
    repo.get_commit(sha=pr_sha).create_status(
        context=context,
        description=description,
        state=state,
        target_url=details_url
    )


def update_status_on_current_pr(context, description, state, details_url):
    try:
        username = os.environ[GITHUB_USERNAME_ENV]
        password = os.environ[GITHUB_PASSWORD_ENV]
        repo_name = os.environ[GHPRB_REPO_ENV]
        pr_sha = os.environ[GHPRB_PR_SHA_ENV]
    except KeyError as e:
        print("[-] Required environment variable '%s' cannot be found" % e.message)
        sys.exit(1)

    github_post_or_edit_status(username, password, repo_name, pr_sha, context, description, state, details_url)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('context')
    parser.add_argument('description')
    parser.add_argument('state')
    parser.add_argument('details_url')
    args = parser.parse_args()
    update_status_on_current_pr(args.context, args.description, args.state, args.details_url)
