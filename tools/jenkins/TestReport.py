# Copyright (c) 2019 Lightricks. All rights reserved.
# Created by Noam Freeman.

import collections
import os
import re
import xml.etree.ElementTree as ET
from enum import Enum
from glob import glob

import project_modules
from BuildReport import ReportEntry, Status


class TestType(Enum):
    UNIT_TEST = "unit tests"
    ANDROID_TEST = "android tests"


FailingTest = collections.namedtuple('FailingTest', 'klass name failure_message')

TestReport = collections.namedtuple('TestReport', 'num_of_test failing_tests')

######################
# xml report parsing #
######################

def _is_test_failing(test_case_xml):
    return any(child.tag == 'failure' for child in test_case_xml)


def _get_test_cases(report_xml):
    return (child for child in report_xml if child.tag == "testcase")


def _get_test_name(test_xml):
    return test_xml.attrib["name"]


def _get_test_class(test_xml):
    return test_xml.attrib["classname"]


def _get_failure_stack(test_xml):
    return [child for child in test_xml if child.tag == "failure"][0]


def _get_failure_message(test_xml):
    return _get_failure_stack(test_xml).text.splitlines()[0]


def _get_test_cases_from_file(junit_xml_path):
    tree = ET.parse(junit_xml_path)
    root = tree.getroot()
    tests = _get_test_cases(root)
    return tests


def num_of_tests(junit_xml_path):
    tests_xml_objects = _get_test_cases_from_file(junit_xml_path)
    return sum(True for test in tests_xml_objects)


def get_failing_tests_xmls_from_file(junit_xml_path):
    tests_xml_objects = _get_test_cases_from_file(junit_xml_path)
    failures = filter(_is_test_failing, tests_xml_objects)
    return failures


def create_failing_test(failure_xml):
    klass = _get_test_class(failure_xml)
    name = _get_test_name(failure_xml)
    reason = _get_failure_message(failure_xml)
    return FailingTest(klass=klass, name=name, failure_message=reason)


############
# Markdown #
############

def _markdown_table(failing_tests):
    return _markdown_test_header() + "\n".join(map(_markdown_failing_test, failing_tests))


def _markdown_test_header():
    return "| Class | Name | Reason |\n|---|---|---|\n"


def _markdown_failing_test(failing_test):
    return markdown_table_separator + \
           markdown_table_separator.join(list(failing_test)) + \
           markdown_table_separator

markdown_table_separator = " | "

####################
# Module Detection #
####################

module_marker_file = "build.gradle"
_module_exclusion_list = ['/third_party/.*', '.*/benchmark']

def _exclude_module(module_path):
    return not any(re.search(exclusion, module_path) for exclusion in _module_exclusion_list)

def is_in_module(file, module_name):
    # we assume the file is in the form of "./module/build/..."
    return file.split(os.path.sep)[1] == module_name


def module_of_file(file_path, root_dir):
    all_mods = project_modules.get_module_dirs(root_dir)
    dir_gen = (dir for dir in file_path.split(os.path.sep) if dir in all_mods)
    return next(dir_gen, None)


def _test_results_path_for_type(test_type):
    if test_type == TestType.UNIT_TEST:
        return os.path.join("build", "**", "test-results", "**", "*.xml")
    if test_type == TestType.ANDROID_TEST:
        return os.path.join("build", "**", "*Test-results", "**", "*.xml")


def _test_dir_in_module(test_type):
    if test_type == TestType.UNIT_TEST:
        return os.path.join("src", "test")
    if test_type == TestType.ANDROID_TEST:
        return os.path.join("src", "androidTest")


def _does_module_have_type_of_tests(module_path, test_type):
    return os.path.exists(os.path.join(module_path, _test_dir_in_module(test_type)))


#############################
# Github Comment Formatting #
#############################

def _failure_details(results):
    if results.failing_tests:
        return _markdown_table(results.failing_tests)
    return ""


def _status_for_result(results):
    if results.failing_tests:
        return Status.ERROR
    elif results.num_of_test:
        return Status.OK
    else:
        return Status.WARNING


def _test_status_message(results):
    if results.failing_tests:
        return f"{len(results.failing_tests)} out of {results.num_of_test} failed."
    elif results.num_of_test:
        return f"All {results.num_of_test} tests passed."
    else:
        return "No tests have run."

def _report_entry_for_test_type(module, result, test_type):
    emoji = _status_for_result(result)
    status = _test_status_message(result)
    details = _failure_details(result)
    stage = test_type.value
    return ReportEntry(module, emoji, stage, status, details)

########
# Main #
########

def _test_report(test_results_paths):
    failures = []
    test_count = 0
    for test_result in test_results_paths:
        test_count += num_of_tests(test_result)
        failures.extend(get_failing_tests_xmls_from_file(test_result))

    failing_tests = [create_failing_test(failure) for failure in failures]
    return TestReport(test_count, failing_tests)


def _test_report_for_type(module_path, test_type):
    results_paths = glob(os.path.join(module_path, _test_results_path_for_type(test_type)), recursive=True)
    return _test_report(results_paths)

def _create_test_entries_for_all_modules(workspace):
    all_modules = project_modules.get_module_dirs(workspace)
    filtered_modules = filter(_exclude_module, all_modules)

    for module in filtered_modules:
        module_path = os.path.join(workspace, module)
        module_name = os.path.basename(module)
        if _does_module_have_type_of_tests(module, TestType.UNIT_TEST):
            test_entry = _report_entry_for_test_type(module_name,
                _test_report_for_type(module_path, TestType.UNIT_TEST), TestType.UNIT_TEST)
            yield test_entry

        if _does_module_have_type_of_tests(module, TestType.ANDROID_TEST):
            android_test_entry = _report_entry_for_test_type(module_name,
                _test_report_for_type(module_path, TestType.ANDROID_TEST), TestType.ANDROID_TEST)
            yield android_test_entry

def generate_report_entries(workspace):
    return _create_test_entries_for_all_modules(workspace)
