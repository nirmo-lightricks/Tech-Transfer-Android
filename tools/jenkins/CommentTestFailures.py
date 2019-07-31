# Copyright (c) 2019 Lightricks. All rights reserved.
# Created by Noam Freeman.

import xml.etree.ElementTree as ET
import argparse
import collections

import github_message as message

TESTS_SIGNATURE = "generated_by_comment_test_failures_script"

def getFailingTests(tests):
    return filter(isAnyTestFailing, tests)

def isAnyTestFailing(test):
    return any(child.tag =='failure' for child in test)

def getTestCases(root):
    return (child for child in root if child.tag == "testcase")

def getTestName(test):
    return test.attrib["name"]

def getTestClass(test):
    return test.attrib["classname"]

def getFailure(test):
    return [child for child in test if child.tag == "failure"][0]

def getFailureMessage(test):
    return getFailure(test).text.splitlines()[0]


def getFailingTestFromFile(junit_xml_path):
    tree = ET.parse(junit_xml_path)
    root = tree.getroot()
    tests = getTestCases(root)
    failures = getFailingTests(tests)
    return failures

def createFailingTest(failure_xml):
    klass = getTestClass(failure_xml)
    name = getTestName(failure_xml)
    reason = getFailureMessage(failure_xml)
    return FailingTest(klass=klass, name=name, failure_message=reason)

FailingTest = collections.namedtuple('FailingTest', 'klass name failure_message')

def hidden_html_tag(metadata):
    return "<p align='right' metadata='" + metadata + "'></p>\n"

def markdown_table(failing_tests):
    return markdown_test_header() + "\n".join(map(markdown_failing_test, failing_tests))

def markdown_test_header():
    return "| Class | Name | Reason |\n|---|---|---|\n"

def markdown_failing_test(failing_test):
    return "|" + "|".join(list(failing_test)) + "|"

def markdown_link(text, url, alt=None):
    return f'[{text}]({url}{alt if alt else ""})'

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', metavar="test-results", type=str, nargs='*',
                        help='paths of the test result files')

    args = parser.parse_args()
    test_paths = args.paths

    if len(args.paths) == 0:
        print("No test found")
        exit(1)

    failures = []
    for test_result in test_paths:
        failures.extend(getFailingTestFromFile(test_result))

    failing_tests = list(map(createFailingTest, failures))

    if failing_tests:
        message.post_comment_on_current_pr("### There were failing test\n" +
                                           markdown_table(failing_tests), hidden_html_tag("Failing Tests"))
    else:
        message.post_comment_on_current_pr("### All tests passed\n", hidden_html_tag("Failing Tests"))
