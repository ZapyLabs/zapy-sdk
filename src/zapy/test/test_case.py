import unittest
import warnings

from httpx import Request, Response


class TestCase(unittest.TestCase):

    httpx_args: dict
    request: Request
    response: Response

    def assert_between(self, x, lo, hi):
        """Verifies `lo <= x <= hi`.
        Fails if `x` is not within the defined bounds.

        Parameters
        ----------
        x : any
            The value that should be within defined bounds.

        lo : any
            The lower bound, inclusive.

        hi : any
            The upper bound, inclusive.

        Raises
        ------
        AssertionError
            If `x` is not within the defined bounds.
        """
        if not (lo <= x <= hi):
            err_msg = f"{x} not between {lo} and {hi}"
            raise AssertionError(err_msg)

    def assertBetween(self, x, lo, hi):  # noqa: N802
        """This alias will be deprecated in preference of `assert_between`."""
        warnings.warn("Call to deprecated function assertBetween. Replace it with assert_between.", stacklevel=2)
        self.assert_between(x, lo, hi)
