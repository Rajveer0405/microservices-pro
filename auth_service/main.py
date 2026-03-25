import sqlite3
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel


app = FastAPI(title="Auth Service")
DB_PATH = "auth.db"
TOKEN_EXPIRY_MINUTES = 60
bearer_scheme = HTTPBearer()


class LoginRequest(BaseModel):
    username: str
    password: str


class SignupRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_at: str


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tokens (
            token TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            FOREIGN KEY(username) REFERENCES users(username)
        )
        """
    )

    cursor.executemany(
        "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
        [
            ("admin", "admin123"),
            ("alice", "alice123"),
            ("bob", "bob123"),
        ],
    )
    connection.commit()
    connection.close()


@app.on_event("startup")
def startup() -> None:
    init_db()


def create_token(username: str) -> dict:
    token = str(uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRY_MINUTES)
    connection = get_connection()
    connection.execute(
        "INSERT INTO tokens (token, username, expires_at) VALUES (?, ?, ?)",
        (token, username, expires_at.isoformat()),
    )
    connection.commit()
    connection.close()
    return {"token": token, "username": username, "expires_at": expires_at}


def get_user_password(username: str) -> str | None:
    connection = get_connection()
    user = connection.execute(
        "SELECT password FROM users WHERE username = ?",
        (username,),
    ).fetchone()
    connection.close()
    return None if user is None else user["password"]


def get_token_record(token: str) -> sqlite3.Row | None:
    connection = get_connection()
    token_row = connection.execute(
        "SELECT username, expires_at FROM tokens WHERE token = ?",
        (token,),
    ).fetchone()
    connection.close()
    return token_row


def delete_token(token: str) -> None:
    connection = get_connection()
    connection.execute("DELETE FROM tokens WHERE token = ?", (token,))
    connection.commit()
    connection.close()


def create_user(username: str, password: str) -> None:
    connection = get_connection()
    try:
        connection.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password),
        )
        connection.commit()
    except sqlite3.IntegrityError as exc:
        connection.close()
        raise HTTPException(status_code=400, detail="Username already exists") from exc
    connection.close()


def get_bearer_token(credentials: HTTPAuthorizationCredentials | None) -> str:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authorization header is missing")

    if credentials.scheme.lower() != "bearer" or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
    return credentials.credentials


@app.post("/signup")
def signup(payload: SignupRequest) -> dict:
    create_user(payload.username, payload.password)
    return {"message": "User account created successfully", "username": payload.username}


@app.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    stored_password = get_user_password(payload.username)
    if stored_password != payload.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token_data = create_token(payload.username)
    return TokenResponse(
        access_token=token_data["token"],
        expires_at=token_data["expires_at"].isoformat(),
    )


@app.get("/verify")
def verify(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    token = get_bearer_token(credentials)
    token_data = get_token_record(token)

    if not token_data:
        raise HTTPException(status_code=401, detail="Token is invalid")

    expires_at = datetime.fromisoformat(token_data["expires_at"])
    if expires_at < datetime.now(timezone.utc):
        delete_token(token)
        raise HTTPException(status_code=401, detail="Token has expired")

    return {
        "valid": True,
        "username": token_data["username"],
        "expires_at": expires_at.isoformat(),
    }
