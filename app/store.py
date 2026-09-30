from datetime import date
from typing import Protocol
from uuid import UUID, uuid4

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
