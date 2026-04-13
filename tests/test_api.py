import json


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


def test_update_task_empty_body_succeeds(client):
    """PATCH with no fields should succeed and preserve title and completed status."""
    create_resp = client.post(
        "/tasks",
        data=json.dumps({"title": "Stable task"}),
        content_type="application/json",
    )
    task = create_resp.get_json()
    response = client.patch(
        f"/tasks/{task['id']}",
        data=json.dumps({}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.get_json()["title"] == "Stable task"


def test_update_task_toggle_to_incomplete(client):
    """Toggle a completed task back to incomplete."""
    create_resp = client.post(
        "/tasks",
        data=json.dumps({"title": "Done task"}),
        content_type="application/json",
    )
    task_id = create_resp.get_json()["id"]
    client.patch(
        f"/tasks/{task_id}",
        data=json.dumps({"completed": True}),
        content_type="application/json",
    )
    response = client.patch(
        f"/tasks/{task_id}",
        data=json.dumps({"completed": False}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.get_json()["completed"] is False


def test_update_task_whitespace_title_rejected(client):
    """PATCH with whitespace-only title should be rejected."""
    create_resp = client.post(
        "/tasks",
        data=json.dumps({"title": "Real task"}),
        content_type="application/json",
    )
    task_id = create_resp.get_json()["id"]
    response = client.patch(
        f"/tasks/{task_id}",
        data=json.dumps({"title": "   "}),
        content_type="application/json",
    )
    assert response.status_code == 400
