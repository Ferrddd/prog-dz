"""
wallet/gui/dashboard_tab.py
---------------------------
Вкладка «Обзор»: баланс, статистика месяца, последние транзакции.
"""

import tkinter as tk
from tkinter import ttk

from ..models import Transaction
from ..utils  import fmt
from .base_tab import BaseTab


class DashboardTab(BaseTab):
    """Главный экран с балансом и кратким обзором активности."""

    def _build(self) -> None:
        # ── Текущий баланс ─────────────────────────────────────────────
        bal_frame = ttk.LabelFrame(self.frame, text="Текущий баланс", padding=12)
        bal_frame.pack(fill="x", pady=(0, 10))

        self._balance_var = tk.StringVar(value="0,00 ₽")
        tk.Label(
            bal_frame,
            textvariable=self._balance_var,
            font=("Helvetica", 28, "bold"),
            fg="#0a7c4a",
        ).pack()

        # ── Статистика текущего месяца ─────────────────────────────────
        stats_frame = ttk.LabelFrame(
            self.frame, text="Статистика текущего месяца", padding=12
        )
        stats_frame.pack(fill="x", pady=(0, 10))
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)

        ttk.Label(stats_frame, text="Доходы:", font=("Helvetica", 11)).grid(
            row=0, column=0, sticky="w"
        )
        self._income_var = tk.StringVar(value="0,00 ₽")
        tk.Label(
            stats_frame,
            textvariable=self._income_var,
            font=("Helvetica", 14, "bold"),
            fg="#0a7c4a",
        ).grid(row=1, column=0, sticky="w")

        ttk.Label(stats_frame, text="Расходы:", font=("Helvetica", 11)).grid(
            row=0, column=1, sticky="w"
        )
        self._expense_var = tk.StringVar(value="0,00 ₽")
        tk.Label(
            stats_frame,
            textvariable=self._expense_var,
            font=("Helvetica", 14, "bold"),
            fg="#b03020",
        ).grid(row=1, column=1, sticky="w")

        # ── Последние 10 транзакций ─────────────────────────────────────
        rec_frame = ttk.LabelFrame(
            self.frame, text="Последние 10 транзакций", padding=8
        )
        rec_frame.pack(fill="both", expand=True)

        cols = ("date", "description", "category", "amount")
        self._tree = ttk.Treeview(rec_frame, columns=cols, show="headings", height=10)
        self._tree.heading("date",        text="Дата")
        self._tree.heading("description", text="Описание")
        self._tree.heading("category",    text="Категория")
        self._tree.heading("amount",      text="Сумма")
        self._tree.column("date",        width=90,  anchor="center")
        self._tree.column("description", width=220)
        self._tree.column("category",    width=120)
        self._tree.column("amount",      width=120, anchor="e")
        self._tree.tag_configure("income",  foreground="#0a7c4a")
        self._tree.tag_configure("expense", foreground="#b03020")

        sb = ttk.Scrollbar(rec_frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def refresh(self) -> None:
        balance = self.service.get_balance()
        self._balance_var.set(fmt(balance))

        stats = self.service.month_stats()
        self._income_var.set(fmt(stats["income"]))
        self._expense_var.set(fmt(stats["expense"]))

        self._tree.delete(*self._tree.get_children())
        for t in self.service.get_recent(10):
            sign = "+" if t.is_income() else "-"
            tag  = "income" if t.is_income() else "expense"
            self._tree.insert("", "end", values=(
                t.date,
                t.description,
                t.category or "—",
                f"{sign}{fmt(t.amount)}",
            ), tags=(tag,))
