"""Repositório genérico: leitura e gravação comuns a todos os cadastros."""
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

T = TypeVar("T")


class Repository(Generic[T]):
    model: type[T]

    def __init__(self, session: Session) -> None:
        self.session = session

    def order_by(self) -> tuple:
        return (self.model.name,)

    def get(self, entity_id: int) -> T | None:
        return self.session.get(self.model, entity_id)

    def add(self, entity: T) -> T:
        self.session.add(entity)
        self.session.flush()
        return entity

    def list_all(self, include_inactive: bool = False) -> list[T]:
        stmt = select(self.model).order_by(*self.order_by())
        if not include_inactive and hasattr(self.model, "active"):
            stmt = stmt.where(self.model.active.is_(True))
        return list(self.session.scalars(stmt))

    def find_by_name(self, name: str, ignore_id: int | None = None) -> T | None:
        """Busca por nome ignorando maiúsculas/minúsculas e acentos de caixa."""
        wanted = name.casefold()
        for entity in self.list_all(include_inactive=True):
            if entity.id != ignore_id and entity.name.casefold() == wanted:
                return entity
        return None
