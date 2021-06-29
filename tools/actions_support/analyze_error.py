"""
This script is used to analyze the errors in a gradle build log file.
It is used currently to make the error analysis easier, but there is a much
greater potential, like finding flaky tests
"""
import argparse
import logging
import os
import re
import traceback
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import List, TextIO
from slack_message import slack_message
from test_analyzer import extract_test_failure_from_directory

logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)


class ErrorType(Enum):
    """
    Representation of error types
    """

    ANDROID_TEST = auto()
    COMPILATION = auto()
    UNIT_TEST = auto()


@dataclass
class BuildError:
    """
    Represntation of build errors. The class could be more fine grained
    but this is a starting point
    """

    project: str
    error_type: ErrorType
    details: List[str]


def _extract_compilation_error(project: str, log_fh: TextIO) -> BuildError:
    compilation_errors: List[str] = []
    for line in log_fh:
        if re.match(r"\d+\s+errors", line):
            return BuildError(project, ErrorType.COMPILATION, compilation_errors)
        if line:
            compilation_errors.append(line)
    return BuildError(project, ErrorType.COMPILATION, compilation_errors)


def _extract_unit_test_failures_from_task(project: str, task_name: str) -> BuildError:
    test_dir = Path(project) / "build/test-results" / task_name
    error_details = extract_test_failure_from_directory(test_dir)
    return BuildError(
        project=project, error_type=ErrorType.UNIT_TEST, details=error_details
    )


def _extract_android_test_failures_from_task(
    project: str, task_name: str
) -> BuildError:
    report_base_dir = Path(project) / "build/outputs/androidTest-results/connected"
    flavors_dir = report_base_dir / "flavors"
    if flavors_dir.exists():
        test_dir = next(
            dir
            for dir in flavors_dir.glob("*")
            if task_name.startswith(f"connected{dir.name.title()}")
        )
    else:
        test_dir = report_base_dir

    error_details = extract_test_failure_from_directory(test_dir)
    return BuildError(
        project=project, error_type=ErrorType. ANDROID_TEST, details=error_details
    )


def _slack_github_actions_analysis_error(
    text: str, github_run_id: str, webhook: str
) -> None:
    url = f"https://github.com/Lightricks/facetune-android/actions/runs/{github_run_id}"
    message = f"{text}\n For more details visit {url}"
    slack_message(text=message, webhook=webhook)


def _print_build_error(build_error: BuildError) -> None:
    print(f"project:{build_error.project}, error type:{build_error.error_type}:")
    print("Details:")
    for detail in build_error.details:
        print(detail)
    print("*" * 100)


def analyze_error(log_file: Path) -> List[BuildError]:
    """
    Main function which takes a log file and finds all gradle task
    errors
    """
    build_errors = []
    with open(log_file) as log_fh:
        for log_line in log_fh:
            match = re.search(r"Task\s+:(.+?):(.+)\s+FAILED", log_line)
            if match:
                project, task = match.groups()
                if task.startswith("compile") or task.startswith("kapt"):
                    build_errors.append(_extract_compilation_error(project, log_fh))
                if task.startswith("test"):
                    build_errors.append(
                        _extract_unit_test_failures_from_task(project, task)
                    )
                if task.startswith("connected"):
                    build_errors.append(
                        _extract_android_test_failures_from_task(project, task)
                    )
    return build_errors


def _run(log_file: str, run_id: str, slack_webhook: str) -> None:
    try:
        res = analyze_error(Path(log_file))
        if res:
            for build_error in res:
                _print_build_error(build_error)
        else:
            _slack_github_actions_analysis_error(
                "no errors found but workflow failed", run_id, slack_webhook
            )
    except Exception:  # pylint: disable=W0703
        stack_trace = f"{traceback.format_exc()}"
        _slack_github_actions_analysis_error(stack_trace, run_id, slack_webhook)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("log_file")
    parser.add_argument("github_run_id")
    args = parser.parse_args()
    _run(
        log_file=args.log_file,
        run_id=args.github_run_id,
        slack_webhook=os.environ["webhook"],
    )
