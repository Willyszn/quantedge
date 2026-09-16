from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import get_settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info("startup", extra={"event": "startup", "environment": settings.ENVIRONMENT})

    if settings.SEED_ON_STARTUP and settings.ENVIRONMENT != "production":
        from app.core.seed import seed_development_data

        try:
            await seed_development_data()
        except Exception as exc:
            logger.warning("seed_failed", extra={"event": "seed_failed", "reason": str(exc)})

    yield
    logger.info("shutdown", extra={"event": "shutdown"})


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="QUANTEDGE API",
        description=(
            "Quantitative and sentiment trading-analysis backend. QUANTEDGE is a manual "
            "decision-support system — it identifies and explains trade opportunities and "
            "never places orders. See each endpoint's description for its data source and "
            "calculation methodology."
        ),
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(api_router)

    return app


app = create_app()
