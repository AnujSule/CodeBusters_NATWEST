from fastapi import APIRouter
from app.api.v1 import auth, datasets, queries, audit, health

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
api_router.include_router(queries.router, prefix="/queries", tags=["queries"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
