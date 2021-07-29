#  Copyright (c) 2019 Lightricks. All rights reserved.
#  Created by Noam Freeman.

import glob
import os
import parse_lint
import project_modules
from BuildReport import ReportEntry, Status
from typing import List

MAX_LINT_ISSUES_TO_PREVIEW = 20
LINT_REPORT_PATH_IN_MODULE = os.path.join("build", "reports", "lint-results*.xml")
DETEKT_REPORT_PATH_IN_MODULE = os.path.join("build", "detekt-results", "detekt.xml")


def markdown_table_header(*titles):
    header = "| "
    for title in titles:
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


def detekt_report(lint_report_paths):
    return [parse_lint.parse_detekt_issue(file_node, issue_node) for lint_report_xml in lint_report_paths
            for file_node in parse_lint.obtain_file_nodes(lint_report_xml)
            for issue_node in file_node]


def lint_report_for_module(module_path):
    results_paths = glob.glob(os.path.join(module_path, LINT_REPORT_PATH_IN_MODULE))
    return lint_report(results_paths)


def detekt_report_for_module(module_path):
    result_paths = glob.glob(os.path.join(module_path, DETEKT_REPORT_PATH_IN_MODULE))
    return detekt_report(result_paths)


def lint_comment(workspace, lint_report):
    return markdown_table(workspace, lint_report[:MAX_LINT_ISSUES_TO_PREVIEW])


def lint_entry(lint_issues, module_name, workspace) -> List[ReportEntry]:
    if lint_issues:
        status = Status.WARNING
        info = f"there are {len(lint_issues)} lint issues"
        details = lint_comment(workspace, lint_issues)
        contribution = [ReportEntry(module_name, status, "Lint", info, details)]
    else:
        contribution = []

    return contribution


def detekt_entry(detekt_issues_report, module_name, workspace) -> List[ReportEntry]:
    if detekt_issues_report:
        status = Status.WARNING
        num_detekt_issues = len(detekt_issues_report)
        if num_detekt_issues > 1:
            info = f"there are {num_detekt_issues} Detekt issues"
        else:
            info = "there is a Detekt issue"
        details = lint_comment(workspace, detekt_issues_report)
        contribution = [ReportEntry(module_name, status, "Detekt", info, details)]
    else:
        contribution = []

    return contribution


def no_issues_entry(module_name) -> ReportEntry:
    status = Status.OK
    info = "no lint issues"
    details = ""
    return ReportEntry(module_name, status, "Lint", info, details)


def create_lint_entries(workspace):
    modules = project_modules.get_module_dirs()

    for module in modules:
        module_name = os.path.basename(module)

        # a list of LintReport('id priority location')
        reports_paths = glob.glob(os.path.join(workspace, module, LINT_REPORT_PATH_IN_MODULE))

        lint_is_integrated = bool(reports_paths)
        if lint_is_integrated:
            report = lint_report_for_module(os.path.join(workspace, module))
        else:
            report = []

        lint_issues = [issue for issue in report
                       if parse_lint.severities[issue.severity] >= parse_lint.severities["Warning"]]

        detekt_issues_report = detekt_report_for_module(os.path.join(workspace, module))

        entries = []
        entries += lint_entry(lint_issues, module_name, workspace)
        entries += detekt_entry(detekt_issues_report, module_name, workspace)

        if lint_is_integrated and not entries:
            entries.append(no_issues_entry(module_name))

        for entry in entries:
            yield entry
