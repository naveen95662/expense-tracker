from __future__ import annotations

import os
from datetime import date
from decimal import Decimal
from typing import Any, Protocol
from uuid import UUID, uuid4

from botocore.exceptions import ClientError

from app import config
from app.models import Expense, ExpenseCreate


class ExpenseStore(Protocol):
    def create(self, payload: ExpenseCreate) -> Expense: ...

    def list(self, category: str | None = None) -> list[Expense]: ...

    def delete(self, expense_id: UUID) -> bool: ...

    def summary(self) -> dict[str, float]: ...


class InMemoryExpenseStore:
    """Dict-backed store. Replace with DynamoDB later without changing routes."""

    def __init__(self) -> None:
        self._items: dict[UUID, Expense] = {}

    def create(self, payload: ExpenseCreate) -> Expense:
        expense = Expense(
            id=uuid4(),
            amount=payload.amount,
            category=payload.category,
            description=payload.description,
            date=payload.date or date.today(),
        )
        self._items[expense.id] = expense
        return expense

    def list(self, category: str | None = None) -> list[Expense]:
        items = list(self._items.values())
        if category is not None:
            needle = category.strip()
            items = [item for item in items if item.category == needle]
        return items

    def delete(self, expense_id: UUID) -> bool:
        if expense_id not in self._items:
            return False
        del self._items[expense_id]
        return True

    def summary(self) -> dict[str, float]:
        totals: dict[str, float] = {}
        for item in self._items.values():
            totals[item.category] = round(totals.get(item.category, 0.0) + item.amount, 2)
        return totals


class DynamoDbExpenseStore:
    """DynamoDB-backed store. Credentials and region come from the environment."""

    def __init__(self) -> None:
        import boto3
        from boto3.dynamodb.conditions import Attr

        self._Attr = Attr
        region = os.environ.get("AWS_REGION")
        resource_kwargs: dict[str, str] = {}
        if region:
            resource_kwargs["region_name"] = region
        resource = boto3.resource("dynamodb", **resource_kwargs)
        self._table = resource.Table(config.TABLE_NAME)

    def create(self, payload: ExpenseCreate) -> Expense:
        expense = Expense(
            id=uuid4(),
            amount=payload.amount,
            category=payload.category,
            description=payload.description,
            date=payload.date or date.today(),
        )
        item: dict[str, Any] = {
            "id": str(expense.id),
            "amount": Decimal(str(expense.amount)),
            "category": expense.category,
            "date": expense.date.isoformat(),
        }
        if expense.description is not None:
            item["description"] = expense.description
        self._table.put_item(Item=item)
        return expense

    def list(self, category: str | None = None) -> list[Expense]:
        scan_kwargs: dict[str, Any] = {}
        if category is not None:
            scan_kwargs["FilterExpression"] = self._Attr("category").eq(category.strip())
        return [self._to_expense(item) for item in self._scan(**scan_kwargs)]

    def delete(self, expense_id: UUID) -> bool:
        try:
            self._table.delete_item(
                Key={"id": str(expense_id)},
                ConditionExpression="attribute_exists(id)",
            )
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return False
            raise
        return True

    def summary(self) -> dict[str, float]:
        totals: dict[str, float] = {}
        for item in self._scan():
            expense = self._to_expense(item)
            totals[expense.category] = round(
                totals.get(expense.category, 0.0) + expense.amount, 2
            )
        return totals

    def _scan(self, **scan_kwargs: Any) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        exclusive_start_key = None
        while True:
            params = dict(scan_kwargs)
            if exclusive_start_key is not None:
                params["ExclusiveStartKey"] = exclusive_start_key
            response = self._table.scan(**params)
            items.extend(response.get("Items", []))
            exclusive_start_key = response.get("LastEvaluatedKey")
            if not exclusive_start_key:
                break
        return items

    @staticmethod
    def _to_expense(item: dict[str, Any]) -> Expense:
        return Expense(
            id=UUID(item["id"]),
            amount=float(item["amount"]),
            category=item["category"],
            description=item.get("description"),
            date=date.fromisoformat(item["date"]),
        )


def create_store() -> ExpenseStore:
    backend = config.STORE_BACKEND
    if backend == "dynamodb":
        return DynamoDbExpenseStore()
    if backend == "memory":
        return InMemoryExpenseStore()
    raise ValueError(f"Unknown STORE_BACKEND: {backend}")
