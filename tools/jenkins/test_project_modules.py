import unittest
from build_modified_modules_v2 import (
    get_project_dependencies,
    ProjectModule,
    ModuleType,
)



class ProjectModulesTest(unittest.TestCase):
    def test_asset_module(self):
        module = ProjectModule(
            name="facetune_assets_pack", module_type=ModuleType.ASSET
        )
        dependencies = get_project_dependencies(module)
        self.assertSetEqual(set(), dependencies)

    def test_leaf_module(self):
        module = ProjectModule(name="protobuf", module_type=ModuleType.LIBRARY)
        dependencies = get_project_dependencies(module)
        self.assertSetEqual(set(), dependencies)

    def test_app(self):
        module = ProjectModule(
            name="billing_playground", module_type=ModuleType.LIBRARY
        )
        dependencies = get_project_dependencies(module)
        expected = {
            ProjectModule(name="authentication", module_type=ModuleType.LIBRARY),
            ProjectModule(name="billing", module_type=ModuleType.LIBRARY),
            ProjectModule(name="common", module_type=ModuleType.LIBRARY),
            ProjectModule(name="analytics", module_type=ModuleType.LIBRARY),
        }
        self.assertSetEqual(expected, dependencies)


if __name__ == "__main__":
    unittest.main()
