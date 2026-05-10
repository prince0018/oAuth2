from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from src.auth.oauth_routes import router as auth_router
from src.config import get_settings
from src.db.users import create_users_table


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_users_table()
    yield


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="OAuth Login System",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.session_secret_key,
        same_site=settings.session_cookie_samesite,
        https_only=settings.session_cookie_secure,
    )

    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=list(settings.cors_origins),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(auth_router)

    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    return app


app = create_app()
