from datetime import datetime

import socketio

from .exceptions import global_error_handler
from .deps.socketio import sio

from . import v1 as api_v1 

from fastapi import FastAPI, APIRouter


app = FastAPI()
app.state.application_start_time = datetime.now()
app.add_exception_handler(Exception, global_error_handler)

app_v1 = APIRouter()
app_v1.include_router(api_v1.api_server_v1)
app_v1.include_router(api_v1.api_store_v1)
app_v1.include_router(api_v1.api_request_v1)

app.include_router(app_v1, prefix='/v1')

server = socketio.ASGIApp(sio, app)
