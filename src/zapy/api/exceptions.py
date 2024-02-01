import traceback

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from zapy.base.exceptions import HandledError, ZapyError


def global_error_handler(_: Request, exception: Exception) -> JSONResponse:
    traceback.print_exc()
    status_code = getattr(exception, "status_code", 500)
    error_type = getattr(exception, "error_type", "error:unhandled")
    if isinstance(exception, HandledError):
        status_code = 400
    if isinstance(exception, ValidationError):
        status_code = 400
        error_type = "validation:json"
    response = {
        "error": str(exception),
        "class": exception.__class__.__name__,
        "error_type": error_type,
    }
    if isinstance(exception, ZapyError):
        response.update({"class": "ZapyError", "context": exception.context})
    return JSONResponse(response, status_code=status_code)
