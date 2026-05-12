"""
wallet/gui/base_tab.py
----------------------
Абстрактный базовый класс для всех вкладок GUI.
"""

from abc import ABC, abstractmethod
from tkinter import ttk

from ..service import WalletService


class BaseTab(ABC):
    """
    Каждая вкладка приложения наследует этот класс.
    Содержит ссылку на сервис и фрейм вкладки в Notebook.
    """

    def __init__(self, notebook: ttk.Notebook, title: str, service: WalletService):
        self.service = service
        self.frame   = ttk.Frame(notebook, padding=16)
        notebook.add(self.frame, text=f"  {title}  ")
        self._build()

    @abstractmethod
    def _build(self) -> None:
        """Строит все виджеты вкладки. Вызывается один раз при создании."""

    def refresh(self) -> None:
        """Обновляет данные вкладки. Вызывается при переключении на неё."""
