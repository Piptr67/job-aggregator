import jwt

from fastapi import APIRouter, Depends, HTTPException, status
from google.auth.exceptions import GoogleAuthError
from sqlalchemy import select
from sqlalchemy.orm import Session

from job_aggregator.api.dependencies import get_db
from job_aggregator.api.schemas.auth import (
    GoogleLoginRequest,
    TokenResponse,
    TokenRequest,
    RegisterRequest,
    UserResponse,
)
from job_aggregator.core.email import send_verification_email
from job_aggregator.core.google_auth import verify_google_token
from job_aggregator.core.passwords import hash_password, verify_password
from job_aggregator.core.security import (
    create_access_token,
    decode_verification_token,
    create_verification_token,
)
from job_aggregator.db.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=TokenResponse)
def login(credentials: TokenRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalars(select(User).where(User.email == credentials.email)).one_or_none()

    if (
        user is None
        or user.hashed_password is None
        or not verify_password(credentials.password, user.hashed_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in",
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

    verification_token = create_verification_token(user.email)
    send_verification_email(user.email, verification_token)

    return UserResponse.model_validate(user)


@router.get("/verify-email")
def verify_email(
    token: str,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    try:
        email = decode_verification_token(token)
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification link",
        ) from None

    user = db.scalars(select(User).where(User.email == email)).one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification link",
        )

    if user.is_verified:
        return {"message": "Email already verified"}

    user.is_verified = True
    db.commit()

    return {"message": "Email verified successfully"}


@router.post("/google", response_model=TokenResponse)
def google_login(
    credentials: GoogleLoginRequest, db: Session = Depends(get_db)
) -> TokenResponse:
    try:
        google_user = verify_google_token(credentials.id_token)
    except (ValueError, GoogleAuthError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google ID token"
        ) from None

    email = google_user.get("email")

    if not isinstance(email, str) or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google account has no valid email",
        )

    user = db.scalars(select(User).where(User.email == email)).one_or_none()

    if user is None:
        user = User(
            email=email,
            hashed_password=None,
            is_verified=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    elif not user.is_verified:
        user.is_verified = True
        user.hashed_password = None
        db.commit()

    access_token = create_access_token(subject=str(user.id))

    return TokenResponse(access_token=access_token, token_type="bearer")
