"""
Script which prints all tests sorted by the run time descendant
"""
import argparse
import glob
import re
from typing import cast, List, Tuple
from bs4 import BeautifulSoup, Tag  # type: ignore


def _get_performance_data_of_row(row: Tag) -> Tuple[str, float]:
    test_class = cast(str, row.a.text)
    duration_str = row.find_all("td")[3].text
    parts = [float(part) for part in re.split("[ms]", duration_str) if part]
    if len(parts) == 2:
        duration = 60 * parts[0] + parts[1]
    else:
        duration = parts[0]
    return (test_class, duration)


def _get_performance_data(html_file: str) -> List[Tuple[str, float]]:
    with open(html_file) as html_fh:
        soup = BeautifulSoup(html_fh, "html.parser")
        class_tables = [
            table
            for table in soup.find_all("table")
            if table.th and table.th.text == "Class"
        ]
        class_table = class_tables[0]
        return [
            _get_performance_data_of_row(row)
            for row in class_table.find_all("tr")
            if row.a
        ]


def create_report(reports_dir: str) -> None:
    """
    Create a report which prints all tests sorted by the run time descendant
    """
    pathname = f"{reports_dir}/**/build/reports/androidTests/connected/**/index.html"
    all_results = [
        result
        for html_file in glob.iglob(pathname, recursive=True)
        for result in _get_performance_data(html_file)
    ]
    sorted_results = sorted(all_results, key=lambda x: x[1], reverse=True)
    for sorted_result in sorted_results:
        print(sorted_result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "reports_dir", help="base dir of reports downloaded from github"
    )
    args = parser.parse_args()
    create_report(args.reports_dir)
