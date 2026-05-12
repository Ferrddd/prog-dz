"""
wallet/models.py
----------------
Модели данных приложения.
"""


class Transaction:
    """Модель одной финансовой транзакции (доход или расход)."""

    TYPE_INCOME  = "income"
    TYPE_EXPENSE = "expense"

    def __init__(
        self,
        id_: int,
        type_: str,
        amount: float,
        date: str,
        description: str,
        category: str = "",
    ):
        self.id          = id_
        self.type        = type_
        self.amount      = float(amount)
        self.date        = date
        self.description = description
        self.category    = category

    def is_income(self) -> bool:
        return self.type == self.TYPE_INCOME

    def is_expense(self) -> bool:
        return self.type == self.TYPE_EXPENSE

    def __repr__(self) -> str:
        sign = "+" if self.is_income() else "-"
        return (
            f"<Transaction #{self.id} {sign}{self.amount:.2f}"
            f" [{self.date}] '{self.description}'>"
        )
