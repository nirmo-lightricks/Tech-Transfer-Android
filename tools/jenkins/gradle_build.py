# Copyright (c) 2020 Lightricks. All rights reserved.
# Created by Geva Kipper.

import subprocess
from typing import List


def execute_gradle(tasks: List[str], excluded_tasks: List[str] = None, wrapper_path: str = "./gradlew"):
    """
    Executes gradle build with the given parameters, and returns the error code.
    """
    args = [wrapper_path] + tasks
    for task_name in excluded_tasks:
        args.append("-x")
        args.append(task_name)

    print("[+] Executing: " + " ".join(args), flush=True)  # If we don't flush, jenkins will print this out of order
    return subprocess.run(args).returncode
