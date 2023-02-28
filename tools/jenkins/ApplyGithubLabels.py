import os
import sys

from github import Github

# Environment variable for the repo name, in the format 'Lightricks/Repo'.
GHPRB_REPO_ENV = "ghprbGhRepository"

# Environment variable for the pull request ID.
GHPRB_PR_ID_ENV = "ghprbPullId"

# Environment variable holding the Github username.
GITHUB_USERNAME_ENV = "DANGER_GITHUB_API_USER"

# Environment variable holding the Github password.
GITHUB_PASSWORD_ENV = "DANGER_GITHUB_API_TOKEN"

def apply_labels(username, password, repo, pr_id):
    github = Github(username, password)

    print("[+] Fetching repo %s..." % repo)
    repo = github.get_repo(repo)

    print("[+] Fetching PR #%s..." % pr_id)
    pull = repo.get_pull(int(pr_id))

    files = list(pull.get_files())
    print("[+] Files changed in PR: [%s]" % [f.filename for f in files])

    print("[+] Fetching issue #%s..." % pr_id)
    issue = repo.get_issue(int(pr_id))

    repo_labels = list(repo.get_labels())
    print("[+] Currently available labels: [%s]" % [l.name for l in repo_labels])

    issue_labels = list(issue.get_labels())
    print("[+] Currently set labels for PR: [%s]" % [l.name for l in issue_labels])

    available_labels = set([l.name for l in repo_labels])
    labels = labels_from_files(files) & available_labels | non_status_labels(issue_labels)

    print("[+] Labels to set: [%s]" % ", ".join(labels))
    if set([l.name for l in issue_labels]) != labels:
        print("[+] Setting labels...")
        issue.set_labels(*labels)
    else:
        print("[+] All labels are already set, skipping")


def labels_from_files(files):
    return set([f.filename.split(os.path.sep)[0] for f in files if os.path.sep in f.filename])


def non_status_labels(labels):
    return set([l.name for l in labels if l.name.startswith("[") and l.name.endswith("]")])


def main():
    try:
        username = os.environ[GITHUB_USERNAME_ENV]
        password = os.environ[GITHUB_PASSWORD_ENV]
        repo = os.environ[GHPRB_REPO_ENV]
        pr_id = os.environ[GHPRB_PR_ID_ENV]
    except KeyError as e:
        print("[-] Required environment variable '%s' cannot be found" % e.message)
        sys.exit(1)

    apply_labels(username, password, repo, pr_id)


if __name__ == "__main__":
    main()

