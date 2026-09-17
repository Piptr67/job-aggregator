from fastapi import FastAPI

from job_aggregator.api.routes.health import router as health_router

app = FastAPI()

app.include_router(health_router)
