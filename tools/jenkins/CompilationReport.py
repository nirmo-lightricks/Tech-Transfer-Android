#  Copyright (c) 2019 Lightricks. All rights reserved.
#  Created by Noam Freeman.

import glob
import os
import collections
import re

import project_modules
from BuildReport import ReportEntry, Status

COMPILATION_LOG_PATH_IN_MODULE = os.path.join("build", "logs", "compilerErrors",  "*.txt")

Location = collections.namedtuple('Location', 'file line')
CompilationError = collections.namedtuple('CompilationError', 'location')

def remove_string_begining(string, infix):
    f = string.find(infix)
    if f == -1:
        return string
    return string[f + len(infix):]

###################
###################


def _parse_log(compilation_log_path, workspace):
    with open(compilation_log_path) as f:
        lines = f.readlines()
        errors = []
        for line in lines:
            if ": error:" in line:
               m = re.search("(.*):(\d+): (error|warning): (.*)", line)
               error = CompilationError(Location(m.group(1), m.group(2)))
               errors.append(error)
        return errors

def parse_compilation_errors(compilation_log_paths, workspace):
    return [error
            for file in compilation_log_paths
            for error in _parse_log(file, workspace)
            ]

#################
#################

def markdown_compilation_error(compilation_error, workspace):
    short_path = remove_string_begining(compilation_error.location.file, f"{workspace}/")
    return f"| {short_path} | {compilation_error.location.line} |"


def markdown_table_header(*titles):
    header = "| "
    for title in titles :
        header += str(title) + " | "
    header += "\n"
    separation_line = "|"
    for title in titles:
        separation_line += "---|"
    separation_line += "\n"
    return header + separation_line

def markdown_table(compilation_errors, workspace):
    body = "\n".join(markdown_compilation_error(error, workspace) for error in compilation_errors)
    return markdown_table_header("File", "Row") + body

def compilation_comment(compilation_errors, workspace):
    return markdown_table(compilation_errors, workspace)


def create_compilation_entries(workspace):
    modules = project_modules.get_module_dirs(workspace)

    for module in modules:
        module_name = os.path.basename(module)
        compilation_log_paths = glob.glob(os.path.join(workspace, module, COMPILATION_LOG_PATH_IN_MODULE))
        if not compilation_log_paths:
            # no compilation occured TODO: do we want to continue?
            continue
        compilation_errors = parse_compilation_errors(compilation_log_paths, workspace)

        if not compilation_errors:
            continue
        else:
            status = Status.ERROR
            info = f"there are {len(compilation_errors)} compilation errors"
            details = compilation_comment(compilation_errors, workspace)
            yield ReportEntry(module_name, status, "Compilation", info, details)
