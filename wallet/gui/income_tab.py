#Вкладка «Пополнение»

from tkinter import ttk, messagebox

from ..service import WalletError
from ..utils   import fmt, today_str
from .base_tab import BaseTab


class IncomeTab(BaseTab):
    """Позволяет внести деньги в кошелёк с проверкой разрешённого дня."""

    def _build(self) -> None:
        # ── Форма ввода ────────────────────────────────────────────────
        form = ttk.LabelFrame(self.frame, text="Внести деньги в кошелёк", padding=12)
        form.pack(fill="x", pady=(0, 10))

        ttk.Label(form, text="Сумма (₽):").grid(
            row=0, column=0, sticky="w", padx=4, pady=4
        )
        self._amount = ttk.Entry(form, width=18)
        self._amount.grid(row=0, column=1, sticky="w", padx=4, pady=4)

        ttk.Label(form, text="Дата (ДД.ММ.ГГГГ):").grid(
            row=1, column=0, sticky="w", padx=4, pady=4
        )
        self._date = ttk.Entry(form, width=18)
        self._date.insert(0, today_str())
        self._date.grid(row=1, column=1, sticky="w", padx=4, pady=4)

        ttk.Label(form, text="Описание:").grid(
            row=2, column=0, sticky="w", padx=4, pady=4
        )
        self._desc = ttk.Entry(form, width=30)
        self._desc.grid(row=2, column=1, sticky="w", padx=4, pady=4)


        self._day_info = ttk.Label(
            form, text="", foreground="#0a7c4a", font=("Helvetica", 9)
        )
        self._day_info.grid(row=4, column=0, columnspan=3, sticky="w", padx=4)

        ttk.Button(form, text="✚  Зачислить", command=self._on_add).grid(
            row=5, column=0, columnspan=2, pady=10, sticky="w", padx=4
        )

        # ── Настройка разрешённого дня ─────────────────────────
        day_frame = ttk.LabelFrame(
            self.frame,
            text="Настройка дня поступления",
            padding=12
        )
        day_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(
            day_frame,
            text="Разрешённый день (1–31):"
        ).grid(row=0, column=0, sticky="w", padx=4, pady=4)

        self._income_day_setting = ttk.Entry(day_frame, width=8)
        self._income_day_setting.grid(
            row=0, column=1, sticky="w", padx=4, pady=4
        )

        ttk.Button(
            day_frame,
            text="Сохранить",
            command=self._on_set_income_day
        ).grid(row=0, column=2, padx=6)

        self._day_info = ttk.Label(
            day_frame,
            text="",
            foreground="#0a7c4a",
            font=("Helvetica", 9)
        )

        self._day_info.grid(
            row=1,
            column=0,
            columnspan=3,
            sticky="w",
            padx=4
        )

        # ── История поступлений ────────────────────────────────────────
        lst_frame = ttk.LabelFrame(
            self.frame, text="История поступлений", padding=8
        )
        lst_frame.pack(fill="both", expand=True)

        cols = ("id", "date", "description", "amount")
        self._tree = ttk.Treeview(lst_frame, columns=cols, show="headings", height=9)
        self._tree.heading("id",          text="#")
        self._tree.heading("date",        text="Дата")
        self._tree.heading("description", text="Описание")
        self._tree.heading("amount",      text="Сумма")
        self._tree.column("id",          width=40,  anchor="center")
        self._tree.column("date",        width=90,  anchor="center")
        self._tree.column("description", width=260)
        self._tree.column("amount",      width=120, anchor="e")
        self._tree.tag_configure("income", foreground="#0a7c4a")

        sb = ttk.Scrollbar(lst_frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    # ── Обработчики ────────────────────────────────────────────────────

    def _on_add(self) -> None:
        try:
            t = self.service.add_income(
                self._amount.get(),
                self._date.get(),
                self._desc.get(),
            )
            messagebox.showinfo("Готово", f"Зачислено {fmt(t.amount)}")
            self._amount.delete(0, "end")
            self._desc.delete(0, "end")
            self.refresh()
        except WalletError as e:
            messagebox.showerror("Ошибка", str(e))

    def refresh(self) -> None:
        day = self.service.get_income_day()

        if day:
            self._day_info.config(
                text=f"Текущий разрешённый день поступления: {day}"
            )
            self._income_day_setting.delete(0, "end")
            self._income_day_setting.insert(0, str(day))
        else:
            self._day_info.config(text="Ограничение по дню не задано")

        self._tree.delete(*self._tree.get_children())
        for t in self.service.get_incomes():
            self._tree.insert("", "end", values=(
                t.id, t.date, t.description, f"+{fmt(t.amount)}"
            ), tags=("income",))

    def _on_set_income_day(self) -> None:
        try:
            self.service.set_income_day(
                self._income_day_setting.get()
            )

            messagebox.showinfo("Готово", "День сохранён")
            self.refresh()

        except WalletError as e:
            messagebox.showerror("Ошибка", str(e))