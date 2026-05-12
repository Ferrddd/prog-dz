"""
wallet/gui/expense_tab.py
-------------------------
Вкладка «Трата»: форма добавления новой траты с проверкой баланса.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from ..service import WalletError, WalletService
from ..utils   import fmt, today_str
from .base_tab import BaseTab


class ExpenseTab(BaseTab):
    """Форма добавления расхода с выбором категории и проверкой лимита."""

    def _build(self) -> None:
        form = ttk.LabelFrame(self.frame, text="Новая трата", padding=12)
        form.pack(fill="x", pady=(0, 10))

        ttk.Label(form, text="Сумма (₽):").grid(
            row=0, column=0, sticky="w", padx=4, pady=5
        )
        self._amount = ttk.Entry(form, width=18)
        self._amount.grid(row=0, column=1, sticky="w", padx=4, pady=5)

        ttk.Label(form, text="Категория:").grid(
            row=1, column=0, sticky="w", padx=4, pady=5
        )
        self._cat_var = tk.StringVar()
        self._cat = ttk.Combobox(
            form,
            textvariable=self._cat_var,
            values=WalletService.CATEGORIES,
            state="readonly",
            width=22,
        )
        self._cat.grid(row=1, column=1, sticky="w", padx=4, pady=5)

        ttk.Label(form, text="Дата (ДД.ММ.ГГГГ):").grid(
            row=2, column=0, sticky="w", padx=4, pady=5
        )
        self._date = ttk.Entry(form, width=18)
        self._date.insert(0, today_str())
        self._date.grid(row=2, column=1, sticky="w", padx=4, pady=5)

        ttk.Label(form, text="Описание:").grid(
            row=3, column=0, sticky="w", padx=4, pady=5
        )
        self._desc = ttk.Entry(form, width=30)
        self._desc.grid(row=3, column=1, sticky="w", padx=4, pady=5)

        self._balance_lbl = ttk.Label(
            form, text="", foreground="#0a7c4a", font=("Helvetica", 10, "bold")
        )
        self._balance_lbl.grid(
            row=4, column=0, columnspan=2, sticky="w", padx=4, pady=(6, 2)
        )

        ttk.Button(form, text="✚  Добавить трату", command=self._on_add).grid(
            row=5, column=0, columnspan=2, pady=8, sticky="w", padx=4
        )

    # ── Обработчики ────────────────────────────────────────────────────

    def _on_add(self) -> None:
        try:
            t = self.service.add_expense(
                self._amount.get(),
                self._date.get(),
                self._desc.get(),
                self._cat_var.get(),
            )
            messagebox.showinfo("Готово", f"Трата {fmt(t.amount)} добавлена.")
            self._amount.delete(0, "end")
            self._desc.delete(0, "end")
            self._cat.set("")
            self.refresh()
        except WalletError as e:
            messagebox.showerror("Ошибка", str(e))

    def refresh(self) -> None:
        bal = self.service.get_balance()
        self._balance_lbl.config(text=f"Доступный баланс: {fmt(bal)}")
