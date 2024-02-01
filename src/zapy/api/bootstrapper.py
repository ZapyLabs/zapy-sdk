import sys
from typing import NoReturn, cast

import uvicorn

from .models import UvicornRunConfig


def start_server(options: UvicornRunConfig | None = None) -> NoReturn:
    from .connection import load_server_config

    if options is None:
        options = {}

    server_config = load_server_config()

    uvicorn_config = cast(UvicornRunConfig, server_config.dict() | options)

    uvicorn.run("zapy.api.server:server", **uvicorn_config)
    sys.exit(0)
