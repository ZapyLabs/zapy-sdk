from unittest.mock import mock_open, patch

import pytest

from zapy.api.connection import (
    ServerConnection,
    create_connection,
    get_random_free_port,
    load_server_config,
    read_connection,
)


@pytest.fixture
def mock_server_connection():
    return ServerConnection(host="127.0.0.1", port=8080)


def test_create_connection(tmp_path):
    conn_path = tmp_path / "connection.json"
    with (
        patch("builtins.open", mock_open()) as mock_file_open,
        patch("zapy.api.connection.get_random_free_port", return_value=8080),
    ):
        connection = create_connection(conn_path)
        assert connection.host == "127.0.0.1"
        assert connection.port == 8080
        mock_file_open.assert_called_once_with(conn_path, "w")
        mock_file_open().write.assert_called_once_with(connection.model_dump_json())


def test_read_connection(mock_server_connection, tmp_path):
    conn_path = tmp_path / "connection.json"
    with patch("builtins.open", mock_open(read_data=mock_server_connection.model_dump_json())):
        connection = read_connection(conn_path)
        assert connection.host == "127.0.0.1"
        assert connection.port == 8080


def test_get_random_free_port():
    port = get_random_free_port()
    assert isinstance(port, int)
    assert 1024 <= port <= 65535


def test_load_server_config(mock_server_connection):
    with patch("zapy.api.connection.create_connection", return_value=mock_server_connection):
        connection = load_server_config()
        assert connection.host == "127.0.0.1"
        assert connection.port == 8080
