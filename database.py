import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Optional, TypedDict


class TaskDict(TypedDict):
    id: str
    title: str
    completed: bool
    created_at: str
    updated_at: str


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_db_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str) -> None:
    conn = get_db_connection(db_path)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


def _row_to_dict(row: sqlite3.Row) -> TaskDict:
    return {
        "id": row["id"],
        "title": row["title"],
        "completed": bool(row["completed"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def create_task(db_path: str, title: str) -> TaskDict:
    task_id = str(uuid.uuid4())
    now = _now_iso()
    conn = get_db_connection(db_path)
    try:
        conn.execute(
            "INSERT INTO tasks (id, title, completed, created_at, updated_at) VALUES (?, ?, 0, ?, ?)",
            (task_id, title, now, now),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return _row_to_dict(row)
    finally:
        conn.close()


def get_all_tasks(db_path: str) -> list[TaskDict]:
    conn = get_db_connection(db_path)
    try:
        rows = conn.execute("SELECT * FROM tasks ORDER BY created_at ASC").fetchall()
        return [_row_to_dict(r) for r in rows]
    finally:
        conn.close()


def get_task(db_path: str, task_id: str) -> Optional[TaskDict]:
    conn = get_db_connection(db_path)
    try:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return _row_to_dict(row) if row else None
    finally:
        conn.close()


def update_task(
    db_path: str,
    task_id: str,
    title: Optional[str] = None,
    completed: Optional[bool] = None,
) -> Optional[TaskDict]:
    task = get_task(db_path, task_id)
    if task is None:
        return None
    new_title = title if title is not None else task["title"]
    new_completed = completed if completed is not None else task["completed"]
    now = _now_iso()
    conn = get_db_connection(db_path)
    try:
        conn.execute(
            "UPDATE tasks SET title = ?, completed = ?, updated_at = ? WHERE id = ?",
            (new_title, int(new_completed), now, task_id),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return _row_to_dict(row)
    finally:
        conn.close()


def delete_task(db_path: str, task_id: str) -> bool:
    conn = get_db_connection(db_path)
    try:
        cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()
