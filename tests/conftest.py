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
