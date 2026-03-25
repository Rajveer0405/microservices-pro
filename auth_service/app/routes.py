from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .schemas import LoginRequest, SignupRequest, TokenResponse
from .services import create_user, extract_bearer_token, login_user, verify_token


router = APIRouter()
bearer_scheme = HTTPBearer()


@router.post("/signup")
def signup(payload: SignupRequest) -> dict:
    create_user(payload.username, payload.password)
    return {"message": "User account created successfully", "username": payload.username}


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    token_data = login_user(payload.username, payload.password)
    return TokenResponse(
        access_token=token_data["token"],
        expires_at=token_data["expires_at"].isoformat(),
    )


@router.get("/verify")
def verify(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    token = extract_bearer_token(credentials)
    return verify_token(token)
