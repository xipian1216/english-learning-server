from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.logging import get_logger, setup_logging
from app.core.logging.middleware import RequestLoggingMiddleware
from app.db.session import create_db_and_tables


settings = get_settings()
setup_logging(
    level=settings.log_level,
    json_enabled=settings.log_json,
    access_log_enabled=settings.log_access_enabled,
)
logger = get_logger(__name__)


def format_validation_errors(errors: list[dict] | tuple[dict, ...] | object) -> list[dict[str, str]]:
    formatted_errors: list[dict[str, str]] = []
    if not isinstance(errors, (list, tuple)):
        return formatted_errors

    for error in errors:
        if not isinstance(error, dict):
            continue
        location = error.get("loc", [])
        field = ".".join(str(item) for item in location if item != "body") or "request"
        formatted_errors.append(
            {
                "field": field,
                "message": error.get("msg", "invalid value"),
            }
        )
    return formatted_errors


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    logger.info(
        "application startup",
        extra={
            "app_name": settings.app_name,
            "app_env": settings.app_env,
            "debug": settings.debug,
            "auto_create_tables": settings.auto_create_tables,
            "log_json": settings.log_json,
            "log_access_enabled": settings.log_access_enabled,
        },
    )
    try:
        if settings.auto_create_tables:
            logger.info("creating database tables")
            create_db_and_tables()
            logger.info("database tables ready")
        yield
    finally:
        logger.info("application shutdown")


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    log_method = logger.error if exc.status_code >= 500 else logger.warning
    log_method(
        "application error",
        extra={
            "status_code": exc.status_code,
            "code": exc.code,
            "method": request.method,
            "path": request.url.path,
        },
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message, "data": None},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = format_validation_errors(exc.errors())
    logger.warning(
        "request validation failed",
        extra={
            "status_code": 422,
            "method": request.method,
            "path": request.url.path,
            "errors": errors,
        },
    )
    return JSONResponse(
        status_code=422,
        content={
            "code": 40001,
            "message": errors[0]["message"] if errors else "validation error",
            "data": {
                "errors": errors,
            },
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "unhandled exception",
        extra={
            "status_code": 500,
            "method": request.method,
            "path": request.url.path,
            "exception_type": type(exc).__name__,
        },
    )
    return JSONResponse(
        status_code=500,
        content={"code": 50000, "message": "internal server error", "data": None},
    )


app.add_middleware(RequestLoggingMiddleware, access_log_enabled=settings.log_access_enabled)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_allow_origins(),
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.get_cors_allow_methods(),
    allow_headers=settings.get_cors_allow_headers(),
    expose_headers=settings.get_cors_expose_headers(),
    max_age=settings.cors_max_age,
)
app.include_router(api_router)


@app.get("/healthz")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_env}
