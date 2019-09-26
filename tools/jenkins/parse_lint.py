#  Copyright (c) 2019 Lightricks. All rights reserved.
#  Created by Noam Freeman.

import xml.etree.ElementTree as ET

import collections

Location = collections.namedtuple('Location', 'file line column')

LintIssue = collections.namedtuple('LintIssue', 'id priority location')

def _getLocation(issue):
    return [n for n in issue][0]

def _issues(tree):
    return [node for node in tree.getroot() if node.tag == "issue"]

def _has_issues(tree):
    return len(_issues(tree)) > 0

def _issues_ids(issues):
    return {issue.attrib["id"] for issue in issues}

def _has_fatal_issues(tree):
    return bool(_fatal_issues(tree.getroot()))


def _issues_with_severity(git_issues, severity):
    return [issue for issue in git_issues if issue.attrib["severity"] == severity]


def _fatal_issues(git_issues):
    return _issues_with_severity(git_issues, "Fatal")


def _fatal_issues_ids(git_issues):
    return {issue.attrib["id"] for issue in _fatal_issues(git_issues)}


def _parse_location(xml_location):
    file = xml_location.attrib["file"]
    try:
        line = xml_location.attrib["line"]
        column = xml_location.attrib["column"]
    except:
        line = -1
        column = -1

    return Location(file, line, column)

def parse_issue(xml_issue):
    id = xml_issue.attrib["id"]
    priority = xml_issue.attrib["priority"]
    location = _parse_location(_getLocation(xml_issue))
    return LintIssue(id, priority, location)

def linter_issues(lint_xml_report):
    tree = ET.parse(lint_xml_report)
    return _issues(tree)

def parse_issues(lint_xml_report):
    return [parse_issue(issue) for issue in linter_issues(lint_xml_report)]
