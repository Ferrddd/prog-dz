#Главное окно приложения

import tkinter as tk
from tkinter import ttk

from ..database import DatabaseManager
from ..service  import WalletService
from ..utils    import fmt
from .base_tab      import BaseTab
from .dashboard_tab import DashboardTab
from .income_tab    import IncomeTab
from .expense_tab   import ExpenseTab
from .history_tab   import HistoryTab
from .filter_tab    import FilterTab


#Корневое окно приложения «Учёт денежных средств»
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Учёт денежных средств")
        self.geometry("760x580")
        self.resizable(True, True)
        self.minsize(900, 800)

        self._db      = DatabaseManager()
        self._service = WalletService(self._db)

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ──────────────────────────────────────────────
    # Построение интерфейса
    # ──────────────────────────────────────────────

    def _build_ui(self) -> None:
        ttk.Style(self).theme_use("clam")

        # ── Шапка с балансом ──────────────────────────────────────────
        header = tk.Frame(self, bg="#1a4a7a", height=46)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Мой Кошелёк",
            bg="#1a4a7a", fg="white",
            font=("Helvetica", 14, "bold"),
        ).pack(side="left", padx=16, pady=8)

        self._hdr_balance = tk.Label(
            header,
            text="",
            bg="#1a4a7a", fg="#7ee8b8",
            font=("Helvetica", 13, "bold"),
        )
        self._hdr_balance.pack(side="right", padx=16)

        # ── Notebook с вкладками ───────────────────────────────────────
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self._tabs: list[BaseTab] = [
            DashboardTab(notebook, "Обзор",      self._service),
            IncomeTab   (notebook, "Пополнение", self._service),
            ExpenseTab  (notebook, "Трата",      self._service),
            HistoryTab  (notebook, "История",    self._service),
            FilterTab   (notebook, "Фильтры",    self._service),
        ]

        notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)
        self._tabs[0].refresh()
        self._update_header()

    # ──────────────────────────────────────────────
    # Обработчики событий
    # ──────────────────────────────────────────────

    def _on_tab_change(self, event: tk.Event) -> None:
        idx = event.widget.index("current")
        self._tabs[idx].refresh()
        self._update_header()

    def _update_header(self) -> None:
        bal = self._service.get_balance()
        self._hdr_balance.config(text=f"Баланс: {fmt(bal)}")

    def _on_close(self) -> None:
        self._db.close()
        self.destroy()
