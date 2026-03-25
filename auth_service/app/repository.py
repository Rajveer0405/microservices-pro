import sqlite3

from .database import get_connection


def insert_user(username: str, password: str) -> None:
    connection = get_connection()
    connection.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (username, password),
    )
    connection.commit()
    connection.close()


def fetch_user_password(username: str) -> str | None:
    connection = get_connection()
    user = connection.execute(
        "SELECT password FROM users WHERE username = ?",
        (username,),
    ).fetchone()
    connection.close()
    return None if user is None else user["password"]


def insert_token(token: str, username: str, expires_at: str) -> None:
    connection = get_connection()
    connection.execute(
        "INSERT INTO tokens (token, username, expires_at) VALUES (?, ?, ?)",
        (token, username, expires_at),
    )
    connection.commit()
    connection.close()


def fetch_token(token: str) -> sqlite3.Row | None:
    connection = get_connection()
    token_row = connection.execute(
        "SELECT username, expires_at FROM tokens WHERE token = ?",
        (token,),
    ).fetchone()
    connection.close()
    return token_row


def remove_token(token: str) -> None:
    connection = get_connection()
    connection.execute("DELETE FROM tokens WHERE token = ?", (token,))
    connection.commit()
    connection.close()
