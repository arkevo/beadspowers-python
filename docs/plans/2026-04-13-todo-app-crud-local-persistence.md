# To-Do App MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a minimal single-screen to-do app with full CRUD, local SQLite persistence, and a mobile-first vanilla JS frontend served by Flask.

**Architecture:** Flask serves a single-page HTML/CSS/JS frontend and a REST API backed by SQLite via Python's built-in `sqlite3`. All persistence lives in `todos.db` on the server. The frontend calls the API with `fetch()` — no frameworks, no build step.

**Tech Stack:** Python 3.10+, Flask 3.x, SQLite (stdlib), pytest, pytest-flask, vanilla HTML/CSS/JS

---

## File Structure

| File | Responsibility |
|------|----------------|
| `app.py` | Flask app factory + REST endpoints (CRUD for `/tasks`) |
| `database.py` | SQLite connection, schema init, all DB queries |
| `static/index.html` | Single-page UI shell |
| `static/style.css` | Mobile-first stylesheet |
| `static/app.js` | Frontend CRUD logic via fetch API |
| `requirements.txt` | Runtime dependencies |
| `requirements-dev.txt` | Dev/test dependencies |
| `tests/conftest.py` | pytest fixtures (test app, test client, temp DB) |
| `tests/test_database.py` | Unit tests for all DB functions |
| `tests/test_api.py` | Integration tests for all REST endpoints |

---

## Task 1: Project Bootstrap & Dependencies

**Files:**
- Create: `requirements.txt`
- Create: `requirements-dev.txt`

- [ ] **Step 1: Create requirements.txt**

```
flask>=3.0
```

- [ ] **Step 2: Create requirements-dev.txt**

```
pytest>=8.0
pytest-flask>=1.3
```

- [ ] **Step 3: Install dependencies**

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

Expected: installs Flask, pytest, pytest-flask with no errors.

- [ ] **Step 4: Add todos.db to .gitignore** <!-- Refined: file-organization -->

Create or append `.gitignore`:

```
todos.db
__pycache__/
*.pyc
.pytest_cache/
```

```bash
git add .gitignore requirements.txt requirements-dev.txt
```

- [ ] **Step 5: Commit**

```bash
git commit -m "chore: add Flask and test dependencies"
```

---

## Task 2: Database Layer (TDD)

**Files:**
- Create: `database.py`
- Create: `tests/conftest.py`
- Create: `tests/test_database.py`

- [ ] **Step 1: Write failing tests for database layer**

Create `tests/conftest.py`:

```python
import pytest
from database import init_db, get_db_connection


@pytest.fixture
def db_path(tmp_path):
    path = str(tmp_path / "test_todos.db")
    init_db(path)
    return path
```

Create `tests/test_database.py`:

```python
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
    assert updated["updated_at"] >= task["updated_at"]


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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_database.py -v
```

Expected: `ImportError` or `ModuleNotFoundError` — `database` module does not exist yet.

- [ ] **Step 3: Implement database.py**

Create `database.py`:

```python
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Optional


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_db_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str) -> None:
    conn = get_db_connection(db_path)
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
    conn.close()


def _row_to_dict(row) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "completed": bool(row["completed"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def create_task(db_path: str, title: str) -> dict:
    task_id = str(uuid.uuid4())
    now = _now_iso()
    conn = get_db_connection(db_path)
    conn.execute(
        "INSERT INTO tasks (id, title, completed, created_at, updated_at) VALUES (?, ?, 0, ?, ?)",
        (task_id, title, now, now),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return _row_to_dict(row)


def get_all_tasks(db_path: str) -> list[dict]:
    conn = get_db_connection(db_path)
    rows = conn.execute("SELECT * FROM tasks ORDER BY created_at ASC").fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_task(db_path: str, task_id: str) -> Optional[dict]:
    conn = get_db_connection(db_path)
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return _row_to_dict(row) if row else None


def update_task(
    db_path: str,
    task_id: str,
    title: Optional[str] = None,
    completed: Optional[bool] = None,
) -> Optional[dict]:
    task = get_task(db_path, task_id)
    if task is None:
        return None
    new_title = title if title is not None else task["title"]
    new_completed = completed if completed is not None else task["completed"]
    now = _now_iso()
    conn = get_db_connection(db_path)
    conn.execute(
        "UPDATE tasks SET title = ?, completed = ?, updated_at = ? WHERE id = ?",
        (new_title, int(new_completed), now, task_id),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return _row_to_dict(row)


def delete_task(db_path: str, task_id: str) -> bool:
    conn = get_db_connection(db_path)
    cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_database.py -v
```

