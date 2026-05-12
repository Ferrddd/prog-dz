"""
wallet/database.py
------------------
Управление базой данных SQLite: создание таблиц, CRUD-операции.
Не содержит бизнес-логики — только чистый доступ к данным.
"""

import sqlite3
import datetime
import os

from .models import Transaction


class DatabaseManager:
    """Управляет подключением к SQLite и выполняет CRUD-операции."""

    DB_FILE = "wallet.db"

    def __init__(self, db_path: str | None = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "..", self.DB_FILE
            )
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._create_tables()

    # ──────────────────────────────────────────────
    # Инициализация схемы
    # ──────────────────────────────────────────────

    def _create_tables(self) -> None:
        sql_transactions = """
        CREATE TABLE IF NOT EXISTS transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            type        TEXT    NOT NULL CHECK(type IN ('income', 'expense')),
            amount      REAL    NOT NULL CHECK(amount > 0),
            date        TEXT    NOT NULL,
            description TEXT    NOT NULL,
            category    TEXT    DEFAULT ''
        );"""
        sql_settings = """
        CREATE TABLE IF NOT EXISTS settings (
            key   TEXT PRIMARY KEY,
            value TEXT
        );"""
        with self._conn:
            self._conn.execute(sql_transactions)
            self._conn.execute(sql_settings)

    # ──────────────────────────────────────────────
    # Настройки (ключ-значение)
    # ──────────────────────────────────────────────

    def get_setting(self, key: str) -> str | None:
        row = self._conn.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        ).fetchone()
        return row["value"] if row else None

    def set_setting(self, key: str, value: str) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT OR REPLACE INTO settings(key, value) VALUES (?, ?)",
                (key, value),
            )

    # ──────────────────────────────────────────────
    # Транзакции — запись
    # ──────────────────────────────────────────────

    def insert_transaction(
        self,
        type_: str,
        amount: float,
        date: str,
        description: str,
        category: str = "",
    ) -> Transaction:
        with self._conn:
            cur = self._conn.execute(
                "INSERT INTO transactions(type, amount, date, description, category)"
                " VALUES (?, ?, ?, ?, ?)",
                (type_, amount, date, description, category),
            )
        return Transaction(cur.lastrowid, type_, amount, date, description, category)

    def delete_transaction(self, id_: int) -> Transaction | None:
        row = self._conn.execute(
            "SELECT * FROM transactions WHERE id = ?", (id_,)
        ).fetchone()
        if not row:
            return None
        with self._conn:
            self._conn.execute("DELETE FROM transactions WHERE id = ?", (id_,))
        return Transaction(
            row["id"], row["type"], row["amount"],
            row["date"], row["description"], row["category"],
        )

    # ──────────────────────────────────────────────
    # Транзакции — чтение
    # ──────────────────────────────────────────────

    def get_balance(self) -> float:
        row = self._conn.execute(
            "SELECT COALESCE("
            "  SUM(CASE WHEN type = 'income' THEN amount ELSE -amount END), 0"
            ") AS bal FROM transactions"
        ).fetchone()
        return row["bal"]

    def get_all(self, limit: int = 0) -> list[Transaction]:
        sql = "SELECT * FROM transactions ORDER BY date DESC, id DESC"
        if limit:
            sql += f" LIMIT {limit}"
        return self._rows_to_transactions(self._conn.execute(sql))

    def get_by_type(self, type_: str) -> list[Transaction]:
        rows = self._conn.execute(
            "SELECT * FROM transactions"
            " WHERE type = ? ORDER BY date DESC, id DESC",
            (type_,),
        ).fetchall()
        return self._rows_to_transactions(rows)

    def filter_expenses(
        self,
        date_from: str = "",
        date_to: str = "",
        category: str = "",
    ) -> list[Transaction]:
        sql = "SELECT * FROM transactions WHERE type = 'expense'"
        params: list = []
        if date_from:
            sql += " AND date >= ?"
            params.append(date_from)
        if date_to:
            sql += " AND date <= ?"
            params.append(date_to)
        if category:
            sql += " AND category = ?"
            params.append(category)
        sql += " ORDER BY date DESC, id DESC"
        return self._rows_to_transactions(self._conn.execute(sql, params))

    def month_stats(self) -> dict:
        ym = datetime.date.today().strftime("%Y-%m")
        row = self._conn.execute(
            "SELECT"
            "  COALESCE(SUM(CASE WHEN type='income'  THEN amount ELSE 0 END), 0) AS income,"
            "  COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0) AS expense"
            " FROM transactions WHERE date LIKE ?",
            (f"{ym}%",),
        ).fetchone()
        return {"income": row["income"], "expense": row["expense"]}

    # ──────────────────────────────────────────────
    # Вспомогательные
    # ──────────────────────────────────────────────

    @staticmethod
    def _rows_to_transactions(rows) -> list[Transaction]:
        return [
            Transaction(r["id"], r["type"], r["amount"],
                        r["date"], r["description"], r["category"])
            for r in rows
        ]

    def close(self) -> None:
        self._conn.close()
