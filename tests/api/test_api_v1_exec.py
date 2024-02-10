import json
from datetime import timedelta
from unittest import mock

import httpx
import pytest
from fastapi.testclient import TestClient

from zapy.api.server import server
from zapy.requests.models import KeyValueItem, ZapyRequest
from zapy.store import use_store


@pytest.fixture()
def client():
    yield TestClient(server, raise_server_exceptions=False)
    store = use_store()
    store.clear()


@mock.patch.object(httpx.AsyncClient, "send", return_value=httpx.Response(201, json={"id": "test-id"}))
def test_exec_without_tests(mocked_request, client):
    mocked_request.return_value.elapsed = timedelta(seconds=2.0)
    with open("tests/assets/requests/request1.zapy") as request_file:
        request_dict = json.load(request_file)
    response = client.post("/v1/request/exec", json=request_dict)
    actual = response.json()

    assert response.status_code == 200
    assert actual["time"] == 2.0
    assert actual["headers"]["content-type"] == "application/json"
    assert actual["content"] == '{"id": "test-id"}'
    assert actual["test_result"] == []
    assert actual["status"] == 201


@mock.patch.object(httpx.AsyncClient, "send", return_value=httpx.Response(201, json={"id": "test-id"}))
def test_exec_param_error(mocked_request, client):
    mocked_request.return_value.elapsed = timedelta(seconds=2.0)
    zapy_request = ZapyRequest(
        endpoint="http://test/",
        method="GET",
        params=[
            KeyValueItem(key="Error Param", value="{{ 0/0 }}", active=True),
        ],
    )
    response = client.post("/v1/request/exec", json=zapy_request.model_dump())
    actual = response.json()

    assert response.status_code == 400
    assert actual == {"class": "ZapyError", "context": {}, "error": "Error on params", "error_type": "render:params"}


def test_exec_pre_request_error(client):
    zapy_request = ZapyRequest(
        endpoint="http://test/",
        method="GET",
        script=["@ctx.hooks.pre_request", "async def on_pre_request(httpx_args):", '   raise ValueError("mock")'],
    )
    response = client.post("/v1/request/exec", json=zapy_request.model_dump())
    actual = response.json()

    expected_traceback = """Traceback (most recent call last):
  hook, line 3, in on_pre_request
    raise ValueError("mock")
ValueError: mock"""

    assert response.status_code == 400
    assert actual == {
        "class": "ZapyError",
        "context": {
            "stacktrace": {
                "exception_message": "mock",
                "exception_type": "ValueError",
                "line": 3,
                "stacktrace": expected_traceback,
            }
        },
        "error": "Error on pre_request",
        "error_type": "render:pre_request",
    }


def test_exec_422_error(client):
    zapy_request = {
        "endpoint": "http://test/",
    }
    response = client.post("/v1/request/exec", json=zapy_request)
    actual = response.json()

    assert response.status_code == 422
    assert actual == {
        "detail": [
            {
                "input": {"endpoint": "http://test/"},
                "loc": ["body", "method"],
                "msg": "Field required",
                "type": "missing",
                "url": mock.ANY,
            }
        ]
    }
