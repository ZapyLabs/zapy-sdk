from __future__ import annotations

import typing
from pathlib import Path

from httpx import _types as httpx_types
from httpx._client import AsyncClient as HttpxAsyncClient
from httpx._client import Response as HttpxResponse
from httpx._client import UseClientDefault
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from zapy.__about__ import __version__
from zapy.base import Metadata, ZapyCell
from zapy.store import Store
from zapy.test import assert_test_result_dict

Code = list[str] | str


class KeyValueItem(BaseModel):
    key: str
    value: str
    active: bool = True


class RequestMetadata(Metadata):
    cell_type: str = "zapy.ZapyRequest"
    v: str = __version__


class RequestArguments(TypedDict, total=False):
    store: Store | None
    logger: typing.Callable
    client: HttpxAsyncClient | None


class ZapyRequest(BaseModel, ZapyCell):
    metadata: RequestMetadata = Field(default_factory=RequestMetadata)
    endpoint: str
    method: str
    params: list[KeyValueItem] = Field(default_factory=list)
    headers: list[KeyValueItem] = Field(default_factory=list)
    variables: list[KeyValueItem] = Field(default_factory=list)
    script: Code = ""
    body_type: str = "None"
    body: Code | list[KeyValueItem] | None = None

    @classmethod
    def from_dict(cls, value: dict[str, typing.Any]) -> ZapyRequest:
        return cls.model_validate(value)

    @classmethod
    def from_path(cls, file_path: str | Path) -> ZapyRequest:
        import json

        with open(file_path) as f:
            loaded_json: dict = json.load(f)
        return cls.from_dict(loaded_json)

    async def send(
        self,
        *,
        raise_assert: bool = True,
        store: Store | None = None,
        logger: typing.Callable = print,
        client: HttpxAsyncClient | None = None,
    ) -> HttpxResponse:
        from .requester import send_request

        request_wrapper = await send_request(self, store=store, logger=logger, client=client)

        if request_wrapper.test_result and raise_assert is True:
            assert_test_result_dict(request_wrapper.test_result)

        return request_wrapper.response


# Copied from httpx


class HttpxArguments(TypedDict, total=False):
    method: typing.Required[str]
    url: typing.Required[httpx_types.URLTypes]
    content: httpx_types.RequestContent | None
    data: httpx_types.RequestData | None
    files: httpx_types.RequestFiles | None
    json: typing.Any | None
    params: httpx_types.QueryParamTypes
    headers: httpx_types.HeaderTypes
    cookies: httpx_types.CookieTypes
    auth: httpx_types.AuthTypes | UseClientDefault
    follow_redirects: bool | UseClientDefault
    timeout: httpx_types.TimeoutTypes | UseClientDefault
    extensions: httpx_types.RequestExtensions
