from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    himalayas_rss_url: str

    model_config = {
        "env_file": ".env",
    }


settings = Settings() # type: ignore[call-arg]
