import unittest
import unittest.case
from typing import List
from unittest.runner import TextTestResult

from .models import TestResult


class TestResult(TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.successes = []

    def addSuccess(self, test):  # noqa: N802
        super().addSuccess(test)
        self.successes.append(test)

    def as_list(self) -> List[TestResult]:
        successes = [
            {
                "method": test._testMethodName,
                "status": "success",
            }
            for test in self.successes
        ]
        errors = [
            {
                "method": test._testMethodName,
                "traceback": traceback_str,
                "status": "error",
            }
            for test, traceback_str in self.errors
        ]
        failures = [
            {
                "method": test._testMethodName,
                "traceback": traceback_str,
                "status": "failure",
            }
            for test, traceback_str in self.failures
        ]
        return successes + errors + failures


def run_tests(*test_classes) -> TestResult:
    loader = unittest.TestLoader()
    suites_list = (loader.loadTestsFromTestCase(test_class) for test_class in test_classes)
    test_suit = unittest.TestSuite(suites_list)

    test_runner = unittest.runner.TextTestRunner(resultclass=TestResult)
    test_result = test_runner.run(test_suit)

    return test_result
