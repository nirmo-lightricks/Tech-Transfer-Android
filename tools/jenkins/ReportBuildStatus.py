# Copyright (c) 2019 Lightricks. All rights reserved.
# Created by Noam Freeman.

import argparse
from itertools import chain

import BuildReport
import LintReport
import MarkdownUtils
import TestReport
import CompilationReport
import github_message as message

TESTS_SIGNATURE = "generated_by_comment_test_failures_script"


def collect_test_entries(workspace):
    return TestReport.generate_report_entries(workspace)


def collect_compilation_entries(workspace):
    return CompilationReport.create_compilation_entries(workspace)

def collect_lint_entries(workspace):
    return LintReport.create_lint_entries(workspace)

def collect_entries(workspace):
    return chain(
        collect_test_entries(workspace),
        collect_compilation_entries(workspace),
        collect_lint_entries(workspace)
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('workspace_dir')
    args = parser.parse_args()
    workspace = args.workspace_dir

    entries = collect_entries(workspace)
    report = BuildReport.report_markdown(entries)

    tests_signature = MarkdownUtils.hidden_html_tag(TESTS_SIGNATURE)
    message.post_comment_on_current_pr(tests_signature + report, tests_signature)
