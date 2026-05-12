#Вспомогательные утилиты, не привязанные к слою данных или GUI.

import datetime


# Форматирует число как денежную сумму: 1 234,56 ₽
def fmt(n: float) -> str:
    return f"{n:,.2f} ₽".replace(",", "\u00a0")


# Возвращает сегодняшнюю дату в формате ДД.ММ.ГГГГ
def today_str() -> str:
    return datetime.date.today().strftime("%d.%m.%Y")
