import pytest

from zapy.requests import RenderLocationError
from zapy.requests.converter import RequestConverter
from zapy.requests.models import KeyValueItem, ZapyRequest
from zapy.requests.requester import ZapyRequestContext
from zapy.store import use_store


def test_header_auto():
    zapy_request = ZapyRequest(
        endpoint="http://test/",
        method="GET",
        headers=[
            KeyValueItem(key="Content-TYPE", value="{{ ctx.auto() }}", active=True),
            KeyValueItem(key=" X-stripped", value=" no_stripped ", active=True),
            KeyValueItem(key="Skipped", value="{{ 0/0 }}", active=False),
        ],
        body_type="application/json",
        body=[
            '{ "hello": "world" }',
        ],
    )
    ctx = ZapyRequestContext(store=use_store(), logger=print)
    requester = RequestConverter(zapy_request, ctx)
    request_context = requester.build_httpx_args()

    assert {"Content-TYPE": "application/json", "X-stripped": " no_stripped "} == request_context["headers"]
    assert '{ "hello": "world" }' == request_context["content"]


def test_header_override():
    zapy_request = ZapyRequest(
        endpoint="http://test/",
        method="GET",
        variables=[
            KeyValueItem(key="content_type", value="text/plain", active=True),
        ],
        headers=[
            KeyValueItem(key="content-Type", value="{{ content_type }}", active=True),
        ],
        body_type="application/json",
        body=[
            "{{ content_type | upper }}",
        ],
    )
    ctx = ZapyRequestContext(store=use_store(), logger=print)
    requester = RequestConverter(zapy_request, ctx)
    request_context = requester.build_httpx_args()

    assert {
        "content-Type": "text/plain",
    } == request_context["headers"]
    assert "TEXT/PLAIN" == request_context["content"]


def test_header_missing():
    zapy_request = ZapyRequest(
        endpoint="http://test/",
        method="GET",
        body_type="text/plain",
        body=[
            "any",
        ],
    )
    ctx = ZapyRequestContext(store=use_store(), logger=print)
    requester = RequestConverter(zapy_request, ctx)
    request_context = requester.build_httpx_args()

    assert {} == request_context["headers"]
    assert "any" == request_context["content"]


def test_headers_error():
    zapy_request = ZapyRequest(
        endpoint="http://test/",
        headers=[
            KeyValueItem(key="content-Type", value="{{ 0/0 }}", active=True),
        ],
        method="GET",
    )
    ctx = ZapyRequestContext(store=use_store(), logger=print)
    requester = RequestConverter(zapy_request, ctx)
    with pytest.raises(RenderLocationError) as exc_info:
        _ = requester.build_httpx_args()
    assert exc_info.value.error_type == "render:headers"
