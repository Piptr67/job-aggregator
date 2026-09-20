from sqlalchemy.orm import sessionmaker

from job_aggregator.db.database import engine


SessionLocal = sessionmaker(bind=engine)
