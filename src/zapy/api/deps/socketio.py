from typing import Annotated
from fastapi import Depends
import socketio

sio = socketio.AsyncServer(async_mode='asgi')

def get_sio():
    return sio

SocketIO = Annotated[socketio.AsyncServer, Depends(get_sio)]
