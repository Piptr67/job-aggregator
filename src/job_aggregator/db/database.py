from sqlalchemy import create_engine

from job_aggregator.core.config import Settings


settings = Settings()

engine = create_engine(settings.database_url)