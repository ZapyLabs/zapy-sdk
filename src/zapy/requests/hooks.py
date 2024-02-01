from dataclasses import dataclass
from typing import Callable
from unittest import TestCase

from zapy.utils.functools import empty_function


@dataclass
class RequestHook:
    pre_request: Callable = empty_function
    post_request: Callable = empty_function
    test: type[TestCase] | None = None


class RequestHookBlueprint:

    def __init__(self) -> None:
        self.request_hook = RequestHook()

    def pre_request(self, func: Callable) -> Callable:
        """
        `pre_request` is a decorator used to intercept and modify `httpx` arguments **before** sending the request.
        This can be used globally or locally, under a request file.

        Read more about it in the
        [Zapy docs - Hooks](https://docs.zapy.dev/sdk/hooks/).


        ## Example

        ```python
        from zapy.requests import hooks, HttpxArguments

        @hooks.pre_request
        async def on_each_request(httpx_args: HttpxArguments):
            httpx_args['auth'] = ('alice', 'ecila123')
            print(httpx_args)
        ```
        """
        self.request_hook.pre_request = func
        return func

    def post_request(self, func: Callable) -> Callable:
        """
        `pre_request` is a decorator used to intercept and modify `httpx` arguments **after** sending the request.
        This can be used globally or locally, under a request file.

        Read more about it in the
        [Zapy docs - Hooks](https://docs.zapy.dev/sdk/hooks/).


        ## Example

        ```python
        from zapy.requests import hooks, HttpxResponse

        @hooks.post_request
        async def after_each_request(httpx_response: HttpxResponse):
            print(httpx_response.data)
        ```
        """
        self.request_hook.post_request = func
        return func

    def test(self, cls: type[TestCase]) -> type[TestCase]:
        self.request_hook.test = cls
        return cls


_global_blueprint = RequestHookBlueprint()


def use_global_hook() -> RequestHook:
    return _global_blueprint.request_hook


pre_request = _global_blueprint.pre_request
post_request = _global_blueprint.post_request
