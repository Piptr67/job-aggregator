from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    himalayas_rss_url: str
    arbeitnow_json_url: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    resend_api_key: str
    email_from: str

    google_client_id: str

    base_url: str

    model_config = {
        "env_file": ".env",
    }


settings = Settings()  # type: ignore[call-arg]
