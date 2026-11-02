"""Configuração de logging em arquivo, com rotação."""
import logging
from logging.handlers import RotatingFileHandler

from src.app.config import get_logs_dir


def setup_logging() -> None:
    handler = RotatingFileHandler(
        get_logs_dir() / "app.log",
        maxBytes=1_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)