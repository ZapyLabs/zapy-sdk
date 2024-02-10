import pytest

from zapy.requests import RenderLocationError
from zapy.requests.converter import RequestConverter
from zapy.requests.models import KeyValueItem, ZapyRequest
from zapy.requests.requester import ZapyRequestContext
from zapy.store import use_store


def test_url():
    zapy_request = ZapyRequest(
        endpoint="http://test/{{var1}}/{{var2}}",
        method="GET",
        variables=[
            KeyValueItem(key="var1", value="{{ 1 + 2 }}", active=True),
            KeyValueItem(key=" var2 ", value=" between spaces ", active=True),
        ],
    )
    ctx = ZapyRequestContext(store=use_store(), logger=print)
    requester = RequestConverter(zapy_request, ctx)
    request_context = requester.build_httpx_args()

    assert "http://test/3/ between spaces " == request_context["url"]


def test_url_error():
    zapy_request = ZapyRequest(
        endpoint="http://test/{{0/0}}",
        method="GET",
    )
    ctx = ZapyRequestContext(store=use_store(), logger=print)
    requester = RequestConverter(zapy_request, ctx)
    with pytest.raises(RenderLocationError) as exc_info:
        _ = requester.build_httpx_args()
    assert exc_info.value.error_type == "render:url"
