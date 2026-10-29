from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str

    himalayas_rss_url: str = "https://himalayas.app/jobs/rss"
    arbeitnow_json_url: str = "https://www.arbeitnow.com/api/job-board-api"

    jwt_secret_key: str
    access_token_expire_minutes: int = 30

    base_url: str

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }


settings = Settings()  # type: ignore[call-arg]
