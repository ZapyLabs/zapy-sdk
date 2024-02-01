import pytest
from fastapi.testclient import TestClient

from zapy.api.server import server
from zapy.store import use_store


@pytest.fixture()
def client():
    yield TestClient(server)
    store = use_store()
    store.clear()


def test_info(client):
    response = client.get("/v1/info")

    assert response.status_code == 200
    actual = response.json()
    assert actual["key"] == "zapy"
    assert actual["application"] == "Zapy"
    assert isinstance(actual["version"], str)
    assert actual["is_venv"] is True
    assert actual["documentation"] == "https://docs.zapy.dev"
    assert len(actual["sys_prefix"]) > 0
    assert len(actual["directory"]) > 0
    assert "current_time" in actual
    assert "start_time" in actual
