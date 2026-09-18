from fastapi import FastAPI

from job_aggregator.api.routes.health import router as health_router
from job_aggregator.api.router import api_router

app = FastAPI()

app.include_router(health_router)
app.include_router(api_router)
