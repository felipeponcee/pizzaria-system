"""Ponto de entrada da aplicação."""
import logging

import customtkinter as ctk

from src.core.logging_config import setup_logging
from src.ui.windows.main_window import MainWindow

logger = logging.getLogger(__name__)


def main() -> None:
    setup_logging()
    logger.info("Aplicação iniciada")
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    app = MainWindow()
    app.mainloop()
    logger.info("Aplicação encerrada")


if __name__ == "__main__":
    main()