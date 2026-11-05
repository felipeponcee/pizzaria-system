import pytest
from sqlalchemy.orm import Session

from src.core.database import make_engine, run_migrations


@pytest.fixture
def engine(tmp_path):
    db_path = tmp_path / "test.db"
    run_migrations(db_path)
    engine = make_engine(db_path)
    yield engine
    engine.dispose()


@pytest.fixture
def session(engine):
    with Session(engine) as session:
        yield session
