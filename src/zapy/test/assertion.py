import warnings
from typing import Callable, List

from .models import TestResult


def filter_failed_tests(test_result: List[TestResult]) -> List[TestResult]:
    failed_tests = [result for result in test_result if result["status"] in ("error", "failure")]
    return failed_tests


class AssertTestResultMixin:

    assertEqual: Callable  # noqa: N815

    def assert_zapy_test_results(self, test_result: List[TestResult]) -> None:
        """Fails if `test_result` contains an item with `error` or `failure` status.

        Parameters
        ----------
        test_result : List[TestResult]
            The test results of the request.

        Raises
        ------
        AssertionError
            If `test_result` contains an item with `error` or `failure` status.
        """
        failed_tests = filter_failed_tests(test_result)
        self.assertEqual([], failed_tests)

    def assertZapyTestResults(self, test_result: List[TestResult]) -> None:  # noqa: N802
        """This alias will be deprecated in preference of `assert_zapy_test_results`."""
        warnings.warn(
            "Call to deprecated function assertZapyTestResults. Replace it with assert_zapy_test_results.", stacklevel=2
        )
        self.assert_zapy_test_results(test_result)


def assert_test_result_dict(test_result: List[TestResult]) -> None:
    failed_tests = filter_failed_tests(test_result)
    if [] != failed_tests:
        err_msg = stringify_error(failed_tests)
        raise AssertionError(err_msg)


def stringify_error(error: List[TestResult]) -> str:
    output = ""
    for err in error:
        output += f"Method: {err['method']}"
        output += f"\n{err['traceback']}\n"
    return output
