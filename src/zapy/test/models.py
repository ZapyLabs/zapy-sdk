from typing import Literal, NotRequired

from typing_extensions import TypedDict


class TestResult(TypedDict):
    method: str
    status: Literal["success", "error", "failure"]
    traceback: NotRequired[str]
