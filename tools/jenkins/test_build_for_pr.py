import unittest
from build_for_pr import _get_gradle_arguments, GRADLE_PR_TASK_NAME


class TestBuildForPr(unittest.TestCase):
    def test_large_test(self):
        res = _get_gradle_arguments(["swish"], True, set())
        expected = ["clean", f":swish:{GRADLE_PR_TASK_NAME}"]
        self.assertListEqual(expected, res)

    def test_small_test(self):
        res = _get_gradle_arguments(["swish"], False, set())
        expected = [
            "-Pandroid.testInstrumentationRunnerArguments.notAnnotation=androidx.test.filters.LargeTest",
            "clean",
            f":swish:{GRADLE_PR_TASK_NAME}",
        ]
        self.assertListEqual(expected, res)

    def test_assets(self):
        res = _get_gradle_arguments(["swish", "assets"], True, set(["assets"]))
        expected = ["clean", f":swish:{GRADLE_PR_TASK_NAME}"]
        self.assertListEqual(expected, res)


if __name__ == "__main__":
    unittest.main()
