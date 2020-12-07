# Copyright (c) 2019 Lightricks. All rights reserved.
# Created by Noam Freeman.
'''
Get list of modules/ applications by calling gradle
'''
import json
from subprocess import run
from typing import cast, List


def get_module_dirs() -> List[str]:
    '''
    Get all gradle modules
    '''
    command_res = run(
        ["./gradlew", "-q", "listProjects"], capture_output=True, check=True, text=True
    )
    modules_list = json.loads(command_res.stdout.splitlines()[-1])
    return cast(List[str], modules_list)


def get_application_dirs() -> List[str]:
    '''
    Get all Android applications
    '''
    command_res = run(
        ["./gradlew", "-q", "listApplications"],
        capture_output=True,
        check=True,
        text=True,
    )
    modules_list = json.loads(command_res.stdout.splitlines()[-1])
    return cast(List[str], modules_list)
