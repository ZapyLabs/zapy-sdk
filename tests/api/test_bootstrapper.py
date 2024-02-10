from unittest.mock import patch

import pytest

from zapy.api import start_server
from zapy.api.connection import ServerConnection


@pytest.fixture
def mock_load_config():
    with patch("zapy.api.connection.load_server_config") as mock_load_config:
        yield mock_load_config


@pytest.fixture
def mock_uv():
    with patch("uvicorn.run") as mock_uv:
        yield mock_uv


@pytest.fixture
def mock_sys():
    with patch("sys.exit") as mock_sys:
        yield mock_sys


def test_start_server(mock_load_config, mock_uv, mock_sys):
    mock_load_config.return_value = ServerConnection(
        host="localhost",
        port=8000,
    )

    start_server()

    mock_load_config.assert_called_once()
    mock_uv.assert_called_once_with("zapy.api.server:server", host="localhost", port=8000)
    mock_sys.assert_called_once_with(0)
