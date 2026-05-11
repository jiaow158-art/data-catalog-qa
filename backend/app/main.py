from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.api.v1 import databases, tables, columns, schedules, reports, search, qa, lineage, import_

# Import all models to register them on Base.metadata
import app.models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="数仓元数据智能问答平台",
        description="Data Catalog Q&A Platform - MVP",
        version="0.1.0",
        lifespan=lifespan,
    )

    origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(databases.router, prefix="/api/v1")
    app.include_router(tables.router, prefix="/api/v1")
    app.include_router(columns.router, prefix="/api/v1")
    app.include_router(schedules.router, prefix="/api/v1")
    app.include_router(reports.router, prefix="/api/v1")
    app.include_router(search.router, prefix="/api/v1")
    app.include_router(qa.router, prefix="/api/v1")
    app.include_router(lineage.router, prefix="/api/v1")
    app.include_router(import_.router, prefix="/api/v1")

    return app


app = create_app()
