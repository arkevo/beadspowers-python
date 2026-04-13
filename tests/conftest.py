import pytest
from database import init_db, get_db_connection


@pytest.fixture
def db_path(tmp_path):
    path = str(tmp_path / "test_todos.db")
    init_db(path)
    return path
