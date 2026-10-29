from fastapi import APIRouter

from job_aggregator.api.routes.auth import router as auth_router
from job_aggregator.api.routes.ingestion import router as ingestion_router
from job_aggregator.api.routes.jobs import router as jobs_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(jobs_router)
api_router.include_router(ingestion_router)
api_router.include_router(auth_router)
