from __future__ import annotations
from pathlib import Path

from pydantic import BaseModel, Field

from zapy.__init__ import __version__
from zapy.base import ZapyCell, Metadata
from zapy.test import assert_test_result_dict, AssertTestResultMixin

Code = list[str] | str

class KeyValueItem(BaseModel):
    key: str
    value: str
    active: bool = True


class RequestMetadata(Metadata):
    cell_type: str = 'zapy.ZapyRequest'
    v: str = __version__


class ZapyRequest(BaseModel, ZapyCell):
    metadata: RequestMetadata = Field(default_factory=RequestMetadata)
    endpoint: str
    method: str
    params: list[KeyValueItem] = Field(default_factory=list)
    headers: list[KeyValueItem] = Field(default_factory=list)
    variables: list[KeyValueItem] = Field(default_factory=list)
    script: Code = ""
    body_type: str = 'None'
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
                raise_assert.assertZapyTestResults(request_wrapper.test_result)

        return request_wrapper.response


# Copied from httpx
from httpx._client import *
from typing_extensions import TypedDict


class HttpxArguments(TypedDict):
    method: str
    url: URLTypes
    content: typing.Optional[RequestContent]
    data: typing.Optional[RequestData]
    files: typing.Optional[RequestFiles]
    json: typing.Optional[typing.Any]
    params: typing.Optional[QueryParamTypes]
    headers: typing.Optional[HeaderTypes]
    cookies: typing.Optional[CookieTypes]
    auth: typing.Union[AuthTypes, UseClientDefault, None]
    follow_redirects: typing.Union[bool, UseClientDefault]
    timeout: typing.Union[TimeoutTypes, UseClientDefault]
    extensions: typing.Optional[RequestExtensions]
