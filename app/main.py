from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.learning import router as learning_router
from app.api.system import router as system_router
from app.core.config import get_settings
from app.core.errors import install_error_handlers


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title=settings.app_name, debug=settings.debug)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.get_cors_methods(),
        allow_headers=settings.get_cors_headers(),
    )
    install_error_handlers(application)
    application.include_router(system_router)
    application.include_router(auth_router)
    application.include_router(learning_router)
    return application


app = create_app()
