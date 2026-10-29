from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TokenRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr


class GoogleLoginRequest(BaseModel):
    id_token: str


class EmailRequest(BaseModel):
    email: EmailStr
