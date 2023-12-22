import json
from unittest import mock
import httpx
from datetime import timedelta

from zapy.api.server import server
from zapy.store import use_store
from fastapi.testclient import TestClient
import pytest


@pytest.fixture()
def client():
    yield TestClient(server)
    store = use_store()
    store.clear()


def test_info(client):
    response = client.get("/v1/info")

    assert response.status_code == 200
    actual = response.json()
    assert actual['key'] == "zapy"
    assert actual['application'] == "Zapy"
    assert actual['version'] == "0.0.1a0"
    assert actual['virtualEnv'] == True
    assert actual['documentation'] == "https://docs.zapy.dev"
    assert len(actual['sys_prefix']) > 0
    assert len(actual['directory']) > 0
    assert "current_time" in actual
    assert "start_time" in actual


@mock.patch.object(
    httpx.AsyncClient, 'send',
    return_value = httpx.Response(201, json={'id': 'test-id'})
)
def test_exec_without_tests(mocked_request, client):
    mocked_request.return_value.elapsed = timedelta(seconds=2.0)
    with open('tests/assets/request1.zapy') as request_file:
        request_dict = json.load(request_file)
    response = client.post("/v1/request/exec", json=request_dict)
    actual = response.json()

    assert response.status_code == 200
    assert actual['time'] == 2.0
    assert actual['headers']['content-type'] == 'application/json'
    assert actual['content'] == '{"id": "test-id"}'
    assert actual['test_result'] == []
    assert actual['status'] == 201


def test_store_empty(client):
    response = client.get("/v1/stores/default")
    actual = response.json()

    assert response.status_code == 200
    assert actual == {
        'attributes': [],
        'field_name': 'default',
        'path': 'default',
        'type_str': 'Store',
        'value_repr': '{}'
    }

def test_store(client):
    store = use_store()
    store.test_var1 = 'dummy'

    response = client.get("/v1/stores/default")
    actual = response.json()
    

    assert response.status_code == 200
    assert actual == {
        'attributes': [
            {
                'attributes': [],
                'field_name': "'test_var1'",
                'path': "default['test_var1']",
                'type_str': 'str',
                'value_repr': "'dummy'",
            }
        ],
        'field_name': 'default',
        'path': 'default',
        'type_str': 'Store',
        'value_repr': "{'test_var1': 'dummy'}"
    }
