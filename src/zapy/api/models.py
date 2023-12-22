from pydantic import BaseModel


class ServerConnection(BaseModel):
    host: str
    port: int



from uvicorn.main import *
from typing_extensions import TypedDict

class UvicornRunConfig(TypedDict):
    host: str
    port: int
    uds: typing.Optional[str]
    fd: typing.Optional[int]
    loop: LoopSetupType
    http: typing.Union[typing.Type[asyncio.Protocol], HTTPProtocolType]
    ws: typing.Union[typing.Type[asyncio.Protocol], WSProtocolType]
    ws_max_size: int
    ws_max_queue: int
    ws_ping_interval: typing.Optional[float]
    ws_ping_timeout: typing.Optional[float]
    ws_per_message_deflate: bool
    lifespan: LifespanType
    interface: InterfaceType
    reload: bool
    reload_dirs: typing.Optional[typing.Union[typing.List[str], str]]
    reload_includes: typing.Optional[typing.Union[typing.List[str], str]]
    reload_excludes: typing.Optional[typing.Union[typing.List[str], str]]
    reload_delay: float
    workers: typing.Optional[int]
    env_file: typing.Optional[typing.Union[str, os.PathLike]]
    log_config: typing.Optional[
        typing.Union[typing.Dict[str, typing.Any], str]
    ]
    log_level: typing.Optional[typing.Union[str, int]]
    access_log: bool
    proxy_headers: bool
    server_header: bool
    date_header: bool
    forwarded_allow_ips: typing.Optional[typing.Union[typing.List[str], str]]
    root_path: str
    limit_concurrency: typing.Optional[int]
    backlog: int
    limit_max_requests: typing.Optional[int]
    timeout_keep_alive: int
    timeout_graceful_shutdown: typing.Optional[int]
    ssl_keyfile: typing.Optional[str]
    ssl_certfile: typing.Optional[typing.Union[str, os.PathLike]]
    ssl_keyfile_password: typing.Optional[str]
    ssl_version: int
    ssl_cert_reqs: int
    ssl_ca_certs: typing.Optional[str]
    ssl_ciphers: str
    headers: typing.Optional[typing.List[typing.Tuple[str, str]]]
    use_colors: typing.Optional[bool]
    app_dir: typing.Optional[str]
    factory: bool
    h11_max_incomplete_event_size: typing.Optional[int]
