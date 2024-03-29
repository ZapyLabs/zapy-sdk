import asyncio
import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, List

import httpx

from zapy.base import Metadata
from zapy.store import Store, use_store
from zapy.templating.traceback import annotate_traceback
from zapy.test import TestResult, run_tests
from zapy.utils import functools

from .context import ZapyRequestContext
from .converter import RequestConverter
from .exceptions import RenderLocationError, error_location
from .hooks import RequestHook, use_global_hook
from .models import HttpxArguments, HttpxResponse, ZapyRequest


@dataclass
class RequesterResponse:
    response: httpx.Response
    test_result: List[TestResult] = field(default_factory=list)


_http_request_signature = inspect.signature(httpx.Client.build_request).parameters


class Requester:

    def __init__(self, zapy_request: ZapyRequest, converter: RequestConverter, client: httpx.AsyncClient):
        self.zapy_request = zapy_request
        self.converter = converter
        self.client = client
        self.__hook_context = {
            Metadata: self.zapy_request.metadata,
            ZapyRequest: self.zapy_request,
        }

    async def make_request(self) -> RequesterResponse:
        httpx_args = self.converter.build_httpx_args()

        # Hook: pre_request
        await self._invoke_hooks_pre_request(httpx_args)

        # send request
        request_parameters, rest_parameters = self._split_parameters(httpx_args)
        request = self.client.build_request(**request_parameters)
        response = await self.client.send(request, **rest_parameters)

        # Hook: post_request
        try:
            await self._invoke_hooks_post_request(response)
        except RenderLocationError as ex:
            ex.context["response"] = response
            raise

        response_wrapper = RequesterResponse(response)

        # Hook: test
        if self.request_hooks.test:
            response_wrapper.test_result = self._run_test(
                httpx_args=httpx_args,
                request=request,
                response=response,
            )

        return response_wrapper

    @error_location("pre_request")
    async def _invoke_hooks_pre_request(self, httpx_args: HttpxArguments) -> None:
        try:
            await self.__call_hook(use_global_hook().pre_request, httpx_args)
            await self.__call_hook(self.request_hooks.pre_request, httpx_args)
        except BaseException as e:
            annotate_traceback(e, self.converter.script, location="hook")
            raise e

    @error_location("post_request")
    async def _invoke_hooks_post_request(self, response: httpx.Response) -> None:
        try:
            await self.__call_hook(use_global_hook().post_request, response)
            await self.__call_hook(self.request_hooks.post_request, response)
        except Exception as e:
            annotate_traceback(e, self.converter.script, location="hook")
            raise e

    def _run_test(
        self, httpx_args: HttpxArguments, request: httpx.Request, response: HttpxResponse
    ) -> list[TestResult]:
        if self.request_hooks.test is None:
            return []

        class RequestMeta(type):
            def __new__(cls, name: str, bases: tuple, attrs: dict) -> type:
                attrs["httpx_args"] = httpx_args
                attrs["request"] = request
                attrs["response"] = response
                return super().__new__(cls, name, bases, attrs)

        class DecoratedClass(self.request_hooks.test, metaclass=RequestMeta):  # type: ignore[name-defined]
            pass

        test_result = run_tests(DecoratedClass).as_list()
        return test_result

    def _split_parameters(self, httpx_args: HttpxArguments) -> tuple[dict, dict]:
        request_parameters, rest_parameters = {}, {}
        for k, v in httpx_args.items():
            if k in _http_request_signature:
                request_parameters[k] = v
            else:
                rest_parameters[k] = v
        return request_parameters, rest_parameters

    async def __call_hook(self, hook: Callable, *args: Any) -> Any:
        result = functools.call_with_signature(hook, *args, kwargs=self.__hook_context)
        if asyncio.iscoroutine(result):
            return await result
        return result

    @property
    def request_hooks(self) -> RequestHook:
        return self.converter.request_hooks


async def send_request(
    zapy_request: ZapyRequest,
    *,
    store: Store | None = None,
    logger: Callable = print,
    client: httpx.AsyncClient | None = None,
) -> RequesterResponse:
    if store is None:
        store = use_store()
    ctx = ZapyRequestContext(
        store=store,
        logger=logger,
    )
    _client = client or httpx.AsyncClient(follow_redirects=True, timeout=None)
    try:
        request = build_request(zapy_request, ctx, client=_client)
        return await request.make_request()
    finally:
        if client is None:
            await _client.aclose()


def build_request(zapy_request: ZapyRequest, ctx: ZapyRequestContext, client: httpx.AsyncClient) -> Requester:
    converter = RequestConverter(zapy_request, ctx)
    requester = Requester(zapy_request, converter, client)

    return requester
