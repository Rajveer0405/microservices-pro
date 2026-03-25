import sqlite3

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from .auth_client import verify_token as verify_with_auth_service
from .repository import delete_user_record, fetch_all_users, fetch_user_by_id, insert_user, replace_user_record


def require_token(credentials: HTTPAuthorizationCredentials | None) -> dict:
    return verify_with_auth_service(credentials)


def list_users() -> dict:
    return {"users": fetch_all_users()}


def create_user(payload: dict) -> dict:
    try:
        user_id = insert_user(payload["name"], payload["email"], payload["age"])
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail="Email already exists") from exc

    user = {**payload, "id": user_id}
    return {"message": "User added successfully", "user": user}


def update_user(user_id: int, updates: dict) -> dict:
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    existing_user = fetch_user_by_id(user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        updated_user = replace_user_record(user_id, updates)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail="Email already exists") from exc

    return {"message": "User updated successfully", "user": updated_user}


def delete_user(user_id: int) -> dict:
    existing_user = fetch_user_by_id(user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    delete_user_record(user_id)
    return {"message": "User deleted successfully", "user": dict(existing_user)}
