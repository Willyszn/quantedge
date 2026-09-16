from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.logging import get_logger

logger = get_logger(__name__)


class QuantEdgeError(Exception):
    """Base class for all domain errors. Maps to a stable error code and
    HTTP status so the frontend can branch on `error.code` rather than
    parsing prose messages."""

    code: str = "INTERNAL_ERROR"
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message: str, *, code: str | None = None, status_code: int | None = None):
        super().__init__(message)
        self.message = message
        if code:
            self.code = code
        if status_code:
            self.status_code = status_code


class SymbolNotFoundError(QuantEdgeError):
    code = "SYMBOL_NOT_FOUND"
    status_code = status.HTTP_404_NOT_FOUND


class SignalNotFoundError(QuantEdgeError):
    code = "SIGNAL_NOT_FOUND"
    status_code = status.HTTP_404_NOT_FOUND


class UnsupportedTimeframeError(QuantEdgeError):
    code = "UNSUPPORTED_TIMEFRAME"
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class InvalidBacktestConfigError(QuantEdgeError):
    code = "INVALID_BACKTEST_CONFIG"
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class UnsupportedStrategyError(QuantEdgeError):
    code = "UNSUPPORTED_STRATEGY"
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class DataUnavailableError(QuantEdgeError):
    code = "DATA_UNAVAILABLE"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE


class ProviderError(QuantEdgeError):
    code = "PROVIDER_ERROR"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE


def _error_body(code: str, message: str) -> dict:
    return {"error": {"code": code, "message": message}}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(QuantEdgeError)
    async def handle_quantedge_error(request: Request, exc: QuantEdgeError) -> JSONResponse:
        logger.warning(
            "domain_error",
            extra={"event": "domain_error", "code": exc.code, "path": str(request.url.path)},
        )
        return JSONResponse(status_code=exc.status_code, content=_error_body(exc.code, exc.message))

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_body("VALIDATION_ERROR", "One or more fields failed validation."),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        # Never leak stack traces or exception internals to the client.
        logger.error(
            "unhandled_exception",
            extra={"event": "unhandled_exception", "path": str(request.url.path)},
            exc_info=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_body("INTERNAL_ERROR", "An unexpected error occurred."),
        )