Expected: all 11 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add database.py tests/conftest.py tests/test_database.py
git commit -m "feat: add SQLite database layer with full CRUD"
```

---

## Task 3: Flask REST API (TDD)

**Files:**
- Create: `app.py`
- Modify: `tests/conftest.py`
- Create: `tests/test_api.py`

- [ ] **Step 1: Write failing API tests**

Replace `tests/conftest.py` with: <!-- Refined: testing-strategy — lazy import inside fixture body so conftest loads cleanly before app.py exists -->

```python
import pytest
from database import init_db


@pytest.fixture
def db_path(tmp_path):
    path = str(tmp_path / "test_todos.db")
    init_db(path)
    return path


@pytest.fixture
def app(db_path):
    from app import create_app  # lazy import — app.py may not exist during Task 2
    flask_app = create_app(db_path=db_path)
    flask_app.config["TESTING"] = True
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()
```

Create `tests/test_api.py`:

```python
import json
import pytest


def test_get_tasks_empty(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_task_success(client):
    response = client.post(
        "/tasks",
        data=json.dumps({"title": "Buy groceries"}),
        content_type="application/json",
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "Buy groceries"
    assert data["completed"] is False
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_task_empty_title_rejected(client):
    response = client.post(
        "/tasks",
        data=json.dumps({"title": ""}),
        content_type="application/json",
    )
    assert response.status_code == 400


def test_create_task_whitespace_only_rejected(client):
    response = client.post(
        "/tasks",
        data=json.dumps({"title": "   "}),
        content_type="application/json",
    )
    assert response.status_code == 400


def test_create_task_missing_title_rejected(client):
    response = client.post(
        "/tasks",
        data=json.dumps({}),
        content_type="application/json",
    )
    assert response.status_code == 400


def test_get_tasks_returns_created_task(client):
    client.post(
        "/tasks",
        data=json.dumps({"title": "Task A"}),
        content_type="application/json",
    )
    response = client.get("/tasks")
    assert response.status_code == 200
    tasks = response.get_json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Task A"


def test_update_task_title(client):
    create_resp = client.post(
        "/tasks",
        data=json.dumps({"title": "Old title"}),
        content_type="application/json",
    )
    task_id = create_resp.get_json()["id"]
    response = client.patch(
        f"/tasks/{task_id}",
        data=json.dumps({"title": "New title"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.get_json()["title"] == "New title"


def test_update_task_completion(client):
    create_resp = client.post(
        "/tasks",
        data=json.dumps({"title": "My task"}),
        content_type="application/json",
    )
    task_id = create_resp.get_json()["id"]
    response = client.patch(
        f"/tasks/{task_id}",
        data=json.dumps({"completed": True}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.get_json()["completed"] is True


def test_update_task_empty_title_rejected(client):
    create_resp = client.post(
        "/tasks",
        data=json.dumps({"title": "Task"}),
        content_type="application/json",
    )
    task_id = create_resp.get_json()["id"]
    response = client.patch(
        f"/tasks/{task_id}",
        data=json.dumps({"title": ""}),
        content_type="application/json",
    )
    assert response.status_code == 400


def test_update_task_not_found(client):
    response = client.patch(
        "/tasks/nonexistent-id",
        data=json.dumps({"title": "X"}),
        content_type="application/json",
    )
    assert response.status_code == 404


def test_delete_task_success(client):
    create_resp = client.post(
        "/tasks",
        data=json.dumps({"title": "To delete"}),
        content_type="application/json",
    )
    task_id = create_resp.get_json()["id"]
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204


def test_delete_task_not_found(client):
    response = client.delete("/tasks/nonexistent-id")
    assert response.status_code == 404


def test_delete_task_no_longer_in_list(client):
    create_resp = client.post(
        "/tasks",
        data=json.dumps({"title": "Bye"}),
        content_type="application/json",
    )
    task_id = create_resp.get_json()["id"]
    client.delete(f"/tasks/{task_id}")
    tasks = client.get("/tasks").get_json()
    assert all(t["id"] != task_id for t in tasks)


def test_index_route_returns_html(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"html" in response.data.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_api.py -v
```

Expected: `ImportError` — `app` module does not exist yet.

- [ ] **Step 3: Implement app.py**

Create `app.py`:

```python
import os
from flask import Flask, jsonify, request, send_from_directory
from database import init_db, create_task, get_all_tasks, get_task, update_task, delete_task

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "todos.db")


def create_app(db_path: str = DEFAULT_DB_PATH) -> Flask:
    app = Flask(__name__, static_folder="static")
    app.config["DB_PATH"] = db_path
    init_db(db_path)

    @app.route("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.route("/tasks", methods=["GET"])
    def list_tasks():
        tasks = get_all_tasks(app.config["DB_PATH"])
        return jsonify(tasks), 200

    @app.route("/tasks", methods=["POST"])
    def add_task():
        body = request.get_json(silent=True) or {}
        title = (body.get("title") or "").strip()
        if not title:
            return jsonify({"error": "title is required and cannot be empty"}), 400
        task = create_task(app.config["DB_PATH"], title)
        return jsonify(task), 201

    @app.route("/tasks/<task_id>", methods=["PATCH"])
    def edit_task(task_id):
        if get_task(app.config["DB_PATH"], task_id) is None:
            return jsonify({"error": "task not found"}), 404
        body = request.get_json(silent=True) or {}
        title = body.get("title")
        completed = body.get("completed")
        if title is not None and not str(title).strip():
            return jsonify({"error": "title cannot be empty"}), 400
        if title is not None:
            title = str(title).strip()
        updated = update_task(app.config["DB_PATH"], task_id, title=title, completed=completed)
        return jsonify(updated), 200

    @app.route("/tasks/<task_id>", methods=["DELETE"])
    def remove_task(task_id):
        deleted = delete_task(app.config["DB_PATH"], task_id)
        if not deleted:
            return jsonify({"error": "task not found"}), 404
        return "", 204

    return app


if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(debug=True, port=5000)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_api.py -v
```

Expected: all 14 tests PASS.

- [ ] **Step 5: Run full test suite**

```bash
pytest -v
```

Expected: all 25 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add app.py tests/test_api.py tests/conftest.py
git commit -m "feat: add Flask REST API with CRUD endpoints"
```

---

## Task 4: Frontend HTML Shell

**Files:**
- Create: `static/index.html`

- [ ] **Step 1: Create static directory and index.html**

```bash
mkdir -p static
```

Create `static/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>My Tasks</title>
  <link rel="stylesheet" href="/static/style.css" />
</head>
<body>
  <div class="app">
    <header class="app-header">
      <h1>My Tasks</h1>
      <span id="task-count" class="task-count" aria-live="polite"></span>
    </header>

    <section class="input-section" aria-label="Add new task">
      <form id="add-form" class="add-form">
        <label for="task-input" class="sr-only">New task</label>
        <input
          id="task-input"
          type="text"
          class="task-input"
          placeholder="What needs to get done?"
          aria-label="New task"
          autocomplete="off"
          maxlength="200"
        />
        <button type="submit" id="add-btn" class="btn btn-primary" aria-label="Add task" disabled>+</button>
      </form>
    </section>

    <nav class="filter-nav" aria-label="Filter tasks">
      <button class="filter-btn active" data-filter="all" aria-pressed="true">All</button>
      <button class="filter-btn" data-filter="active" aria-pressed="false">Active</button>
      <button class="filter-btn" data-filter="completed" aria-pressed="false">Completed</button>
    </nav>

    <main>
      <ul id="task-list" class="task-list" aria-label="Task list" aria-live="polite"></ul>
      <div id="empty-state" class="empty-state" hidden>
        <p>No tasks yet</p>
        <p class="empty-subtitle">Add your first task to begin.</p>
      </div>
    </main>
  </div>

  <!-- Toast notification for API errors --> <!-- Refined: error-handling -->
  <div id="toast" class="toast" role="alert" aria-live="assertive" hidden></div>

  <script src="/static/app.js"></script>
</body>
</html>
```

- [ ] **Step 2: Verify the route serves it**

```bash
python app.py &
curl -s http://localhost:5000/ | grep "My Tasks"
kill %1
```

Expected: output contains `My Tasks`.

- [ ] **Step 3: Commit**

```bash
git add static/index.html
git commit -m "feat: add HTML shell for single-page todo app"
```

---

## Task 5: Stylesheet (Mobile-First)

**Files:**
- Create: `static/style.css`

- [ ] **Step 1: Create style.css**

Create `static/style.css`:

```css
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

:root {
  --accent: #5b6af0;
  --accent-hover: #4353d9;
  --bg: #f9f9fb;
  --surface: #ffffff;
  --border: #e4e4e8;
  --text: #1a1a2e;
  --text-muted: #8a8a9a;
  --completed-text: #b0b0c0;
  --danger: #e05252;
  --radius: 10px;
  --shadow: 0 2px 8px rgba(0,0,0,0.07);
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  padding: 0 0 2rem;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
}

.app {
  max-width: 600px;
  margin: 0 auto;
  padding: 0 1rem;
}

.app-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.5rem 0 1rem;
}

.app-header h1 {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.task-count {
  font-size: 0.85rem;
  color: var(--text-muted);
  background: var(--border);
  padding: 0.1rem 0.5rem;
  border-radius: 99px;
}

.input-section {
  margin-bottom: 1rem;
}

.add-form {
  display: flex;
  gap: 0.5rem;
}

.task-input {
  flex: 1;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
  color: var(--text);
  outline: none;
  min-height: 44px;
}

.task-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(91,106,240,0.15);
}

.task-input::placeholder {
  color: var(--text-muted);
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 44px;
  min-height: 44px;
  border: none;
  border-radius: var(--radius);
  font-size: 1.25rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, opacity 0.15s;
}

.btn:focus-visible {
  outline: 3px solid var(--accent);
  outline-offset: 2px;
}

.btn-primary {
  background: var(--accent);
  color: #fff;
  padding: 0 1rem;
}

.btn-primary:hover:not(:disabled) {
  background: var(--accent-hover);
}

.btn-primary:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-icon {
  background: transparent;
  color: var(--text-muted);
  padding: 0;
  font-size: 1rem;
}

.btn-icon:hover {
  color: var(--text);
}

.btn-delete:hover {
  color: var(--danger);
}

.filter-nav {
  display: flex;
  gap: 0.25rem;
  margin-bottom: 1rem;
}

.filter-btn {
  padding: 0.4rem 0.9rem;
  border: 1.5px solid var(--border);
  border-radius: 99px;
  background: transparent;
  color: var(--text-muted);
  font-size: 0.9rem;
  cursor: pointer;
  min-height: 44px;
  transition: all 0.15s;
}

.filter-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.filter-btn.active {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
}

.filter-btn:focus-visible {
  outline: 3px solid var(--accent);
  outline-offset: 2px;
}

.task-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.task-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  padding: 0.75rem 0.75rem;
  box-shadow: var(--shadow);
  transition: border-color 0.15s;
}

.task-row:hover {
  border-color: var(--accent);
}

.task-checkbox {
  appearance: none;
  width: 22px;
  height: 22px;
  min-width: 22px;
  border: 2px solid var(--border);
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
  background: transparent;
}

.task-checkbox:checked {
  background: var(--accent);
  border-color: var(--accent);
}

.task-checkbox:checked::after {
  content: "checkmark";
  color: #fff;
  font-size: 0.75rem;
  line-height: 1;
}

.task-checkbox:focus-visible {
  outline: 3px solid var(--accent);
  outline-offset: 2px;
}

.task-text {
  flex: 1;
  font-size: 1rem;
  word-break: break-word;
  cursor: default;
}

.task-row.completed .task-text {
  text-decoration: line-through;
  color: var(--completed-text);
}

.task-edit-input {
  flex: 1;
  font-size: 1rem;
  padding: 0.25rem 0.5rem;
  border: 1.5px solid var(--accent);
  border-radius: 6px;
  outline: none;
  color: var(--text);
  background: var(--bg);
}

.task-actions {
  display: flex;
  gap: 0.25rem;
  flex-shrink: 0;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--text-muted);
}

.empty-state p {
  font-size: 1.1rem;
}

.empty-subtitle {
  font-size: 0.9rem !important;
  margin-top: 0.5rem;
}

/* Toast */ /* Refined: error-handling */
.toast {
  position: fixed;
  bottom: 1.5rem;
  left: 50%;
  transform: translateX(-50%);
  background: #e05252;
  color: #fff;
  padding: 0.65rem 1.25rem;
  border-radius: var(--radius);
  font-size: 0.9rem;
  box-shadow: var(--shadow);
  z-index: 100;
  transition: opacity 0.3s;
}

.toast[hidden] {
  display: none;
}
```

- [ ] **Step 2: Commit**

```bash
git add static/style.css
git commit -m "feat: add mobile-first stylesheet"
```

---

## Task 6: Frontend JavaScript (CRUD Logic)

**Files:**
- Create: `static/app.js`

**Security note:** All user-supplied content is set via `textContent` (not `innerHTML`) to prevent XSS. DOM elements are built with `document.createElement` and property assignment.

<!-- Refined: error-handling — toast replaces console.error; Refined: edge-cases — activeEditId prevents multiple simultaneous edit rows -->

- [ ] **Step 1: Create app.js**

Create `static/app.js`:

```javascript
const API = "/tasks";
let tasks = [];
let activeFilter = "all";
let activeEditId = null; // Refined: edge-cases — track which task row is in edit mode

// ---- Toast (error feedback) ---- // Refined: error-handling
let _toastTimer = null;
function showToast(message) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.hidden = false;
  clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => { toast.hidden = true; }, 3000);
}

// ---- API helpers ----

async function fetchTasks() {
  const res = await fetch(API);
  tasks = await res.json();
  renderTasks();
}

async function apiCreateTask(title) {
  const res = await fetch(API, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  if (!res.ok) throw new Error("Failed to create task");
  return res.json();
}

async function apiUpdateTask(id, patch) {
  const res = await fetch(`${API}/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(patch),
  });
  if (!res.ok) throw new Error("Failed to update task");
  return res.json();
}

async function apiDeleteTask(id) {
  const res = await fetch(`${API}/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete task");
}

// ---- DOM helpers ----

function createButton(className, label, text) {
  const btn = document.createElement("button");
  btn.className = `btn btn-icon ${className}`;
  btn.setAttribute("aria-label", label);
  btn.setAttribute("title", label);
  btn.textContent = text;
  return btn;
}

// ---- Render ----

function filteredTasks() {
  if (activeFilter === "active") return tasks.filter((t) => !t.completed);
  if (activeFilter === "completed") return tasks.filter((t) => t.completed);
  return tasks;
}

function renderTasks() {
  const list = document.getElementById("task-list");
  const emptyState = document.getElementById("empty-state");
  const countEl = document.getElementById("task-count");

  const visible = filteredTasks();
  const activeCount = tasks.filter((t) => !t.completed).length;

  countEl.textContent = activeCount > 0 ? `${activeCount} left` : "";
  list.textContent = "";

  if (visible.length === 0) {
    emptyState.hidden = false;
    return;
  }
  emptyState.hidden = true;

  visible.forEach((task) => {
    const li = document.createElement("li");
    li.className = `task-row${task.completed ? " completed" : ""}`;
    li.dataset.id = task.id;

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.className = "task-checkbox";
    checkbox.checked = task.completed;
    checkbox.setAttribute("aria-label", task.completed ? "Mark incomplete" : "Mark complete");

    const span = document.createElement("span");
    span.className = "task-text";
    span.textContent = task.title;

    const actions = document.createElement("div");
    actions.className = "task-actions";
    actions.appendChild(createButton("btn-edit", "Edit task", "\u270F\uFE0F"));
    actions.appendChild(createButton("btn-delete", "Delete task", "\uD83D\uDDD1\uFE0F"));

    li.appendChild(checkbox);
    li.appendChild(span);
    li.appendChild(actions);
    list.appendChild(li);
  });
}

// ---- Add task ----

document.getElementById("add-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const input = document.getElementById("task-input");
  const title = input.value.trim();
  if (!title) return;
  input.disabled = true;
  try {
    const task = await apiCreateTask(title);
    tasks.push(task);
    input.value = "";
    document.getElementById("add-btn").disabled = true;
    renderTasks();
    input.focus();
  } catch (err) {
    showToast("Failed to add task — please try again.");
  } finally {
    input.disabled = false;
  }
});

document.getElementById("task-input").addEventListener("input", (e) => {
  document.getElementById("add-btn").disabled = !e.target.value.trim();
});

// ---- Task list delegation ----

document.getElementById("task-list").addEventListener("click", async (e) => {
  const row = e.target.closest(".task-row");
  if (!row) return;
  const id = row.dataset.id;

  if (e.target.matches(".task-checkbox")) {
    const completed = e.target.checked;
    try {
      const updated = await apiUpdateTask(id, { completed });
      const idx = tasks.findIndex((t) => t.id === id);
      if (idx !== -1) tasks[idx] = updated;
      renderTasks();
    } catch (err) {
      e.target.checked = !completed;
      showToast("Failed to update task — please try again.");
    }
    return;
  }

  if (e.target.closest(".btn-delete")) {
    try {
      await apiDeleteTask(id);
      tasks = tasks.filter((t) => t.id !== id);
      renderTasks();
    } catch (err) {
      showToast("Failed to delete task — please try again.");
    }
    return;
  }

  if (e.target.closest(".btn-edit")) {
    // Refined: edge-cases — cancel any existing edit before opening a new one
    if (activeEditId && activeEditId !== id) {
      renderTasks();
    }
    enterEditMode(row, id);
    return;
  }
});

function enterEditMode(row, id) {
  const task = tasks.find((t) => t.id === id);
  if (!task) return;
  activeEditId = id; // Refined: edge-cases

  const textSpan = row.querySelector(".task-text");
  const actions = row.querySelector(".task-actions");

  const input = document.createElement("input");
  input.type = "text";
  input.className = "task-edit-input";
  input.value = task.title;
  input.setAttribute("aria-label", "Edit task text");
  input.maxLength = 200;

  textSpan.replaceWith(input);

  actions.textContent = "";
  const saveBtn = createButton("btn-save", "Save task", "\u2705");
  const cancelBtn = createButton("btn-cancel", "Cancel edit", "\u274C");
  actions.appendChild(saveBtn);
  actions.appendChild(cancelBtn);

  input.focus();
  input.select();

  async function saveEdit() {
    const newTitle = input.value.trim();
    if (!newTitle) {
      input.focus();
      return;
    }
    try {
      const updated = await apiUpdateTask(id, { title: newTitle });
      const idx = tasks.findIndex((t) => t.id === id);
      if (idx !== -1) tasks[idx] = updated;
      activeEditId = null;
      renderTasks();
    } catch (err) {
      showToast("Failed to save edit — please try again.");
    }
  }

  function cancelEdit() {
    activeEditId = null;
    renderTasks();
  }

  saveBtn.addEventListener("click", saveEdit);
  cancelBtn.addEventListener("click", cancelEdit);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") saveEdit();
    if (e.key === "Escape") cancelEdit();
  });
}

// ---- Filter ----

document.querySelector(".filter-nav").addEventListener("click", (e) => {
  const btn = e.target.closest(".filter-btn");
  if (!btn) return;
  document.querySelectorAll(".filter-btn").forEach((b) => {
    b.classList.remove("active");
    b.setAttribute("aria-pressed", "false");
  });
  btn.classList.add("active");
  btn.setAttribute("aria-pressed", "true");
  activeFilter = btn.dataset.filter;
  renderTasks();
});

// ---- Init ----
fetchTasks();
```

- [ ] **Step 2: Commit**

```bash
git add static/app.js
git commit -m "feat: add frontend JS with safe DOM manipulation and CRUD logic"
```

---

## Task 7: Manual Smoke Test

- [ ] **Step 1: Start the server**

```bash
python app.py
```

Expected: Flask starts on http://127.0.0.1:5000

- [ ] **Step 2: Verify in browser**

Open http://127.0.0.1:5000 and confirm:
- Page loads with "My Tasks" header
- Empty state shows "No tasks yet"
- Typing in input enables the + button
- Submitting a task adds it to the list
- Checkbox toggles completion (strikethrough styling)
- Edit button enables inline editing, Enter saves, Escape cancels
- Delete button removes the task
- Filter tabs (All / Active / Completed) filter the list correctly
- Refreshing the page preserves all tasks (SQLite persistence)

- [ ] **Step 3: Verify empty submission is blocked**

Clear the input and try clicking + — button should be disabled.

- [ ] **Step 4: Stop the server**

```bash
Ctrl+C
```

---

## Task 8: Final Test Run & Cleanup

- [ ] **Step 1: Run full test suite**

```bash
pytest -v
```

Expected: all 25 tests PASS, 0 failures.

- [ ] **Step 2: Remove any todos.db test artifact**

```bash
rm -f todos.db
```

- [ ] **Step 3: Final commit**

```bash
git status
git add docs/ static/ tests/ app.py database.py requirements.txt requirements-dev.txt
git commit -m "chore: final cleanup before PR"
```

---

## Self-Review Against Spec

| Requirement | Task(s) |
|-------------|---------|
| FR-1: Single text input + submit | Task 4, 6 |
| FR-2: New task appears immediately | Task 6 |
| FR-3: Toggle completion | Task 3, 6 |
| FR-4: Completed tasks distinct style | Task 5, 6 |
| FR-5: Edit task text | Task 3, 6 |
| FR-6: Delete task | Task 3, 6 |
| FR-7: Persist after refresh | Task 2 (SQLite) |
| FR-8: Empty state | Task 4, 6 |
| FR-9: Prevent empty submission | Task 3, 6 |
| FR-10: Filter by status (optional) | Task 4, 6 |
| AC-1 through AC-8 | All tasks above |
| Edge: whitespace-only title rejected | Task 3 (test_create_task_whitespace_only_rejected) |
| Edge: edit to blank rejected | Task 3 (test_update_task_empty_title_rejected), Task 6 |
| XSS prevention | Task 6 (textContent + createElement, no innerHTML for user data) |

---

## Refinement Decisions

Decisions from plan refinement Q&A on 2026-04-13:

| # | Category | Tier | Decision | Rationale |
|---|----------|------|----------|-----------|
| 1 | Testing Strategy | Critical | Lazy import — `from app import create_app` inside the `app` fixture body, not module-level | Prevents conftest.py from failing to load when app.py does not yet exist during Task 2 TDD red step |
| 2 | Error Handling | Critical | Toast notification — `<div id="toast">` with `textContent`, auto-dismisses after 3s | Usability test goal requires visible failure feedback; silent errors look identical to bugs |
| 3 | Architecture | Recommended | Keep per-call SQLite connections (as written) | Per-call connections are simpler and self-contained; Flask `g` adds complexity with no benefit for a single-user local app |
| 4 | Edge Cases | Recommended | Auto-cancel existing edit mode when a new edit is opened (`activeEditId` guard) | Prevents two task rows being in edit mode simultaneously, which causes confusing UI state |
| 5 | File Organization | Nice-to-have | Add `todos.db` to `.gitignore` in Task 1 | Runtime artifact should not be committed |

All requirements covered. No placeholders.
