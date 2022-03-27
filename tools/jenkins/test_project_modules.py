import unittest
from typing import List
from build_modified_modules_v2 import (
    get_project_dependencies,
    ProjectModule,
    ModuleType,
)
from project_modules import get_project_modules


def _get_module_by_name(name: str) -> ProjectModule:
    all_modules = get_project_modules()
    return next(module for module in all_modules if module.name == name)


class ProjectModulesTest(unittest.TestCase):
    def test_asset_module(self):
        module = _get_module_by_name("facetune_asset_packs")
        dependencies = get_project_dependencies(module)
        self.assertSetEqual(set(), dependencies)

    def test_leaf_module(self):
        module = _get_module_by_name("protobuf")
        dependencies = get_project_dependencies(module)
        self.assertSetEqual(set(), dependencies)

    def test_app(self):
        module = _get_module_by_name("video_engine_playground")
        dependencies = get_project_dependencies(module)
        expected = {
            _get_module_by_name("common"),
            _get_module_by_name("video_engine"),
            _get_module_by_name("opencv-android"),
            _get_module_by_name("render"),
            _get_module_by_name("analytics")
        }
        self.assertSetEqual(expected, dependencies)


if __name__ == "__main__":
    unittest.main()
