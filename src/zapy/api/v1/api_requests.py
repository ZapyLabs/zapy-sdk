from typing import Annotated, Any, Self

from fastapi import APIRouter, BackgroundTasks, Header
from pydantic import BaseModel

from zapy.api.deps.socketio import SocketIO
from zapy.base.exceptions import ZapyError
from zapy.requests.models import ZapyRequest
from zapy.requests.requester import RequesterResponse, TestResult, send_request

api_request_v1 = APIRouter(tags=["v1"])


class RequestExecResponse(BaseModel):
    @classmethod
    def from_wrapper(cls, wrapper: RequesterResponse) -> Self:
        response = wrapper.response
        content = response.text
        return cls(
            content=content,
            content_type=response.headers.get("content-type"),
            headers=dict(response.headers.items()),
            status=response.status_code,
            time=response.elapsed.total_seconds(),
            test_result=wrapper.test_result,
        )

    content: str
    content_type: str
    headers: dict[str, str]
    status: int
    time: float
    test_result: list[TestResult]


@api_request_v1.post("/request/exec")
async def exec_cell(
    sio: SocketIO,
    background_tasks: BackgroundTasks,
    zapy_request: ZapyRequest,
    x_request_id: Annotated[str | None, Header()] = None,
) -> RequestExecResponse:
    def logger(*msg: tuple[Any], sep: str = " ", end: str = "\n") -> None:
        log_message = sep.join(str(m) for m in msg) + end
        background_tasks.add_task(sio.emit, f"log:{x_request_id}", log_message)

    try:
        response_wrapper = await send_request(
            zapy_request=zapy_request,
            logger=logger,
        )
        response_exec = RequestExecResponse.from_wrapper(response_wrapper)
        return response_exec
    except ZapyError as ex:
        response = ex.context.get("response")
        if response:
            response_wrapper = RequesterResponse(response)
            ex.context["response"] = RequestExecResponse.from_wrapper(response_wrapper)
        raise
