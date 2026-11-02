"""Configurações globais: nome, versão e pastas de dados do usuário."""
import os
from pathlib import Path

APP_NAME = "PizzariaSystem"
APP_VERSION = "0.1.0"


def get_data_dir() -> Path:
    """Pasta de dados do usuário (banco, logs, backups).

    Fica fora da pasta de instalação, para sobreviver a atualizações.
    """
    base = os.environ.get("LOCALAPPDATA") or str(Path.home())
    path = Path(base) / APP_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_logs_dir() -> Path:
    path = get_data_dir() / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path