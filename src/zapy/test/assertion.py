from typing import List

from .models import TestResult


def filter_failed_tests(test_result: List[TestResult]):
    failed_tests = [result for result in test_result if result["status"] in ("error", "failure")]
    return failed_tests


class AssertTestResultMixin:

    def assertZapyTestResults(self, test_result: List[TestResult]):
        failed_tests = filter_failed_tests(test_result)
        self.assertEqual([], failed_tests)


def assert_test_result_dict(test_result: List[TestResult]):
    failed_tests = filter_failed_tests(test_result)
    assert [] == failed_tests, stringify_error(failed_tests)


def stringify_error(error: List[TestResult]):
    output = ""
    for err in error:
        output += f"Method: {err['method']}"
        output += f"\n{err['traceback']}\n"
    return output
