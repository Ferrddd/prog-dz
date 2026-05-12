"""
wallet/service.py
-----------------
Бизнес-логика приложения: валидация, правила операций.
Не знает ничего о GUI — только работает с DatabaseManager.
"""

import datetime

from .models import Transaction
from .database import DatabaseManager


class WalletError(Exception):
    """Бизнес-ошибка приложения."""


class WalletService:
    """
    Фасад бизнес-логики кошелька.
    Все публичные методы либо возвращают результат,
    либо выбрасывают WalletError при нарушении правил.
    """

    CATEGORIES: list[str] = [
        "Продукты", "Транспорт", "Здоровье", "Развлечения",
        "Одежда", "Коммунальные", "Рестораны", "Образование", "Прочее",
    ]

    def __init__(self, db: DatabaseManager):
        self._db = db

    # ──────────────────────────────────────────────
    # Вспомогательные методы парсинга/валидации
    # ──────────────────────────────────────────────

    def _parse_amount(self, value: str) -> float:
        """Парсит строку суммы, выбрасывает WalletError при ошибке."""
        try:
            amount = float(value.replace(",", ".").strip())
            if amount <= 0:
                raise ValueError
            return amount
        except ValueError:
            raise WalletError("Сумма должна быть положительным числом.")

    def _parse_date(self, value: str) -> str:
        """
        Принимает дату в форматах ДД.ММ.ГГГГ / ГГГГ-ММ-ДД / ДД/ММ/ГГГГ.
        Возвращает ISO-строку ГГГГ-ММ-ДД.
        """
        value = value.strip()
        for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
            try:
                return datetime.datetime.strptime(value, fmt).date().isoformat()
            except ValueError:
                continue
        raise WalletError(
            "Неверный формат даты. Используйте ДД.ММ.ГГГГ или ГГГГ-ММ-ДД."
        )

    # ──────────────────────────────────────────────
    # Настройка дня поступления
    # ──────────────────────────────────────────────

    def get_income_day(self) -> int | None:
        """Возвращает разрешённый день поступления или None, если не задан."""
        val = self._db.get_setting("income_day")
        return int(val) if val else None

    def set_income_day(self, day_str: str) -> None:
        """Сохраняет разрешённый день поступления (1–31)."""
        try:
            day = int(day_str.strip())
            if not (1 <= day <= 31):
                raise ValueError
        except ValueError:
            raise WalletError("День поступления должен быть числом от 1 до 31.")
        self._db.set_setting("income_day", str(day))

    # ──────────────────────────────────────────────
    # Операции с кошельком
    # ──────────────────────────────────────────────

    def add_income(
        self,
        amount_str: str,
        date_str: str,
        description: str,
        income_day_str: str = "",
    ) -> Transaction:
        """
        Зачисляет средства на кошелёк.
        Если income_day_str задан — обновляет ограничение по дню и проверяет его.
        """
        if not description.strip():
            raise WalletError("Укажите описание поступления.")

        amount = self._parse_amount(amount_str)
        date   = self._parse_date(date_str)

        if income_day_str.strip():
            self.set_income_day(income_day_str)

        income_day = self.get_income_day()
        if income_day is not None:
            actual_day = datetime.date.fromisoformat(date).day
            if actual_day != income_day:
                raise WalletError(
                    f"Поступление разрешено только в {income_day}-й день месяца.\n"
                    f"Выбранная дата: {actual_day}-й день."
                )

        return self._db.insert_transaction(
            Transaction.TYPE_INCOME, amount, date, description.strip()
        )

    def add_expense(
        self,
        amount_str: str,
        date_str: str,
        description: str,
        category: str,
    ) -> Transaction:
        """
        Добавляет трату.
        Проверяет, что на балансе достаточно средств.
        """
        if not description.strip():
            raise WalletError("Укажите описание траты.")
        if not category:
            raise WalletError("Выберите категорию.")

        amount  = self._parse_amount(amount_str)
        date    = self._parse_date(date_str)
        balance = self._db.get_balance()

        if amount > balance:
            from .utils import fmt  # локальный импорт для форматирования
            raise WalletError(
                f"Недостаточно средств.\n"
                f"Баланс: {fmt(balance)},  трата: {fmt(amount)}."
            )

        return self._db.insert_transaction(
            Transaction.TYPE_EXPENSE, amount, date, description.strip(), category
        )

    def delete_expense(self, id_: int) -> Transaction:
        """Удаляет трату (возврат товара), возвращает удалённую транзакцию."""
        t = self._db.delete_transaction(id_)
        if t is None:
            raise WalletError("Транзакция не найдена.")
        return t

    # ──────────────────────────────────────────────
    # Запросы
    # ──────────────────────────────────────────────

    def get_balance(self) -> float:
        return self._db.get_balance()

    def get_recent(self, n: int = 10) -> list[Transaction]:
        return self._db.get_all(limit=n)

    def get_incomes(self) -> list[Transaction]:
        return self._db.get_by_type(Transaction.TYPE_INCOME)

    def get_expenses(self) -> list[Transaction]:
        return self._db.get_by_type(Transaction.TYPE_EXPENSE)

    def filter_expenses(
        self,
        date_from: str = "",
        date_to: str   = "",
        category: str  = "",
    ) -> list[Transaction]:
        """Фильтрация трат по дате и/или категории."""
        df = self._parse_date(date_from) if date_from.strip() else ""
        dt = self._parse_date(date_to)   if date_to.strip()   else ""
        if df and dt and df > dt:
            raise WalletError("Дата «с» не может быть позже даты «по».")
        return self._db.filter_expenses(df, dt, category)

    def month_stats(self) -> dict:
        return self._db.month_stats()
