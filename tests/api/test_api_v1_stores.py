import pytest
from fastapi.testclient import TestClient

from zapy.api.server import server
from zapy.store import use_store


@pytest.fixture()
def client():
    yield TestClient(server)
    store = use_store()
    store.clear()


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
