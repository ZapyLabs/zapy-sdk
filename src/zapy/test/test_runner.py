import unittest
import unittest.case
from typing import Any, List
from unittest.runner import TextTestResult

from .models import TestResult as TestResultModel


class TestResult(TextTestResult):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.successes: list[Any] = []

    def addSuccess(self, test: Any) -> None:  # noqa: N802
        super().addSuccess(test)
        self.successes.append(test)

    def as_list(self) -> List[TestResultModel]:
        successes = [
            TestResultModel(
                method=test._testMethodName,
                status="success",
            )
            for test in self.successes
        ]
        errors = [
            TestResultModel(
                method=test._testMethodName,
                traceback=traceback_str,
                status="error",
            )
            for test, traceback_str in self.errors
        ]
        failures = [
            TestResultModel(
                method=test._testMethodName,
                traceback=traceback_str,
                status="failure",
            )
            for test, traceback_str in self.failures
        ]
        return successes + errors + failures


def run_tests(*test_classes: type[unittest.TestCase]) -> TestResult:
    loader = unittest.TestLoader()
    suites_list = (loader.loadTestsFromTestCase(test_class) for test_class in test_classes)
    test_suit = unittest.TestSuite(suites_list)

    test_runner = unittest.runner.TextTestRunner(resultclass=TestResult)
    test_result = test_runner.run(test_suit)

    return test_result  # type: ignore
