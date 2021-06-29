"""
this module is intended to deal with parsing of xml test results for both android and unit test
"""
from pathlib import Path
from typing import List
import xml.etree.ElementTree as ET


def _extract_error_message_from_failure_node(test_node: ET.Element) -> str:
    test_name = test_node.get("name")
    test_class = test_node.get("classname")
    failure_node = test_node.find("failure")
    if failure_node is None:
        raise ValueError(f"node {test_name} does not have failure")
    failure = failure_node.text
    return f"{test_class} - {test_name} failed: {failure}"


def _extract_test_failure_from_test_file(test_file: Path) -> List[str]:
    doc = ET.parse(test_file)

    # playing around with xpath
    failing_tests = doc.findall("./testcase/failure/..")
    return [
        _extract_error_message_from_failure_node(failing_test)
        for failing_test in failing_tests
    ]


def extract_test_failure_from_directory(unit_test_directory: Path) -> List[str]:
    """
    parse all test xml files from directory to get the failures
    """
    test_files = unit_test_directory.glob("*.xml")
    return [
        error
        for test_file in test_files
        for error in _extract_test_failure_from_test_file(test_file)
    ]
