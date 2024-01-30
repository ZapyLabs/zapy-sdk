import asyncio
import functools

from zapy.base.exceptions import HandledError, ZapyError
from zapy.templating.traceback import copy_traceback


class RenderLocationError(ZapyError, HandledError):

    namespace = "render"

    def __init__(self, ex: Exception, location: str):
        super().__init__(f"Error on {location}")
        self.identifier = location
        info = copy_traceback(self, from_exc=ex)
        if info:
            self.context["stacktrace"] = info


def error_location(location: str):
    def decorator(function):
        if not asyncio.iscoroutinefunction(function):

            @functools.wraps(function)
            def wrapper(*args, **kwargs):
                try:
                    return function(*args, **kwargs)
                except Exception as ex:
                    raise RenderLocationError(ex, location) from ex

        else:

            @functools.wraps(function)
            async def wrapper(*args, **kwargs):
                try:
                    return await function(*args, **kwargs)
                except Exception as ex:
                    raise RenderLocationError(ex, location) from ex

        return wrapper

    return decorator
