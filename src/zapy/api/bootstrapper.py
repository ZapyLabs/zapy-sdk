import uvicorn

from .models import UvicornRunConfig


def start_server(options: UvicornRunConfig = {}, config: dict | str | None = None):
    from .connection import load_server_config

    server_config = load_server_config()
    uvicorn.run("zapy.api.server:server", host=server_config.host, port=server_config.port, **options)
