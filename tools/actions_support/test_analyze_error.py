import unittest
from pathlib import Path
from analyze_error import analyze_error, ErrorType

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
