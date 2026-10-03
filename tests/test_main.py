from uuid import uuid4

from fastapi.testclient import TestClient


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_expense_returns_201(client: TestClient) -> None:
    response = client.post(
        "/expenses",
        json={"amount": 12.5, "category": "food", "description": "lunch"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["amount"] == 12.5
    assert body["category"] == "food"
    assert body["description"] == "lunch"
    assert "id" in body
    assert "date" in body


def test_create_rejects_invalid_amount(client: TestClient) -> None:
    response = client.post("/expenses", json={"amount": 0, "category": "food"})
    assert response.status_code == 422


def test_create_rejects_blank_category(client: TestClient) -> None:
    response = client.post("/expenses", json={"amount": 10, "category": "   "})
    assert response.status_code == 422


def test_list_expenses(client: TestClient) -> None:
    client.post("/expenses", json={"amount": 5, "category": "food"})
    client.post("/expenses", json={"amount": 20, "category": "travel"})
    response = client.get("/expenses")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 2
    categories = {item["category"] for item in items}
    assert categories == {"food", "travel"}


def test_list_expenses_filtered_by_category(client: TestClient) -> None:
    client.post("/expenses", json={"amount": 5, "category": "food"})
    client.post("/expenses", json={"amount": 20, "category": "travel"})
    response = client.get("/expenses", params={"category": "food"})
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["category"] == "food"
    assert items[0]["amount"] == 5


def test_summary_totals_across_categories(client: TestClient) -> None:
    client.post("/expenses", json={"amount": 10, "category": "food"})
    client.post("/expenses", json={"amount": 5, "category": "food"})
    client.post("/expenses", json={"amount": 30, "category": "rent"})
    response = client.get("/expenses/summary")
    assert response.status_code == 200
    assert response.json()["totals"] == {"food": 15.0, "rent": 30.0}


def test_delete_expense_returns_204(client: TestClient) -> None:
    created = client.post("/expenses", json={"amount": 8, "category": "food"})
    expense_id = created.json()["id"]
    response = client.delete(f"/expenses/{expense_id}")
    assert response.status_code == 204
    assert client.get("/expenses").json() == []


def test_delete_unknown_id_returns_404(client: TestClient) -> None:
    response = client.delete(f"/expenses/{uuid4()}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Expense not found"


def test_summary_after_delete(client: TestClient) -> None:
    food = client.post("/expenses", json={"amount": 10, "category": "food"})
    client.post("/expenses", json={"amount": 40, "category": "travel"})
    client.delete(f"/expenses/{food.json()['id']}")
    response = client.get("/expenses/summary")
    assert response.status_code == 200
    assert response.json()["totals"] == {"travel": 40.0}

def test_create_rejects_negative_amount(client: TestClient) -> None:
    response = client.post("/expenses", json={"amount": -5, "category": "food"})
    assert response.status_code == 422
