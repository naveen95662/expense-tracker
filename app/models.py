import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExpenseCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Must be greater than zero")
    category: str = Field(..., min_length=1)
    description: str | None = None
    date: datetime.date | None = None

    @field_validator("category")
    @classmethod
    def category_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("category must not be empty")
        return stripped

    @field_validator("description")
    @classmethod
    def strip_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class Expense(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    amount: float
    category: str
    description: str | None = None
    date: datetime.date


class ExpenseSummary(BaseModel):
    totals: dict[str, float]
