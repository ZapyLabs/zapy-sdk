from typing import Annotated

import socketio
from fastapi import Depends

sio = socketio.AsyncServer(async_mode="asgi")


def get_sio() -> socketio.AsyncServer:
    return sio


SocketIO = Annotated[socketio.AsyncServer, Depends(get_sio)]
