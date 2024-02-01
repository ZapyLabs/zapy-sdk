import os
import platform
import sys
from datetime import UTC, datetime

from fastapi import APIRouter, Request
from pydantic import BaseModel

from zapy.__about__ import __version__

api_server_v1 = APIRouter(tags=["v1"])


class InfoModel(BaseModel):
    key: str
    application: str
    version: str
    current_time: datetime
    start_time: datetime
    running_time: int
    is_venv: bool
    sys_prefix: str
    python_version: str
    documentation: str
    directory: str


@api_server_v1.get("/info")
async def server_info(request: Request) -> InfoModel:
    application_start_time: datetime = request.app.state.application_start_time
    return InfoModel(
        key="zapy",
        application="Zapy",
        version=__version__,
        current_time=datetime.now(tz=UTC),
        start_time=application_start_time,
        running_time=(datetime.now(tz=UTC) - application_start_time).seconds,
        is_venv=sys.prefix != sys.base_prefix,
        sys_prefix=sys.prefix,
        python_version=platform.python_version(),
        documentation="https://docs.zapy.dev",
        directory=os.path.abspath(os.curdir),
    )
