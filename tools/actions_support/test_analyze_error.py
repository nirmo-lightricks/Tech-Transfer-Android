import unittest
from pathlib import Path
from analyze_error import analyze_error

class AnalyzeError(unittest.TestCase):
    def test_non_existsing_file(self):
        res = analyze_error(Path("non_existing_file.txt"))
        self.assertEqual([], res)