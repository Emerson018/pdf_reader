import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.api.app.core.config import settings
from apps.api.app.core.logging import setup_logging
from apps.api.app.api.v1 import api_v1_router, health_router

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} API in {settings.APP_ENV} environment...")
    yield
    logger.info(f"Shutting down {settings.APP_NAME} API...")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Modular AI Agent Platform API",
    lifespan=lifespan
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health_router, tags=["health"])
app.include_router(api_v1_router)


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "apps.api.app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
