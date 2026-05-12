"""
main.py — точка входа приложения.
Запуск: python main.py
"""

from wallet import App


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()