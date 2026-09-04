from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Settings:
    database_path: str
    himalayas_rss_url: str
    fetch_timeout: int
    job_limit: int
    log_level: str

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            database_path=os.getenv("DATABASE_PATH", "jobs.db"),
            himalayas_rss_url=os.getenv("HIMALAYAS_RSS_URL", "https://himalayas.app/jobs/rss"),
            fetch_timeout=int(os.getenv("FETCH_TIMEOUT", "10")),
            job_limit=int(os.getenv("JOB_LIMIT", "50")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )