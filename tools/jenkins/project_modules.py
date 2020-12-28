# Copyright (c) 2019 Lightricks. All rights reserved.
# Created by Noam Freeman.
"""
Get list of modules/ applications by calling gradle
"""
import json
from subprocess import run
from dataclasses import dataclass
from typing import cast, List, Dict, Union
from enum import Enum


class ModuleType(Enum):
    """
    Describes the type of the android module
    """

    LIBRARY = 1
    APPLICATION = 2
    ASSET = 3
    @staticmethod
    # pylint: disable=E1136
    def get_module_type(module_info: Dict[str, Union[str, bool]]) -> "ModuleType":
        '''
        according to module info from gradle returns appropriate enum
        '''
        if module_info["isAssetModule"]:
            return ModuleType.ASSET
        if module_info["isLibraryModule"]:
            return ModuleType.LIBRARY
        if module_info["isApplicationModule"]:
            return ModuleType.APPLICATION
        raise Exception(f"cant find type of {module_info}")


@dataclass
class ProjectModule:
    """
    Data class holding all data needed for running Prs on module
    """

    name: str
    module_type: ModuleType

    @staticmethod
    # pylint: disable=E1136
    def get_project_module_from_project_info(module_info: Dict[str, Union[str, bool]]
    ) -> "ProjectModule":
        """
        given the module info returns the ProjectModule
        """
        return ProjectModule(
            name=cast(str, module_info["name"]),
            module_type=ModuleType.get_module_type(module_info),
        )


def get_project_modules() -> List[ProjectModule]:
    """
    Get all gradle modules
    """
    command_res = run(
        ["./gradlew", "-q", "listProjects"], capture_output=True, check=True, text=True
    )
    modules_info_list = json.loads(command_res.stdout.splitlines()[-1])
    return [
        ProjectModule.get_project_module_from_project_info(module_info)
        for module_info in modules_info_list
    ]


def get_module_dirs() -> List[str]:
    """
    Get all gradle module directories
    """

    return [module.name for module in get_project_modules()]
