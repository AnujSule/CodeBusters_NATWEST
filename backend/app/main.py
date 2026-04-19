import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("DataDialogue starting up...")
    try:
        await init_db()
        logger.info("Database tables ready")
    except Exception as e:
        logger.error(f"DB init failed: {e}")

    yield  # App runs

    # Shutdown
    logger.info("DataDialogue shutting down")


app = FastAPI(
    title="DataDialogue API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
from app.api.router import api_router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"service": "DataDialogue", "status": "running", "docs": "/docs"}
