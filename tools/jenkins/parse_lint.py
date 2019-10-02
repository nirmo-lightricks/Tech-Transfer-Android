#  Copyright (c) 2019 Lightricks. All rights reserved.
#  Created by Noam Freeman.

import xml.etree.ElementTree as ET

import collections

Location = collections.namedtuple('Location', 'file line column')

LintIssue = collections.namedtuple('LintIssue', 'id priority location severity')

severities = {
    "Fatal": 4,
    "Error": 3,
    "Warning": 2,
    "Information": 1 }

def _get_location(issue):
    return [n for n in issue][0]

def _issues(tree):
    return [node for node in tree.getroot() if node.tag == "issue"]

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
    severity = xml_issue.attrib["severity"]
    location = _parse_location(_get_location(xml_issue))
    return LintIssue(id, priority, location, severity)

def linter_issues(lint_xml_report):
    tree = ET.parse(lint_xml_report)
    return _issues(tree)

def parse_issues(lint_xml_report):
    return [parse_issue(issue) for issue in linter_issues(lint_xml_report)]
