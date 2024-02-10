import pytest

from zapy.requests import RenderLocationError
from zapy.requests.converter import RequestConverter
from zapy.requests.models import KeyValueItem, ZapyRequest
from zapy.requests.requester import ZapyRequestContext
from zapy.store import use_store


def test_params_flag():
    zapy_request = ZapyRequest(
        endpoint="http://test/",
        method="GET",
        params=[
            KeyValueItem(key="Key1", value="val1", active=False),
            KeyValueItem(key="Key2", value="{{ var1 }}", active=True),
            KeyValueItem(key="key3", value="{{ 0/0 }}", active=False),
        ],
        variables=[
            KeyValueItem(key="var1", value="test1", active=True),
        ],
    )
    ctx = ZapyRequestContext(store=use_store(), logger=print)
    requester = RequestConverter(zapy_request, ctx)
    request_context = requester.build_httpx_args()

    assert {"Key2": ["test1"]} == request_context["params"]


def test_params_missing():
    zapy_request = ZapyRequest(
        endpoint="http://test/",
        method="POST",
        body_type="text/plain",
        body=[
            "any",
        ],
    )
    ctx = ZapyRequestContext(store=use_store(), logger=print)
    requester = RequestConverter(zapy_request, ctx)
    request_context = requester.build_httpx_args()

    assert {} == request_context["params"]
    assert "any" == request_context["content"]


def test_params_error():
    zapy_request = ZapyRequest(
        endpoint="http://test/",
        params=[
            KeyValueItem(key="key1", value="{{ 0/0 }}", active=True),
        ],
        method="GET",
    )
    ctx = ZapyRequestContext(store=use_store(), logger=print)
    requester = RequestConverter(zapy_request, ctx)
    with pytest.raises(RenderLocationError) as exc_info:
        _ = requester.build_httpx_args()
    assert exc_info.value.error_type == "render:params"
