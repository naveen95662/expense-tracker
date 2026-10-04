from datetime import date
from uuid import uuid4

import boto3
import pytest
from moto import mock_aws

from app import config
from app.models import ExpenseCreate
from app.store import DynamoDbExpenseStore


@pytest.fixture
def dynamodb_store(monkeypatch: pytest.MonkeyPatch) -> DynamoDbExpenseStore:
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setattr(config, "TABLE_NAME", "expenses")

    with mock_aws():
        table_name = "expenses"
        resource = boto3.resource("dynamodb", region_name="us-east-1")
        resource.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        yield DynamoDbExpenseStore()


def test_create_expense(dynamodb_store: DynamoDbExpenseStore) -> None:
    created = dynamodb_store.create(
        ExpenseCreate(amount=12.5, category="food", description="lunch")
    )
    assert created.amount == 12.5
    assert created.category == "food"
    assert created.description == "lunch"
    assert created.date == date.today()
    listed = dynamodb_store.list()
    assert len(listed) == 1
    assert listed[0].id == created.id
    assert listed[0].amount == 12.5


def test_list_expenses(dynamodb_store: DynamoDbExpenseStore) -> None:
    dynamodb_store.create(ExpenseCreate(amount=5, category="food"))
    dynamodb_store.create(ExpenseCreate(amount=20, category="travel"))
    items = dynamodb_store.list()
    assert len(items) == 2
    assert {item.category for item in items} == {"food", "travel"}


def test_list_filtered_by_category(dynamodb_store: DynamoDbExpenseStore) -> None:
    dynamodb_store.create(ExpenseCreate(amount=5, category="food"))
    dynamodb_store.create(ExpenseCreate(amount=20, category="travel"))
    items = dynamodb_store.list(category="food")
    assert len(items) == 1
    assert items[0].category == "food"
    assert items[0].amount == 5


def test_delete_existing(dynamodb_store: DynamoDbExpenseStore) -> None:
    created = dynamodb_store.create(ExpenseCreate(amount=8, category="food"))
    assert dynamodb_store.delete(created.id) is True
    assert dynamodb_store.list() == []


def test_delete_missing(dynamodb_store: DynamoDbExpenseStore) -> None:
    assert dynamodb_store.delete(uuid4()) is False


def test_summary(dynamodb_store: DynamoDbExpenseStore) -> None:
    dynamodb_store.create(ExpenseCreate(amount=10, category="food"))
    dynamodb_store.create(ExpenseCreate(amount=5, category="food"))
    assert dynamodb_store.summary() == {"food": 15.0}


def test_summary_multiple_categories(dynamodb_store: DynamoDbExpenseStore) -> None:
    dynamodb_store.create(ExpenseCreate(amount=10, category="food"))
    dynamodb_store.create(ExpenseCreate(amount=5, category="food"))
    dynamodb_store.create(ExpenseCreate(amount=30, category="rent"))
    assert dynamodb_store.summary() == {"food": 15.0, "rent": 30.0}
