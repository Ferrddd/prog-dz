"""
wallet/gui/history_tab.py
-------------------------
Вкладка «История»: список трат с возможностью удаления (возврат товара).
"""

from tkinter import ttk, messagebox

from ..service import WalletError
from ..utils   import fmt
from .base_tab import BaseTab


class HistoryTab(BaseTab):
    """Показывает все расходы; позволяет удалить трату (вернуть деньги)."""

    def _build(self) -> None:
        # ── Подсказка + кнопка обновления ─────────────────────────────
        top = ttk.Frame(self.frame)
        top.pack(fill="x", pady=(0, 8))
        ttk.Label(
            top,
            text="Выделите строку и нажмите «Удалить / Возврат».",
            foreground="gray",
        ).pack(side="left")
        ttk.Button(top, text="🔄 Обновить", command=self.refresh).pack(side="right")

        # ── Таблица трат ───────────────────────────────────────────────
        frm = ttk.Frame(self.frame)
        frm.pack(fill="both", expand=True)

        cols = ("id", "date", "description", "category", "amount")
        self._tree = ttk.Treeview(frm, columns=cols, show="headings", height=14)
        self._tree.heading("id",          text="#")
        self._tree.heading("date",        text="Дата")
        self._tree.heading("description", text="Описание")
        self._tree.heading("category",    text="Категория")
        self._tree.heading("amount",      text="Сумма")
        self._tree.column("id",          width=40,  anchor="center")
        self._tree.column("date",        width=90,  anchor="center")
        self._tree.column("description", width=220)
        self._tree.column("category",    width=110)
        self._tree.column("amount",      width=110, anchor="e")
        self._tree.tag_configure("expense", foreground="#b03020")

        sb = ttk.Scrollbar(frm, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # ── Кнопка удаления + статус ───────────────────────────────────
        btn_row = ttk.Frame(self.frame)
        btn_row.pack(fill="x", pady=8)
        ttk.Button(
            btn_row,
            text="🗑  Удалить / Возврат товара",
            command=self._on_delete,
        ).pack(side="left")
        self._status = ttk.Label(btn_row, text="", foreground="gray")
        self._status.pack(side="left", padx=12)

    # ── Обработчики ────────────────────────────────────────────────────

    def _on_delete(self) -> None:
        sel = self._tree.selection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите трату для удаления.")
            return

        item = self._tree.item(sel[0])
        id_  = int(item["values"][0])
        desc = item["values"][2]

        confirmed = messagebox.askyesno(
            "Подтверждение",
            f"Удалить трату «{desc}»?\n(средства вернутся на кошелёк)",
        )
        if not confirmed:
            return

        try:
            t = self.service.delete_expense(id_)
            self._status.config(
                text=f"Возврат: {fmt(t.amount)} — «{t.description}»",
                foreground="#0a7c4a",
            )
            self.refresh()
        except WalletError as e:
            messagebox.showerror("Ошибка", str(e))

    def refresh(self) -> None:
        self._tree.delete(*self._tree.get_children())
        for t in self.service.get_expenses():
            self._tree.insert("", "end", values=(
                t.id, t.date, t.description, t.category, f"-{fmt(t.amount)}"
            ), tags=("expense",))
