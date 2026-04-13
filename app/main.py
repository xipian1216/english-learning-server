from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.db.session import create_db_and_tables


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
    if settings.auto_create_tables:
        create_db_and_tables()
    yield


settings = get_settings()
app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)


@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message, "data": None},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    errors = format_validation_errors(exc.errors())
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


app.include_router(api_router)


@app.get("/healthz")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_env}
