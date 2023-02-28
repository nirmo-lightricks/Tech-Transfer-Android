import argparse
import sys
import xml.etree.ElementTree as etree
from typing import List
import os
import re


def files_in_dir(submodule: str, build_subdir: str, pattern: str) -> List[str]:
    parent = os.path.join(submodule, "build", build_subdir)
    if not os.path.isdir(parent):
        return []

    return [os.path.join(parent, candidate) for candidate in os.listdir(parent)
            if re.match(pattern, candidate, re.IGNORECASE)]


def is_submodule(directory: str):
    return os.path.isdir(os.path.join(directory, "build")) and \
           any(f.startswith("build.gradle") for f in os.listdir(directory))


def verify_detekt(submodules: List[str]) -> List[str]:
    filesToCheck = [file_in_dir for submodule in submodules
                    for file_in_dir in files_in_dir(submodule, "detekt-results", "detekt\\.xml")]

    faults = []
    for file in filesToCheck:
        xmlRoot = etree.parse(file).getroot()
        if xmlRoot.find("file") is not None:
            faults.append(file)

    return faults


def verify_lint(submodules: List[str]) -> List[str]:
    filesToCheck = [file_in_dir for submodule in submodules
                    for file_in_dir in files_in_dir(submodule, "reports", "lint-results-\\w*Debug.xml")]

    allowedSeverities = ["information"]
    faults = []
    for file in filesToCheck:
        xmlRoot = etree.parse(file).getroot()
        issue = xmlRoot.find("issue")

        severityRaw = issue.get("severity") if issue is not None else None
        severity = severityRaw.lower() if severityRaw is not None else None

        if issue is not None and severity not in allowedSeverities:
            faults.append(file)

    return faults


if __name__ == '__main__':
    argsParser = argparse.ArgumentParser()
    argsParser.add_argument("--root_dir", required=False, help="Project root dir", default=".")
    args = argsParser.parse_args()
    rootDir = args.root_dir

    submodules_paths = sorted(os.path.join(rootDir, directory)
                              for directory in os.listdir(rootDir) if is_submodule(directory))

    detekt_faults = verify_detekt(submodules_paths)
    lint_faults = verify_lint(submodules_paths)

    print("Faults:")
    print("-" * 20)
    print("Detekt: ")
    print("-" * 20)
    for fault in detekt_faults:
        print(fault)

    print("-" * 20)
    print("Lint: ")
    print("-" * 20)
    for fault in lint_faults:
        print(fault)

    retCode = 0
    if detekt_faults:
        retCode += 1
    if lint_faults:
        retCode += 2

    sys.exit(retCode)
