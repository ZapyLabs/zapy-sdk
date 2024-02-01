import asyncio
import os
import typing

from pydantic import BaseModel
from typing_extensions import TypedDict
from uvicorn.config import (
    HTTPProtocolType,
    InterfaceType,
    LifespanType,
    LoopSetupType,
    WSProtocolType,
)


class ServerConnection(BaseModel):
    host: str
    port: int


# Copied from uvicorn


class UvicornRunConfig(TypedDict, total=False):
    host: str
    port: int
    uds: str
    fd: int
    loop: LoopSetupType
    http: typing.Union[typing.Type[asyncio.Protocol], HTTPProtocolType]
    ws: typing.Union[typing.Type[asyncio.Protocol], WSProtocolType]
    ws_max_size: int
    ws_max_queue: int
    ws_ping_interval: float
    ws_ping_timeout: float
    ws_per_message_deflate: bool
    lifespan: LifespanType
    interface: InterfaceType
    reload: bool
    reload_dirs: typing.Union[typing.List[str], str]
    reload_includes: typing.Union[typing.List[str], str]
    reload_excludes: typing.Union[typing.List[str], str]
    reload_delay: float
    workers: int
    env_file: typing.Union[str, os.PathLike]
    log_config: typing.Union[typing.Dict[str, typing.Any], str]
    log_level: typing.Union[str, int]
    access_log: bool
    proxy_headers: bool
    server_header: bool
    date_header: bool
    forwarded_allow_ips: typing.Union[typing.List[str], str]
    root_path: str
    limit_concurrency: int
    backlog: int
    limit_max_requests: int
    timeout_keep_alive: int
    timeout_graceful_shutdown: int
    ssl_keyfile: str
    ssl_certfile: typing.Union[str, os.PathLike]
    ssl_keyfile_password: str
    ssl_version: int
    ssl_cert_reqs: int
    ssl_ca_certs: str
    ssl_ciphers: str
    headers: typing.List[typing.Tuple[str, str]]
    use_colors: bool
    app_dir: str
    factory: bool
    h11_max_incomplete_event_size: int
