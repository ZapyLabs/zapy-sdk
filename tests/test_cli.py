from io import StringIO
from unittest.mock import patch

from zapy.cli import ZapyCLI


def test_start_server():
    with (
        patch("sys.argv", ["zapy", "start_server"]),
        patch("sys.exit") as mock_exit,
        patch("zapy.api.bootstrapper.start_server") as mock_start_server,
    ):
        ZapyCLI()
        mock_start_server.assert_called_once()
        mock_exit.assert_called_once_with(0)


def test_connection():
    with (
        patch("sys.argv", ["zapy", "connection"]),
        patch("zapy.api.connection.load_server_config") as mock_load_config,
        patch("sys.exit") as mock_exit,
        patch("sys.stdout", new_callable=StringIO) as mock_stdout,
    ):
        mock_load_config.return_value.model_dump_json.return_value = '{"key": "value"}'
        ZapyCLI()
        assert mock_stdout.getvalue() == '{"key": "value"}\n'
        mock_exit.assert_called_once_with(0)


def test_unrecognized_command():
    with (
        patch("sys.argv", ["zapy", "unknown_command"]),
        patch("sys.exit") as mock_exit,
    ):
        ZapyCLI()
        mock_exit.assert_called_once_with(1)


def test_help_message():
    with (
        patch("sys.argv", ["zapy"]),
        patch("sys.exit") as mock_exit,
        patch("argparse.ArgumentParser.print_help") as mock_print_help,
    ):
        ZapyCLI()
        mock_print_help.assert_called_once()
        mock_exit.assert_called_with(1)
