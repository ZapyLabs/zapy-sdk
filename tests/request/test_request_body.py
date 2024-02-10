from zapy.requests.converter import RequestConverter
from zapy.requests.models import KeyValueItem, ZapyRequest
from zapy.requests.requester import ZapyRequestContext
from zapy.store import use_store


def test_body_form():
    zapy_request = ZapyRequest(
        endpoint="http://test/",
        method="POST",
        variables=[
            KeyValueItem(key="var1", value='{#jinja#}{{ "val1" | upper }}', active=True),
            KeyValueItem(key="var2", value="val2", active=True),
            KeyValueItem(key="var3", value="{{[1, 2, 0.3]}}", active=True),
        ],
        headers=[
            KeyValueItem(key="Content-TYPE", value="{{ ctx.auto() }}", active=True),
        ],
        body_type="application/x-www-form-urlencoded",
        body=[
            KeyValueItem(key="param1", value="val: {{var1}}", active=True),
            KeyValueItem(key="param2", value="{#jinja#}{{var2 | upper}}", active=True),
            KeyValueItem(key="param3", value="{{ var1 }} {{ var2 }}", active=True),
        ],
    )
    ctx = ZapyRequestContext(store=use_store(), logger=print)
    requester = RequestConverter(zapy_request, ctx)
    request_context = requester.build_httpx_args()

    assert {"Content-TYPE": "application/x-www-form-urlencoded"} == request_context["headers"]
    assert {
        "param1": ["val: VAL1"],
        "param2": ["VAL2"],
        "param3": ["VAL1 val2"],
    } == request_context["data"]


def test_body_none():
    zapy_request = ZapyRequest(
        endpoint="http://test/",
        method="GET",
        headers=[
            KeyValueItem(key="Content-TYPE", value="{{ ctx.auto() }}", active=True),
        ],
        body_type="None",
        body=[
            "any",
        ],
    )
    ctx = ZapyRequestContext(store=use_store(), logger=print)
    requester = RequestConverter(zapy_request, ctx)
    request_context = requester.build_httpx_args()

    assert {} == request_context["headers"]
    assert request_context.get("data") is None


def test_multipart_form_with_files():
    zapy_request = ZapyRequest(
        endpoint="http://test/",
        method="POST",
        variables=[
            KeyValueItem(key="var1", value='{#jinja#}{{ "val1" | upper }}', active=True),
            KeyValueItem(key="var3", value="tests/assets/requests/request1.zapy", active=True),
        ],
        body_type="multipart/form-data",
        body=[
            KeyValueItem(key="param1", value="val: {{var1}}", active=True),
            KeyValueItem(key="param4", value="{{ ctx.load_file(var3) }}", active=True),
            KeyValueItem(
                key="param5",
                value="{{ ctx.load_file('tests/assets/requests/request1.zapy', mime='text/plain') }}",
                active=True,
            ),
        ],
    )
    ctx = ZapyRequestContext(store=use_store(), logger=print)
    requester = RequestConverter(zapy_request, ctx)
    request_context = requester.build_httpx_args()

    assert {} == request_context["headers"]
    assert {
        "param1": ["val: VAL1"],
    } == request_context["data"]

    assert isinstance(request_context["files"], list)
    name, file_data = request_context["files"][0]
    _, file_data_2 = request_context["files"][1]
    assert 2 == len(file_data)
    assert 3 == len(file_data_2)

    file_name, file = file_data
    assert "param4" == name
    assert "request1.zapy" == file_name
    assert "text/plain" == file_data_2[-1]
    assert list(open("tests/assets/requests/request1.zapy", mode="rb")) == list(file)
