from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ParsedJob(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=255)
    company: str = Field(min_length=1, max_length=255)
    description: str | None = None
    location: str | None = None
    url: str = Field(min_length=1)
    source: str
    published_at: datetime | None = None

    @field_validator("title", "company", "url")
    @classmethod
    def required_text_must_not_be_blank(cls, value: str) -> str:
        if not value:
            raise ValueError("Field must not be blank")
        return value
