#  Copyright (c) 2019 Lightricks. All rights reserved.
#  Created by Noam Freeman.

# This script is intended to message a PR when it has lint errors
# It also returns 1 in that case, enabling Jenkins to fail the build if we want.

from github import Github
import os
import sys

# Environment variable for the repo name, in the format 'Lightricks/Repo'.
GHPRB_REPO_ENV = "ghprbGhRepository"

# Environment variable for the pull request ID.
GHPRB_PR_ID_ENV = "ghprbPullId"

# Environment variable holding the Github username.
GITHUB_USERNAME_ENV = "DANGER_GITHUB_API_USER"

# Environment variable holding the Github password.
GITHUB_PASSWORD_ENV = "DANGER_GITHUB_API_TOKEN"

def github_post_or_edit_comment(username, passsword, repo_name, pr_number, comment, signature=None):
    github = Github(username, passsword)
    repo = github.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    comments = pr.get_issue_comments()
    if signature:
        for github_comment in comments:
            if github_comment.body.startswith(signature):
                github_comment.edit(comment)
                return

    pr.create_issue_comment(comment)


def post_comment_on_current_pr(comment, signature=None):
    try:
        username = os.environ[GITHUB_USERNAME_ENV]
        password = os.environ[GITHUB_PASSWORD_ENV]
        repo_name = os.environ[GHPRB_REPO_ENV]
        pr_number = int(os.environ[GHPRB_PR_ID_ENV])
    except KeyError as e:
        print("[-] Required environment variable '%s' cannot be found" % e.message)
        sys.exit(1)

    github_post_or_edit_comment(username, password, repo_name, pr_number, comment, signature)
