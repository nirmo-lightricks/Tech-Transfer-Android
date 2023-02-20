import unittest

from build_modified_modules_v2 import _get_modules_to_build

BIG_MODULE_SET = {
    "billing",
    "video_engine",
    "swish",
    "facetune",
    "videoleap",
    "authentication",
    "quickshot",
    "pixaloop",
    "video_engine_playground",
}

# This test takes a lot of time because gradle calculations
class TestStringMethods(unittest.TestCase):
    def test_library(self):
        modules = _get_modules_to_build({"common"})
        self.assertTrue(modules.issuperset(BIG_MODULE_SET))

    def test_application(self):
        modules = _get_modules_to_build({"swish"})
        self.assertEqual({"swish"}, modules)

    def test_asset_pack(self):
        modules = _get_modules_to_build({"facetune_asset_packs"})
        self.assertEqual({"facetune", "facetune_asset_packs"}, modules)

    def test_non_module(self):
        modules = _get_modules_to_build({"tools"})
        self.assertTrue(modules.issuperset(BIG_MODULE_SET))


if __name__ == "__main__":
    unittest.main()
