"""Ponto de entrada da aplicação."""
import logging
from tkinter import messagebox

import customtkinter as ctk

from src.core.database import init_db
from src.core.logging_config import setup_logging
from src.ui.windows.main_window import MainWindow

logger = logging.getLogger(__name__)


def main() -> None:
    setup_logging()
    logger.info("Aplicação iniciada")
    try:
        init_db()
    except Exception:
        logger.exception("Falha ao inicializar o banco de dados")
        messagebox.showerror(
            "Erro",
            "Não foi possível abrir o banco de dados.\n"
            "Consulte o arquivo de log para mais detalhes.",
        )
        raise SystemExit(1)
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    app = MainWindow()
    app.mainloop()
    logger.info("Aplicação encerrada")


if __name__ == "__main__":
    main()
