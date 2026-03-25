import sqlite3
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from .config import TOKEN_EXPIRY_MINUTES
from .repository import fetch_token, fetch_user_password, insert_token, insert_user, remove_token


def create_user(username: str, password: str) -> None:
    try:
        insert_user(username, password)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail="Username already exists") from exc


def login_user(username: str, password: str) -> dict:
    stored_password = fetch_user_password(username)
    if stored_password != password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = str(uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRY_MINUTES)
    insert_token(token, username, expires_at.isoformat())
    return {"token": token, "expires_at": expires_at}


def extract_bearer_token(credentials: HTTPAuthorizationCredentials | None) -> str:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authorization header is missing")

    if credentials.scheme.lower() != "bearer" or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
    return credentials.credentials


def verify_token(token: str) -> dict:
    token_data = fetch_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Token is invalid")

    expires_at = datetime.fromisoformat(token_data["expires_at"])
    if expires_at < datetime.now(timezone.utc):
        remove_token(token)
        raise HTTPException(status_code=401, detail="Token has expired")

    return {
        "valid": True,
        "username": token_data["username"],
        "expires_at": expires_at.isoformat(),
    }
