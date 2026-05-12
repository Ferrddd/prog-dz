"""
wallet/utils.py
---------------
Вспомогательные утилиты, не привязанные к слою данных или GUI.
"""

import datetime


def fmt(n: float) -> str:
    """Форматирует число как денежную сумму: 1 234,56 ₽"""
    return f"{n:,.2f} ₽".replace(",", "\u00a0")


def today_str() -> str:
    """Возвращает сегодняшнюю дату в формате ДД.ММ.ГГГГ."""
    return datetime.date.today().strftime("%d.%m.%Y")
