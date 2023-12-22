from typing import List
from dataclasses import dataclass, field
import inspect
import asyncio

import httpx

from zapy.base import Metadata
from zapy.test import run_tests, TestResult
from zapy.store import Store, use_store
from zapy.utils import functools
from zapy.templating.traceback import annotate_traceback

from .exceptions import error_location, RenderLocationException
from .models import ZapyRequest, HttpxArguments
from .context import ZapyRequestContext
from .hooks import use_global_hook
from .converter import RequestConverter


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
        except RenderLocationException as ex:
            ex.context["response"] = response
            raise

        response_wrapper = RequesterResponse(response)

        # Hook: test
        if self.request_hooks.test:
            response_wrapper.test_result = self._run_test(
                httpx_args = httpx_args,
                request = request,
                response = response,
            )

        return response_wrapper

    @error_location('pre_request')
    async def _invoke_hooks_pre_request(self, httpx_args: dict):
        try:
            await self.__call_hook(use_global_hook().pre_request, httpx_args)
            await self.__call_hook(self.request_hooks.pre_request, httpx_args)
        except BaseException as e:
            annotate_traceback(e, self.converter.script, location='hook')
            raise e

    @error_location('post_request')
    async def _invoke_hooks_post_request(self, response: httpx.Response):
        try:
            await self.__call_hook(use_global_hook().post_request, response)
            await self.__call_hook(self.request_hooks.post_request, response)
        except Exception as e:
            annotate_traceback(e, self.converter.script, location='hook')
            raise e

    def _run_test(self, **args) -> dict:
        class RequestMeta(type):
            def __new__(cls, name, bases, attrs):
                for k, v in args.items():
                    attrs[k] = v
                return super().__new__(cls, name, bases, attrs)
        class DecoratedClass(self.request_hooks.test, metaclass=RequestMeta):
            pass

        test_result = run_tests(DecoratedClass).as_list()
        return test_result

    def _split_parameters(self, httpx_args: HttpxArguments):
        request_parameters, rest_parameters = dict(), dict()
        for k, v in httpx_args.items():
            if k in _http_request_signature:
                request_parameters[k] = v
            else:
                rest_parameters[k] = v
        return request_parameters, rest_parameters

    async def __call_hook(self, hook, *args):
        result = functools.call_with_signature(hook, *args, kwargs=self.__hook_context)
        if asyncio.iscoroutine(result):
            return await result
        return result

    @property
    def request_hooks(self):
        return self.converter.request_hooks

async def send_request(zapy_request: ZapyRequest, *, store: Store | None = None, logger=print, client: httpx.AsyncClient | None =None) -> RequesterResponse:
    if store is None:
        store = use_store()
    ctx = ZapyRequestContext(
        store = store,
        logger = logger,
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
