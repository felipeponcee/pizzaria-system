"""Engine, sessões e migrações do banco SQLite."""
import logging
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.app.config import get_data_dir

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def get_db_path() -> Path:
    return get_data_dir() / "pizzaria.db"


def make_engine(db_path: Path) -> Engine:
    """Cria o engine com foreign keys ativas e modo WAL (mais seguro contra falhas)."""
    engine = create_engine(f"sqlite:///{db_path}")

    @event.listens_for(engine, "connect")
    def _set_pragmas(dbapi_connection, _record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

    return engine


def run_migrations(db_path: Path) -> None:
    """Aplica as migrações do Alembic até a versão mais recente."""
    config = Config()
    config.set_main_option("script_location", str(PROJECT_ROOT / "migrations"))
    url = f"sqlite:///{db_path}".replace("%", "%%")
    config.set_main_option("sqlalchemy.url", url)
    command.upgrade(config, "head")


def init_db(db_path: Path | None = None) -> None:
    """Cria/atualiza o banco e prepara as sessões. Chamar uma vez ao iniciar o app."""
    global _engine, _session_factory
    path = db_path or get_db_path()
    logger.info("Inicializando banco de dados em %s", path)
    run_migrations(path)
    _engine = make_engine(path)
    _session_factory = sessionmaker(_engine, expire_on_commit=False)


@contextmanager
def session_scope() -> Iterator[Session]:
    """Sessão com commit automático e rollback em caso de erro (uma transação)."""
    if _session_factory is None:
        raise RuntimeError("Banco não inicializado. Chame init_db() antes.")
    session = _session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

