# Copyright (c) 2019 Lightricks. All rights reserved.
# Created by Noam Freeman.

import xml.etree.ElementTree as ET
import argparse
import collections
import os
import re
from glob import glob
from enum import Enum

import github_message as message

TESTS_SIGNATURE = "generated_by_comment_test_failures_script"

class TestType(Enum):
    UNIT_TEST = "unit tests"
    ANDROID_TEST = "android tests"


FailingTest = collections.namedtuple('FailingTest', 'klass name failure_message')

TestReport = collections.namedtuple('TestReport', 'num_of_test failing_tests')


######################
# xml report parsing #
######################

def is_test_failing(test_case_xml):
    return any(child.tag == 'failure' for child in test_case_xml)


def get_test_cases(report_xml):
    return (child for child in report_xml if child.tag == "testcase")


def get_test_name(test_xml):
    return test_xml.attrib["name"]


def get_test_class(test_xml):
    return test_xml.attrib["classname"]


def get_failure_stack(test_xml):
    return [child for child in test_xml if child.tag == "failure"][0]


def get_failure_message(test_xml):
    return get_failure_stack(test_xml).text.splitlines()[0]


def get_test_cases_from_file(junit_xml_path):
    tree = ET.parse(junit_xml_path)
    root = tree.getroot()
    tests = get_test_cases(root)
    return tests


def num_of_tests(junit_xml_path):
    tests_xml_objects = get_test_cases_from_file(junit_xml_path)
    return sum(True for test in tests_xml_objects)


def get_failing_tests_xmls_from_file(junit_xml_path):
    tests_xml_objects = get_test_cases_from_file(junit_xml_path)
    failures = filter(is_test_failing, tests_xml_objects)
    return failures


def create_failing_test(failure_xml):
    klass = get_test_class(failure_xml)
    name = get_test_name(failure_xml)
    reason = get_failure_message(failure_xml)
    return FailingTest(klass=klass, name=name, failure_message=reason)


############
# Markdown #
############

def hidden_html_tag(metadata):
    return f"<p align='right' metadata='{metadata}'></p>\n"


def markdown_table(failing_tests):
    return markdown_test_header() + "\n".join(map(markdown_failing_test, failing_tests))


def markdown_test_header():
    return "| Class | Name | Reason |\n|---|---|---|\n"


def markdown_failing_test(failing_test):
    return markdown_table_separator + \
           markdown_table_separator.join(list(failing_test)) + \
           markdown_table_separator


def details_tag(summary, details):
    return f"<details><summary>{summary}</summary><p>\n\n{details}</p></details>"


markdown_table_separator = " | "
markdown_new_paragraph = "\n\n"

####################
# Module Detection #
####################

module_marker_file = "build.gradle"
module_exclusion_list = ['/third_party/.*', '.*/benchmark']
module_dirs = []

def exclude_module(module_path):
    return not any(re.search(exclusion, module_path) for exclusion in module_exclusion_list)


def get_module_dirs(a_dir):
    search_path = os.path.join(a_dir, '**/', module_marker_file)
    marker_files = glob(search_path, recursive=True)
    module_dirs = (os.path.basename(os.path.dirname(mf)) for mf in marker_files)

    return module_dirs


def is_in_module(file, module_name):
    # we assume the file is in the form of "./module/build/..."
    return file.split(os.path.sep)[1] == module_name


def module_of_file(file_path, root_dir):
    all_mods = get_module_dirs(root_dir)
    dir_gen = (dir for dir in file_path.split(os.path.sep) if dir in all_mods)
    return next(dir_gen, None)


def test_results_path_for_type(test_type):
    if test_type == TestType.UNIT_TEST:
        return os.path.join("build", "**", "test-results", "**", "*.xml")
    if test_type == TestType.ANDROID_TEST:
        return os.path.join("build", "**", "*Test-results", "**", "*.xml")

def test_dir_in_module(test_type):
    if test_type == TestType.UNIT_TEST:
        return os.path.join("src", "test")
    if test_type == TestType.ANDROID_TEST:
        return os.path.join("src", "androidTest")


def does_module_have_type_of_tests(module_path, test_type):
    return os.path.exists(os.path.join(module_path, test_dir_in_module(test_type)))


#############################
# Github Comment Formatting #
#############################

def failure_details(results):
    if results.failing_tests:
        return details_tag("Details", markdown_table(results.failing_tests))
    return ""


def emoji_for_result(results):
    if results.failing_tests:
        return ":x:"
    elif results.num_of_test:
        return ":white_check_mark:"
    else:
        return ":warning:"


def test_status_message(results):
    if results.failing_tests:
        return f"{len(results.failing_tests)} out of {results.num_of_test} failed."
    elif results.num_of_test:
        return f"All {results.num_of_test} tests passed."
    else:
        return "No tests have run."


def test_results_comment(modules_test_results):
    res = ""
    for module, result in modules_test_results.items():
        module_res = module_result_comment(module, result)
        if module_res:
            res += f"<tr><td><b> {module.capitalize()} </b></td><td> {module_res} </td></tr>\n"
    return res


def test_type_result_comment(module, result, test_type):
    if not does_module_have_type_of_tests(module, test_type):
        return ""
    emoji = emoji_for_result(result[test_type])
    status = test_status_message(result[test_type])
    details = failure_details(result[test_type])
    return f" {emoji} {test_type.value}: {status} {details}</br>"


def module_result_comment(module, result):
    comment = ""
    comment += test_type_result_comment(module, result, TestType.UNIT_TEST)
    comment += test_type_result_comment(module, result, TestType.ANDROID_TEST)
    return comment


def build_status_comment(modules_test_results):
    comment_header = """
## Lightricks CI status
    
<table>
    """

    comment_footer = """
</table>
    
<p align="right" ${commentSignature()}>
Generated by the Lightricks android jenkins team :hammer:
</p>
    """

    return comment_header + test_results_comment(modules_test_results) + comment_footer


########
# Main #
########

def test_report(test_results_paths):
    failures = []
    test_count = 0
    for test_result in test_results_paths:
        test_count += num_of_tests(test_result)
        failures.extend(get_failing_tests_xmls_from_file(test_result))

    failing_tests = [create_failing_test(failure) for failure in failures]
    return TestReport(test_count, failing_tests)


def test_report_for_type(module_path, test_type):
    results_paths = glob(os.path.join(module_path, test_results_path_for_type(test_type)), recursive=True)
    return test_report(results_paths)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('workspace_dir')
    args = parser.parse_args()
    workspace = args.workspace_dir

    all_modules = get_module_dirs(workspace)
    filtered_modules = filter(exclude_module, all_modules)
    modules_result = {
        module: {
            TestType.UNIT_TEST: test_report_for_type(os.path.join(workspace, module), TestType.UNIT_TEST) ,
            TestType.ANDROID_TEST: test_report_for_type(os.path.join(workspace, module), TestType.ANDROID_TEST)
        }
        for module in filtered_modules
    }

    tests_signature = hidden_html_tag(TESTS_SIGNATURE)
    message.post_comment_on_current_pr(tests_signature +
                                       build_status_comment(modules_result), tests_signature)
