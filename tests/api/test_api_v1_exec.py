import json
from datetime import timedelta
from unittest import mock

import httpx
import pytest
from fastapi.testclient import TestClient

from zapy.api.server import server
from zapy.store import use_store


@pytest.fixture()
def client():
    yield TestClient(server)
    store = use_store()
    store.clear()


@mock.patch.object(httpx.AsyncClient, "send", return_value=httpx.Response(201, json={"id": "test-id"}))
def test_exec_without_tests(mocked_request, client):
    mocked_request.return_value.elapsed = timedelta(seconds=2.0)
    with open("tests/assets/request1.zapy") as request_file:
        request_dict = json.load(request_file)
    response = client.post("/v1/request/exec", json=request_dict)
    actual = response.json()

    assert response.status_code == 200
    assert actual["time"] == 2.0
    assert actual["headers"]["content-type"] == "application/json"
    assert actual["content"] == '{"id": "test-id"}'
    assert actual["test_result"] == []
    assert actual["status"] == 201
