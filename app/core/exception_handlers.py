import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("error_logger")


def register_exception_handlers(app):

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.warning(
            f"HTTP Exception | Path: {request.url.path} | "
            f"Status: {exc.status_code} | Detail: {exc.detail}"
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(
            f"Validation Error | Path: {request.url.path} | "
            f"Errors: {exc.errors()}"
        )

        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error(
            f"Unhandled Exception | Path: {request.url.path}",
            exc_info=True,
        )

        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"},
        )