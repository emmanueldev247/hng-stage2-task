from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.schemas.errors import ErrorResponse

def validation_error_details(exc: RequestValidationError) -> dict:
    details = {}
    for err in exc.errors():
        loc = err.get("loc", [])
        msg = err.get("msg", "Invalid value")
        if loc and loc[0] in ("body", "query", "path"):
            key = ".".join([str(x) for x in loc[1:]]) or loc[0]
        else:
            key = ".".join([str(x) for x in loc]) if loc else "value"
        details[key] = msg
    return details

async def handle_validation_error(request: Request, exc: RequestValidationError):
    data = ErrorResponse(error="Validation failed", details=validation_error_details(exc)).dict()
    return JSONResponse(status_code=400, content=data)

async def handle_http_exception(request: Request, exc: StarletteHTTPException):
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        error = exc.detail.get("error") or "Internal error"
        details = exc.detail.get("details")
        if not details:
            return JSONResponse(status_code=exc.status_code, content=exc.detail)
        return JSONResponse(status_code=exc.status_code, content=ErrorResponse(error=error, details=details).dict())

    if exc.status_code == 404:
        return JSONResponse(status_code=404, content=ErrorResponse(error="Country not found").dict())
    if exc.status_code == 400:
        return JSONResponse(status_code=400, content=ErrorResponse(error="Validation failed").dict())
    if exc.status_code == 503:
        return JSONResponse(status_code=503, content=ErrorResponse(error="External data source unavailable").dict())

    return JSONResponse(status_code=exc.status_code, content=ErrorResponse(error=str(exc.detail)).dict())

async def handle_unexpected_error(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content=ErrorResponse(error="Internal server error").dict())
