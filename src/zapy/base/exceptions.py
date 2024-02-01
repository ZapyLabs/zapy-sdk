from typing import Any


class HandledError(Exception):
    pass


class ZapyError(Exception):
    namespace: str
    identifier: str
    context: dict[str, Any]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.context = {}

    @property
    def error_type(self) -> str:
        return f"{self.namespace}:{self.identifier}"
