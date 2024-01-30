import uvicorn

from .models import UvicornRunConfig


def start_server(options: UvicornRunConfig | None = None):
    from .connection import load_server_config

    if options is None:
        options = {}

    server_config = load_server_config()
    uvicorn.run("zapy.api.server:server", host=server_config.host, port=server_config.port, **options)
