#  Copyright (c) 2019 Lightricks. All rights reserved.
#  Created by Noam Freeman.

import glob
import os

import parse_lint
import project_modules
from BuildReport import ReportEntry, Status

MAX_LINT_ISSUES_TO_PREVIEW = 20
LINT_REPORT_PATH_IN_MODULE = os.path.join("build", "reports", "lint-results*.xml")

def markdown_table_header(*titles):
    header = "| "
    for title in titles :
        header += str(title) + " | "
    header += "\n"
    separation_line = "|"
    for title in titles:
        separation_line += "---|"
    separation_line += "\n"
    return header + separation_line

def markdown_table(workspace, lint_errors):
    lint_issues = "\n".join(markdown_lint_issue(workspace, lint_issue) for lint_issue in lint_errors)
    return markdown_table_header("Id", "Line", "Col", "File") + lint_issues

def remove_string_begining(string, infix):
    f = string.find(infix)
    if f == -1:
        return string
    return string[f + len(infix):]


def markdown_lint_issue(workspace, lint_issue):
    short_path = remove_string_begining(lint_issue.location.file, f"{workspace}/")
    # we want: https://github.com/Lightricks/facetune-android/tree/<CommitFullHash>/short_path
    # should be:
    # github_path = pull.commits.reversed[0].html_url
    # or:
    # repo.get_commit(pull.merge_commit_sha).html_url
    return f"| {lint_issue.id} | {lint_issue.location.line} | {lint_issue.location.column} | {short_path} |"


def lint_report(lint_report_paths):
    return [parse_lint.parse_issue(issue) for lint_report_xml in lint_report_paths
            for issue in parse_lint.linter_issues(lint_report_xml)]


def lint_report_for_module(module_path):
    results_paths = glob.glob(os.path.join(module_path, LINT_REPORT_PATH_IN_MODULE))
    return lint_report(results_paths)

def lint_comment(workspace, lint_report):
    return markdown_table(workspace, lint_report[:MAX_LINT_ISSUES_TO_PREVIEW])

def create_lint_entries(workspace):
    modules = project_modules.get_module_dirs(workspace)

    for module in modules:
        # a list of LintReport('id priority location')
        reports_paths = glob.glob(os.path.join(workspace, module, LINT_REPORT_PATH_IN_MODULE))
        if not reports_paths:
            continue

        lint_issues = lint_report_for_module(os.path.join(workspace, module))
        if not lint_issues:
            status = Status.OK
            info = "no lint issues"
            details = ""
        else:
            status = Status.ERROR
            info = f"there are {len(lint_issues)} lint issues"
            details = lint_comment(workspace, lint_issues)

        module_name = os.path.basename(module)
        yield ReportEntry(module_name, status, "Lint", info, details)
