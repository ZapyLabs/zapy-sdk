import functools
import asyncio

from zapy.base.exceptions import ZapyException, HandledException
from zapy.templating.traceback import copy_traceback

class RenderLocationException(ZapyException, HandledException):

    namespace = "render"

    def __init__(self, ex, location):
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
                    raise RenderLocationException(ex, location)
        else:
            @functools.wraps(function)
            async def wrapper(*args, **kwargs):
                try:
                    return await function(*args, **kwargs)
                except Exception as ex:
                    raise RenderLocationException(ex, location)
        return wrapper
    return decorator
