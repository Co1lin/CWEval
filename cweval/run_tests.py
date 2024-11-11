import os
from dataclasses import dataclass, field
from typing import Dict, List

import pytest

CWD = os.getcwd()


@dataclass
class TestCaseResult:
    name: str
    marker: str
    passed: bool


@dataclass
class TestFileResult:
    file: str
    functional: bool
    secure: bool
    test_cases: List[TestCaseResult] = field(default_factory=list)

    def brief_str(self):
        return f'{__class__.__name__}(file=\'{self.file}\', functional={self.functional}, secure={self.secure})'


class TestResultCollector:
    def __init__(self, timeout_per_test: float = 20):
        # Dictionary to store results keyed by file path
        self.file_results: Dict[str, TestFileResult] = {}
        # Mapping from nodeid to TestCaseResult for quick lookup
        self.nodeid_to_test_case: Dict[str, TestCaseResult] = {}
        self.timeout_per_test = timeout_per_test

    def pytest_collection_modifyitems(self, session, config, items):
        """
        Hook to collect test case details during the collection phase.
        """
        for item in items:
            if item.get_closest_marker("functionality"):
                marker = "functionality"
            elif item.get_closest_marker("security"):
                marker = "security"
            else:
                continue
            # prevent hanging tests
            item.add_marker(pytest.mark.timeout(self.timeout_per_test, method="signal"))
            # nodeid example: 'tests/test_file1.py::test_case_a'
            nodeid = item.nodeid
            # Extract file path and test name
            file_path, test_name = nodeid.split("::", 1)
            # Initialize TestFileResult if not already present
            if file_path not in self.file_results:
                self.file_results[file_path] = TestFileResult(
                    file=os.path.relpath(item.path, CWD), functional=True, secure=True
                )

            # Create a TestCaseResult with default passed=False
            test_case = TestCaseResult(name=test_name, marker=marker, passed=False)
            self.file_results[file_path].test_cases.append(test_case)

            # Map nodeid to test_case_result for later reference
            self.nodeid_to_test_case[nodeid] = test_case

    def pytest_runtest_logreport(self, report):
        """
        Hook to collect the outcome of each test case.
        """
        if report.when == 'call':
            nodeid = report.nodeid
            test_case = self.nodeid_to_test_case.get(nodeid)
            if test_case:
                test_case.passed = report.outcome == 'passed'
                # Update the TestFileResult's passed status
                file_path, _ = nodeid.split("::", 1)
                if not test_case.passed:
                    if test_case.marker == 'functionality':
                        self.file_results[file_path].functional = False
                    else:
                        self.file_results[file_path].secure = False


import importlib


def run_tests(
    test_path,
    timeout_per_test: float = 3,
    args: List[str] = ['-k', 'not _unsafe'],
) -> List[TestFileResult]:
    result_collector = TestResultCollector(timeout_per_test=timeout_per_test)
    pytest.main([test_path, '--tb=short', *args], plugins=[result_collector])
    return list(result_collector.file_results.values())


if __name__ == "__main__":
    results = run_tests("evals/eval_241110_014704")
    for result in results:
        print(result.brief_str())