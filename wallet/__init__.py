"""
wallet — пакет приложения «Учёт денежных средств».

Структура:
    models.py    — модели данных (Transaction)
    database.py  — работа с SQLite (DatabaseManager)
    service.py   — бизнес-логика (WalletService, WalletError)
    utils.py     — вспомогательные функции (fmt, today_str)
    gui/
        base_tab.py     — абстрактный базовый класс вкладки
        dashboard_tab.py — вкладка «Обзор»
        income_tab.py   — вкладка «Пополнение»
        expense_tab.py  — вкладка «Трата»
        history_tab.py  — вкладка «История»
        filter_tab.py   — вкладка «Фильтры»
        app.py          — главное окно App
"""

from .models   import Transaction
from .database import DatabaseManager
from .service  import WalletService, WalletError
from .utils    import fmt, today_str
from .gui      import App

__all__ = [
    "Transaction",
    "DatabaseManager",
    "WalletService",
    "WalletError",
    "fmt",
    "today_str",
    "App",
]