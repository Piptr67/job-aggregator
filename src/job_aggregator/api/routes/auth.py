from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from job_aggregator.api.dependencies import get_db
from job_aggregator.api.schemas.auth import (
    TokenResponse,
    TokenRequest,
    RegisterRequest,
    UserResponse,
)
from job_aggregator.core.passwords import hash_password, verify_password
from job_aggregator.core.security import create_access_token
from job_aggregator.db.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=TokenResponse)
def login(credentials: TokenRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalars(select(User).where(User.email == credentials.email)).one_or_none()

    if user is None or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=str(user.id))

    return TokenResponse(access_token=access_token, token_type="bearer")


@router.post("/register", response_model=UserResponse, status_code=201)
def register(
    credentials: RegisterRequest, db: Session = Depends(get_db)
) -> UserResponse:
    existing_user = db.scalars(
        select(User).where(User.email == credentials.email)
    ).one_or_none()

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )

    user = User(
        email=credentials.email, hashed_password=hash_password(credentials.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse(id=user.id, email=user.email)
