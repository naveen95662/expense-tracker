from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query, status

from app.logging_middleware import JsonRequestLoggingMiddleware
from app.models import Expense, ExpenseCreate, ExpenseSummary
from app.store import ExpenseStore, InMemoryExpenseStore

app = FastAPI(title="Expense Tracker API")
app.add_middleware(JsonRequestLoggingMiddleware)

_store = InMemoryExpenseStore()


def get_store() -> ExpenseStore:
    return _store


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/expenses", status_code=status.HTTP_201_CREATED, response_model=Expense)
def create_expense(
    payload: ExpenseCreate,
    store: ExpenseStore = Depends(get_store),
) -> Expense:
    return store.create(payload)


@app.get("/expenses", response_model=list[Expense])
def list_expenses(
    category: str | None = Query(default=None),
    store: ExpenseStore = Depends(get_store),
) -> list[Expense]:
    return store.list(category)


@app.get("/expenses/summary", response_model=ExpenseSummary)
def expense_summary(store: ExpenseStore = Depends(get_store)) -> ExpenseSummary:
    return ExpenseSummary(totals=store.summary())


@app.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: UUID,
    store: ExpenseStore = Depends(get_store),
) -> None:
    deleted = store.delete(expense_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
