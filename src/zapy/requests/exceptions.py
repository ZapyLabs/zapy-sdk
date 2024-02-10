import asyncio
import functools
from typing import Any, Callable, TypedDict, TypeVar, cast

from zapy.base.exceptions import HandledError, ZapyError
from zapy.templating.traceback import TracebackInfo, copy_traceback

from .models import HttpxResponse


class RenderLocationContext(TypedDict):
    stacktrace: TracebackInfo
    response: HttpxResponse


class RenderLocationError(ZapyError, HandledError):

    namespace = "render"
    context: RenderLocationContext | dict[str, Any]  # type: ignore[assignment]

    def __init__(self, ex: Exception, location: str):
        super().__init__(f"Error on {location}")
        self.identifier = location
        info = copy_traceback(self, from_exc=ex)
        if info:
            self.context["stacktrace"] = info


T = TypeVar("T", bound=Callable[..., Any])


def error_location(location: str) -> Callable[[T], T]:
    def decorator(function: T) -> T:
        if not asyncio.iscoroutinefunction(function):

            @functools.wraps(function)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    return function(*args, **kwargs)
                except Exception as ex:
                    raise RenderLocationError(ex, location) from ex

        else:

            @functools.wraps(function)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    return await function(*args, **kwargs)
                except Exception as ex:
                    raise RenderLocationError(ex, location) from ex

        return cast(T, wrapper)

    return decorator
