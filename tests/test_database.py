import pytest
from database import (
    init_db,
    create_task,
    get_all_tasks,
    get_task,
    update_task,
    delete_task,
)


def test_init_db_creates_tasks_table(db_path):
    from database import get_db_connection
    conn = get_db_connection(db_path)
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
    assert cursor.fetchone() is not None
    conn.close()


def test_create_task_returns_task_with_id(db_path):
    task = create_task(db_path, "Buy groceries")
    assert task["id"] is not None
    assert task["title"] == "Buy groceries"
    assert task["completed"] is False
    assert task["created_at"] is not None
    assert task["updated_at"] is not None


def test_get_all_tasks_returns_empty_list_initially(db_path):
    tasks = get_all_tasks(db_path)
    assert tasks == []


def test_get_all_tasks_returns_created_tasks(db_path):
    create_task(db_path, "Task A")
    create_task(db_path, "Task B")
    tasks = get_all_tasks(db_path)
    assert len(tasks) == 2
    titles = [t["title"] for t in tasks]
    assert "Task A" in titles
    assert "Task B" in titles


def test_get_task_returns_correct_task(db_path):
    created = create_task(db_path, "Specific task")
    fetched = get_task(db_path, created["id"])
    assert fetched["id"] == created["id"]
    assert fetched["title"] == "Specific task"


def test_get_task_returns_none_for_missing_id(db_path):
    result = get_task(db_path, "nonexistent-id")
    assert result is None


def test_update_task_title(db_path):
    task = create_task(db_path, "Old title")
    updated = update_task(db_path, task["id"], title="New title")
    assert updated["title"] == "New title"
    assert updated["completed"] is False


def test_update_task_completion(db_path):
    task = create_task(db_path, "My task")
    updated = update_task(db_path, task["id"], completed=True)
    assert updated["completed"] is True


def test_update_task_updated_at_changes(db_path):
    import time
    task = create_task(db_path, "Task")
    time.sleep(0.01)
    updated = update_task(db_path, task["id"], title="Updated")
    assert updated["updated_at"] > task["updated_at"]


def test_delete_task_removes_it(db_path):
    task = create_task(db_path, "To delete")
    delete_task(db_path, task["id"])
    assert get_task(db_path, task["id"]) is None


def test_delete_task_returns_true_on_success(db_path):
    task = create_task(db_path, "To delete")
    result = delete_task(db_path, task["id"])
    assert result is True


def test_delete_task_returns_false_for_missing_id(db_path):
    result = delete_task(db_path, "nonexistent-id")
    assert result is False
