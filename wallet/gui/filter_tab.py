"""
wallet/gui/filter_tab.py
------------------------
Вкладка «Фильтры»: фильтрация трат по диапазону дат и категории.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from ..models  import Transaction
from ..service import WalletError, WalletService
from ..utils   import fmt
from .base_tab import BaseTab


class FilterTab(BaseTab):
    """Поиск трат с фильтрацией по дате и/или категории."""

    def _build(self) -> None:
        # ── Панель фильтров ────────────────────────────────────────────
        form = ttk.LabelFrame(self.frame, text="Параметры фильтрации", padding=12)
        form.pack(fill="x", pady=(0, 10))

        ttk.Label(form, text="Дата с (ДД.ММ.ГГГГ):").grid(
            row=0, column=0, sticky="w", padx=4, pady=5
        )
        self._date_from = ttk.Entry(form, width=16)
        self._date_from.grid(row=0, column=1, sticky="w", padx=4, pady=5)

        ttk.Label(form, text="Дата по (ДД.ММ.ГГГГ):").grid(
            row=0, column=2, sticky="w", padx=4, pady=5
        )
        self._date_to = ttk.Entry(form, width=16)
        self._date_to.grid(row=0, column=3, sticky="w", padx=4, pady=5)

        ttk.Label(form, text="Категория:").grid(
            row=1, column=0, sticky="w", padx=4, pady=5
        )
        self._cat_var = tk.StringVar()
        self._cat = ttk.Combobox(
            form,
            textvariable=self._cat_var,
            values=[""] + WalletService.CATEGORIES,
            state="readonly",
            width=18,
        )
        self._cat.grid(row=1, column=1, sticky="w", padx=4, pady=5)

        btn_row = ttk.Frame(form)
        btn_row.grid(row=2, column=0, columnspan=4, sticky="w", padx=4, pady=8)
        ttk.Button(btn_row, text="🔍 Найти",    command=self._on_filter).pack(side="left", padx=(0, 6))
        ttk.Button(btn_row, text="✖ Сбросить", command=self._on_clear).pack(side="left")

        self._summary = ttk.Label(
            form, text="", foreground="#0a7c4a", font=("Helvetica", 10, "bold")
        )
        self._summary.grid(row=3, column=0, columnspan=4, sticky="w", padx=4)

        # ── Таблица результатов ────────────────────────────────────────
        frm = ttk.Frame(self.frame)
        frm.pack(fill="both", expand=True)

        cols = ("date", "description", "category", "amount")
        self._tree = ttk.Treeview(frm, columns=cols, show="headings", height=12)
        self._tree.heading("date",        text="Дата")
        self._tree.heading("description", text="Описание")
        self._tree.heading("category",    text="Категория")
        self._tree.heading("amount",      text="Сумма")
        self._tree.column("date",        width=90,  anchor="center")
        self._tree.column("description", width=240)
        self._tree.column("category",    width=120)
        self._tree.column("amount",      width=120, anchor="e")
        self._tree.tag_configure("expense", foreground="#b03020")

        sb = ttk.Scrollbar(frm, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    # ── Обработчики ────────────────────────────────────────────────────

    def _on_filter(self) -> None:
        try:
            results = self.service.filter_expenses(
                self._date_from.get(),
                self._date_to.get(),
                self._cat_var.get(),
            )
            total = sum(t.amount for t in results)
            self._summary.config(
                text=f"Найдено записей: {len(results)},  сумма: {fmt(total)}"
            )
            self._fill_table(results)
        except WalletError as e:
            messagebox.showerror("Ошибка", str(e))

    def _on_clear(self) -> None:
        self._date_from.delete(0, "end")
        self._date_to.delete(0, "end")
        self._cat.set("")
        self._summary.config(text="")
        self._fill_table(self.service.get_expenses())

    def _fill_table(self, items: list[Transaction]) -> None:
        self._tree.delete(*self._tree.get_children())
        for t in items:
            self._tree.insert("", "end", values=(
                t.date, t.description, t.category, f"-{fmt(t.amount)}"
            ), tags=("expense",))

    def refresh(self) -> None:
        self._fill_table(self.service.get_expenses())
        self._summary.config(text="")
