# Copyright (c) 2019 Lightricks. All rights reserved.
# Created by Noam Freeman.
"""
Get list of modules/ applications by calling gradle
"""
import hashlib
import json
import re
import shelve
from functools import lru_cache
from subprocess import run
from dataclasses import dataclass
from pathlib import Path
from typing import cast, List, Dict, Union, Set
from enum import Enum

SHELVE_FILE_NAME = "project_dependencies.db"


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
        """
        according to module info from gradle returns appropriate enum
        """
        if module_info["isAssetModule"]:
            return ModuleType.ASSET
        if module_info["isLibraryModule"]:
            return ModuleType.LIBRARY
        if module_info["isApplicationModule"]:
            return ModuleType.APPLICATION
        raise Exception(f"cant find type of {module_info}")


@dataclass(eq=True, frozen=True)
class ProjectModule:
    """
    Data class holding all data needed for running Prs on module
    """

    name: str
    module_type: ModuleType
    build_file: Path

    @staticmethod
    # pylint: disable=E1136
    def get_project_module_from_project_info(
        module_info: Dict[str, Union[str, bool]]
    ) -> "ProjectModule":
        """
        given the module info returns the ProjectModule
        """
        # Remove the ":" prefix if needed.
        _name = cast(str, module_info["name"])
        if _name.startswith(":"):
            _name = _name[1:]
        build_file = cast(str, module_info["buildFile"])

        return ProjectModule(
            name=_name,
            module_type=ModuleType.get_module_type(module_info),
            build_file=Path(build_file),
        )


@lru_cache()
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

    return [module.name.replace(":", "/") for module in get_project_modules()]


def _get_module_dependencies_from_gradle(module: str) -> Set[ProjectModule]:
    cmd = run(
        [
            "./gradlew",
            "-q",
            f"{module}:dependencies",
        ],
        capture_output=True,
        check=True,
        text=True,
    )
    pattern = re.compile(r"--- project :([\w-]+)")
    match_gen = (pattern.search(line) for line in cmd.stdout.splitlines())
    dependencies = {match.groups()[0] for match in match_gen if match} - {module}
    project_modules = {module.name: module for module in get_project_modules()}
    return {project_modules[dependency] for dependency in dependencies}


def _get_cached_module_key(module: ProjectModule) -> str:
    with open(module.build_file, "rb") as build_fh:
        return hashlib.md5(build_fh.read()).hexdigest()


def get_project_dependencies(module: ProjectModule) -> Set[ProjectModule]:
    """
    Given a project module returns the dependencies of the modules
    """
    if module.module_type == ModuleType.ASSET:
        return set()
    with shelve.open(SHELVE_FILE_NAME, "c") as dependencies_cache:
        key = _get_cached_module_key(module)
        dependencies = cast(Set[ProjectModule], dependencies_cache.get(key))
        if dependencies is None:
            dependencies = _get_module_dependencies_from_gradle(module.name)
            dependencies_cache[key] = dependencies
    return dependencies
