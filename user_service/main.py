import os
import sqlite3
from typing import Optional

import requests
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr


app = FastAPI(title="User Service")

AUTH_SERVICE_VERIFY_URL = os.getenv("AUTH_SERVICE_VERIFY_URL", "http://127.0.0.1:8000/verify")
DB_PATH = "users.db"
bearer_scheme = HTTPBearer()


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: int


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    connection = get_connection()
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            age INTEGER NOT NULL
        )
        """
    )
    connection.commit()
    connection.close()


@app.on_event("startup")
def startup() -> None:
    init_db()


def verify_token(credentials: HTTPAuthorizationCredentials | None) -> dict:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authorization header is missing")

    authorization = f"{credentials.scheme} {credentials.credentials}"

    try:
        response = requests.get(
            AUTH_SERVICE_VERIFY_URL,
            headers={"Authorization": authorization},
            timeout=5,
        )
    except requests.RequestException as exc:
        raise HTTPException(status_code=503, detail="Auth service is unavailable") from exc

    if response.status_code != 200:
        try:
            detail = response.json().get("detail", "Token verification failed")
        except ValueError:
            detail = "Token verification failed"
        raise HTTPException(status_code=401, detail=detail)

    return response.json()


@app.post("/add_user")
def add_user(
    payload: UserCreate,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    verify_token(credentials)

    user = payload.model_dump()
    connection = get_connection()
    try:
        cursor = connection.execute(
            "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
            (user["name"], user["email"], user["age"]),
        )
        connection.commit()
    except sqlite3.IntegrityError as exc:
        connection.close()
        raise HTTPException(status_code=400, detail="Email already exists") from exc

    user["id"] = cursor.lastrowid
    connection.close()
    return {"message": "User added successfully", "user": user}


@app.get("/get_users")
def get_users(
    credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
) -> dict:
    if credentials:
        verify_token(credentials)
    connection = get_connection()
    rows = connection.execute("SELECT id, name, email, age FROM users ORDER BY id").fetchall()
    connection.close()
    return {"users": [dict(row) for row in rows]}


@app.put("/update_user/{user_id}")
def update_user(
    user_id: int,
    payload: UserUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    verify_token(credentials)

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    connection = get_connection()
    existing_user = connection.execute(
        "SELECT id, name, email, age FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    if not existing_user:
        connection.close()
        raise HTTPException(status_code=404, detail="User not found")

    fields = ", ".join(f"{field} = ?" for field in updates)
    values = list(updates.values()) + [user_id]

    try:
        connection.execute(f"UPDATE users SET {fields} WHERE id = ?", values)
        connection.commit()
    except sqlite3.IntegrityError as exc:
        connection.close()
        raise HTTPException(status_code=400, detail="Email already exists") from exc

    updated_user = connection.execute(
        "SELECT id, name, email, age FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    connection.close()
    return {"message": "User updated successfully", "user": dict(updated_user)}


@app.delete("/delete_user/{user_id}")
def delete_user(
    user_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    verify_token(credentials)
    connection = get_connection()
    deleted_user = connection.execute(
        "SELECT id, name, email, age FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    if not deleted_user:
        connection.close()
        raise HTTPException(status_code=404, detail="User not found")

    connection.execute("DELETE FROM users WHERE id = ?", (user_id,))
    connection.commit()
    connection.close()

    return {"message": "User deleted successfully", "user": dict(deleted_user)}
