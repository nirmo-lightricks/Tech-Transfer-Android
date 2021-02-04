# Copyright (c) 2020 Lightricks. All rights reserved.
# Created by Geva Kipper.
"""
Wrapper for running gradle scripts
"""
import subprocess
from typing import List, Optional


def execute_gradle(
    tasks: List[str],
    excluded_tasks: Optional[List[str]] = None,
    wrapper_path: str = "./gradlew",
) -> None:
    """
    Executes gradle build with the given parameters, and returns the error code.
    """
    args = [wrapper_path] + tasks
    excluded_tasks = excluded_tasks or []
    for task_name in excluded_tasks:
        args.append("-x")
        args.append(task_name)

    print(
        "[+] Executing: " + " ".join(args), flush=True
    )  # If we don't flush, jenkins will print this out of order
    subprocess.run(args, check=True)
