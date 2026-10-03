import pytest
from fastapi.testclient import TestClient

from app.main import app, get_store
from app.store import InMemoryExpenseStore


@pytest.fixture
def client() -> TestClient:
    store = InMemoryExpenseStore()
    app.dependency_overrides[get_store] = lambda: store
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
