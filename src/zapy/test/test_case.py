import unittest

from httpx import Request, Response


class TestCase(unittest.TestCase):

    httpx_args: dict
    request: Request
    response: Response

    def assertBetween(self, x, lo, hi):
        if not (lo <= x <= hi):
            raise AssertionError(f"{x} not between {lo} and {hi}")
