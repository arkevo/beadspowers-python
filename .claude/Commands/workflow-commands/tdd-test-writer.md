---
description: TDD Python test writing methodology - 8-phase process for consistent, high-quality tests following pytest conventions and project standards
---

# TDD Python Test Writer

When executing TDD "RED: Write Failing Test" phase in this Python project, follow these 8 phases.

## RED Phase: Writing Failing Tests

### Phase 1: Analyze Target Code
- Use Glob to locate the target file(s) under `src/`
- Use Read to inspect the target file — classes, methods, signatures
- Use Grep to find referencing symbols and dependencies

### Phase 2: Select Test Type

| Testing | Use | Package |
|---------|-----|---------|
| Pure functions, business logic, models | Unit Test | `pytest` |
| Service interactions, database, APIs | Integration Test | `pytest` + fixtures |
| Full user flows, HTTP endpoints | E2E Test | `pytest` + `httpx` |

### Phase 3: Apply Test Templates

**Unit Test:**
```python
import pytest
from src.module import ClassName


class TestClassName:
    class TestMethodName:
        def test_expected_when_condition(self) -> None:
            # Arrange
            subject = ClassName()

            # Act
            result = subject.method_name(arg)

            # Assert
            assert result == expected
```

**Integration Test (with fixture):**
```python
import pytest
from src.services.my_service import MyService


@pytest.fixture
def service(fake_repo: FakeRepository) -> MyService:
    return MyService(repo=fake_repo)


class TestMyService:
    def test_expected_when_condition(self, service: MyService) -> None:
        # Arrange
        # Act
        result = service.do_something()
        # Assert
        assert result == expected
```

**E2E / HTTP Test:**
```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_expected_when_condition(client: AsyncClient) -> None:
    # Arrange
    payload = {"key": "value"}

    # Act
    response = await client.post("/endpoint", json=payload)

    # Assert
    assert response.status_code == 200
    assert response.json()["key"] == "value"
```

### Phase 4: Edge Case Checklist
- **None/Empty:** `None` inputs, empty strings, empty lists/dicts
- **Boundaries:** zero, negative, max/min integer values
- **Async:** success path, exception raised, timeout, cancellation
- **Types:** wrong type passed, unexpected subclass, protocol violation

### Phase 5: Use Fakes Over Mocks
```python
class FakeRepository:
    def __init__(self) -> None:
        self._items: list[str] = []
        self.should_raise: bool = False

    def set_items(self, items: list[str]) -> None:
        self._items = items

    def get_items(self) -> list[str]:
        if self.should_raise:
            raise RepositoryError("Failed")
        return self._items
```

### Phase 6: Naming Convention
Pattern: `test_[expected_behavior]_when_[condition]`

Examples:
- `test_returns_empty_list_when_no_items_exist`
- `test_raises_value_error_when_input_is_none`
- `test_calls_repo_once_when_cache_is_empty`

## GREEN Phase
- Write minimal code to pass the failing test
- Do not add functionality beyond what the test requires

## REFACTOR Phase

### Phase 7: pytest Utilities
```python
# Parametrize multiple cases
@pytest.mark.parametrize("input,expected", [
    (0, "zero"),
    (1, "one"),
    (-1, "negative"),
])
def test_label_when_given_value(input: int, expected: str) -> None:
    assert label(input) == expected

# Assert exceptions
with pytest.raises(ValueError, match="must be positive"):
    parse_value(-1)

# Approximate float comparison
assert compute() == pytest.approx(3.14, rel=1e-3)

# Temporary directory fixture
def test_writes_file(tmp_path: Path) -> None:
    output = tmp_path / "result.txt"
    write_output(output)
    assert output.read_text() == "done"
```

### Phase 8: Verify with Python Tools
1. `ruff check tests/` — check for lint errors
2. `ruff format tests/` — apply formatting
3. `pytest -v` — execute tests and confirm RED (failing) before GREEN

## Test Organization
Mirror `src/` structure in `tests/`. Example:
- `src/auth/login.py` → `tests/auth/test_login.py`
- `src/services/user_service.py` → `tests/services/test_user_service.py`

## Guidelines
- One assertion per test when practical (avoid asserting unrelated things)
- Test behavior, not implementation details
- Independent tests — no shared mutable state between test cases
- Use `setup_method` / `teardown_method` or fixtures for common init
- Prefer fakes/stubs over `unittest.mock.Mock`
- Use `pytest.mark.parametrize` for data-driven tests
- Use type hints in all test function signatures
