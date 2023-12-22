import socket
import sys
import json

from pathlib import Path

from .models import ServerConnection


def load_server_config() -> ServerConnection:
    virtual_env_path = Path(sys.prefix)
    zapy_etc = virtual_env_path / 'etc' / 'zapy'
    zapy_etc.mkdir(parents=True, exist_ok=True)

    conn_file = zapy_etc / 'connection.json'

    if not conn_file.exists():
        conn = create_connection(conn_file)
    else:
        conn = read_connection(conn_file)
    
    return conn


def create_connection(conn_path) -> ServerConnection:
    conn = ServerConnection(
        host = '127.0.0.1',
        port = get_random_free_port(),
    )
    with open(conn_path, "w") as outfile:
        outfile.write(conn.model_dump_json())
    return conn


def read_connection(conn_path) -> ServerConnection:
    with open(conn_path, "r") as outfile:
        raw_data = json.load(outfile)
        return ServerConnection.model_validate(raw_data)

def get_random_free_port() -> int:
    sock = socket.socket()
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port

