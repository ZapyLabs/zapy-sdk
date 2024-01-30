from __future__ import annotations

import typing
from pathlib import Path

from httpx._client import (
    AuthTypes,
    CookieTypes,
    HeaderTypes,
    QueryParamTypes,
    RequestContent,
    RequestData,
    RequestExtensions,
    RequestFiles,
    TimeoutTypes,
    URLTypes,
    UseClientDefault,
)
from httpx._client import (
    Response as HttpxResponse,  # noqa: F401
)
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from zapy.__init__ import __version__
from zapy.base import Metadata, ZapyCell
from zapy.test import AssertTestResultMixin, assert_test_result_dict

Code = list[str] | str


class KeyValueItem(BaseModel):
    key: str
    value: str
    active: bool = True


class RequestMetadata(Metadata):
    cell_type: str = "zapy.ZapyRequest"
    v: str = __version__


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
    def from_dict(cls, value: dict) -> ZapyRequest:
        return cls.model_validate(value)

    @classmethod
    def from_path(cls, file_path: str | Path) -> ZapyRequest:
        import json

        with open(file_path) as f:
            loaded_json = json.load(f)
        return cls.from_dict(loaded_json)

    async def send(self, *, raise_assert: AssertTestResultMixin | bool = True, **kwargs):
        from .requester import send_request

        request_wrapper = await send_request(self, **kwargs)

        if request_wrapper.test_result:
            if raise_assert is True:
                assert_test_result_dict(request_wrapper.test_result)
            elif isinstance(raise_assert, AssertTestResultMixin):
                raise_assert.assert_zapy_test_results(request_wrapper.test_result)

        return request_wrapper.response


# Copied from httpx


class HttpxArguments(TypedDict):
    method: str
    url: URLTypes
    content: RequestContent | None
    data: RequestData | None
    files: RequestFiles | None
    json: typing.Any | None
    params: QueryParamTypes | None
    headers: HeaderTypes | None
    cookies: CookieTypes | None
    auth: AuthTypes | UseClientDefault | None
    follow_redirects: bool | UseClientDefault
    timeout: TimeoutTypes | UseClientDefault
    extensions: RequestExtensions | None
