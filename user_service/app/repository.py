import sqlite3

from .database import get_connection


def insert_user(name: str, email: str, age: int) -> int:
    connection = get_connection()
    cursor = connection.execute(
        "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
        (name, email, age),
    )
    connection.commit()
    user_id = cursor.lastrowid
    connection.close()
    return user_id


def fetch_all_users() -> list[dict]:
    connection = get_connection()
    rows = connection.execute("SELECT id, name, email, age FROM users ORDER BY id").fetchall()
    connection.close()
    return [dict(row) for row in rows]


def fetch_user_by_id(user_id: int) -> sqlite3.Row | None:
    connection = get_connection()
    user = connection.execute(
        "SELECT id, name, email, age FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    connection.close()
    return user


def update_user_record(user_id: int, updates: dict) -> None:
    connection = get_connection()
    fields = ", ".join(f"{field} = ?" for field in updates)
    values = list(updates.values()) + [user_id]
    connection.execute(f"UPDATE users SET {fields} WHERE id = ?", values)
    connection.commit()
    connection.close()


def delete_user_record(user_id: int) -> None:
    connection = get_connection()
    connection.execute("DELETE FROM users WHERE id = ?", (user_id,))
    connection.commit()
    connection.close()


def replace_user_record(user_id: int, updates: dict) -> dict:
    connection = get_connection()
    fields = ", ".join(f"{field} = ?" for field in updates)
    values = list(updates.values()) + [user_id]
    connection.execute(f"UPDATE users SET {fields} WHERE id = ?", values)
    connection.commit()
    updated_user = connection.execute(
        "SELECT id, name, email, age FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    connection.close()
    return dict(updated_user)
