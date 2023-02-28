import unittest
from pathlib import Path
from analyze_error import BuildError, analyze_error, ErrorType

test_files_dir = Path(__file__).parent / "test_files"

class AnalyzeError(unittest.TestCase):
    def test_non_existsing_file(self):
        res = analyze_error(Path("non_existing_file.txt"))
        self.assertEqual([], res)

    def test_aapt_error(self):
        res = analyze_error(test_files_dir / "aapt.log")
        self.assertTrue(res)
        self.assertEqual(ErrorType.AAPT, res[0].error_type)
        self.assertEqual("facetune", res[0].project)

    def test_unittest_error(self):
        def extraction_fun(project:str, task:str)->BuildError:
            self.assertEqual("videoleap", project)
            self.assertEqual("testDebugUnitTest", task)
            return BuildError(project="videoleap", error_type=ErrorType.UNIT_TEST, details=[])
        res = analyze_error(log_file=test_files_dir / "unit_test_failure.log", unit_test_failure_extraction_fun=extraction_fun)
        self.assertTrue(res)
        self.assertEqual(ErrorType.UNIT_TEST, res[0].error_type)
        self.assertEqual("videoleap", res[0].project)

    def test_androidtest_error(self):
        def extraction_fun(project:str, task:str)->BuildError:
            self.assertEqual("swish", project)
            self.assertEqual("connectedDebugAndroidTest", task)
            return BuildError(project="swish", error_type=ErrorType.ANDROID_TEST, details=[])

        res = analyze_error(log_file=test_files_dir / "android_test_failure.log", unit_test_failure_extraction_fun=extraction_fun)
        self.assertTrue(res)
        self.assertEqual(ErrorType.ANDROID_TEST, res[0].error_type)
        self.assertEqual("swish", res[0].project)

    def test_debugunittest_compilation_error(self):
        res = analyze_error(log_file=test_files_dir / "debug_unit_test_compilation_failure.log")
        self.assertTrue(res)
        self.assertEqual(ErrorType.COMPILATION, res[0].error_type)
        self.assertEqual("analytics", res[0].project)
