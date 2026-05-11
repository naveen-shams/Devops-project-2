import pytest
from app.main import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_metrics_endpoint(client):
    res = client.get("/metrics")
    assert res.status_code == 200


def test_create_todo(client):
    res = client.post("/api/todos", json={"title": "Learn DevOps"})
    assert res.status_code == 201
    data = res.get_json()
    assert data["title"] == "Learn DevOps"
    assert data["done"] is False


def test_get_todos(client):
    client.post("/api/todos", json={"title": "Task 1"})
    res = client.get("/api/todos")
    assert res.status_code == 200
    assert len(res.get_json()) >= 1


def test_update_todo(client):
    res = client.post("/api/todos", json={"title": "Old title"})
    todo_id = res.get_json()["id"]
    res = client.put(f"/api/todos/{todo_id}", json={"done": True})
    assert res.status_code == 200
    assert res.get_json()["done"] is True


def test_delete_todo(client):
    res = client.post("/api/todos", json={"title": "To delete"})
    todo_id = res.get_json()["id"]
    res = client.delete(f"/api/todos/{todo_id}")
    assert res.status_code == 204


def test_get_nonexistent_todo(client):
    res = client.get("/api/todos/99999")
    assert res.status_code == 404


def test_create_todo_missing_title(client):
    res = client.post("/api/todos", json={})
    assert res.status_code == 400
