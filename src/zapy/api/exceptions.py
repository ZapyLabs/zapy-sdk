import traceback

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from zapy.base.exceptions import HandledException, ZapyException


def global_error_handler(request: Request, exception: Exception):
    traceback.print_exc()
    status_code = getattr(exception, "status_code", 500)
    if isinstance(exception, HandledException):
        status_code = 400
    if isinstance(exception, ValidationError):
        status_code = 400
        exception.error_type = "validation:json"
    response = {
        "error": str(exception),
        "class": exception.__class__.__name__,
        "error_type": getattr(exception, "error_type", "error:unhandled"),
    }
    if isinstance(exception, ZapyException):
        response.update({"class": "ZapyException", "context": exception.context})
    return JSONResponse(response, status_code=status_code)
