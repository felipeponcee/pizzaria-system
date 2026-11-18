"""Serviço base para os cadastros do cardápio."""
import logging
from typing import Any, Generic, TypeVar

from sqlalchemy.orm import Session

from src.core.exceptions import BusinessRuleError, NotFoundError
from src.repositories.base import Repository
from src.schemas.base import Schema, validate_or_raise

T = TypeVar("T")
logger = logging.getLogger(__name__)


class CatalogService(Generic[T]):
    repository_class: type[Repository[T]]
    schema: type[Schema]

    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = self.repository_class(session)

    def list_all(self, include_inactive: bool = False) -> list[T]:
        return self.repo.list_all(include_inactive)

    def get(self, entity_id: int) -> T:
        entity = self.repo.get(entity_id)
        if entity is None:
            raise NotFoundError("Registro não encontrado.")
        return entity

    def create(self, **data: Any) -> T:
        dto = validate_or_raise(self.schema, **data)
        self._check(dto)
        entity = self.repo.add(self._build(dto))
        logger.info("%s criado: id=%s", self.repo.model.__name__, entity.id)
        return entity

    def update(self, entity_id: int, **data: Any) -> T:
        dto = validate_or_raise(self.schema, **data)
        entity = self.get(entity_id)
        self._check(dto, ignore_id=entity_id)
        self._apply(entity, dto)
        self.session.flush()
        logger.info("%s alterado: id=%s", self.repo.model.__name__, entity_id)
        return entity

    def set_active(self, entity_id: int, active: bool) -> T:
        """Ativa ou desativa. Itens são desativados, nunca apagados."""
        entity = self.get(entity_id)
        entity.active = active
        self.session.flush()
        return entity

    def delete(self, entity_id: int) -> None:
        """Exclui definitivamente. Itens já usados em pedidos só podem ser desativados."""
        entity = self.get(entity_id)
        if self._is_used(entity_id):
            raise BusinessRuleError(
                f"'{entity.name}' já foi usado em pedidos e não pode ser excluído. "
                "Desative-o para que deixe de aparecer em novos pedidos."
            )
        self.session.delete(entity)
        self.session.flush()
        logger.info("%s excluído: id=%s", self.repo.model.__name__, entity_id)

    # Ganchos que os serviços específicos podem sobrescrever
    def _is_used(self, entity_id: int) -> bool:
        """True se o item já aparece em algum pedido (então não pode ser excluído)."""
        return False

    def _exists(self, stmt) -> bool:
        return self.session.scalars(stmt.limit(1)).first() is not None

    def _check(self, dto: Schema, ignore_id: int | None = None) -> None:
        existing = self.repo.find_by_name(dto.name, ignore_id)
        if existing is not None:
            hint = (
                "Selecione o cadastro na lista e use Editar."
                if getattr(existing, "active", True)
                else "Esse cadastro está inativo: ligue 'Mostrar inativos' e use Ativar."
            )
            raise BusinessRuleError(f"Já existe '{existing.name}' cadastrado. {hint}")

    def _build(self, dto: Schema) -> T:
        return self.repo.model(**dto.model_dump())

    def _apply(self, entity: T, dto: Schema) -> None:
        for field, value in dto.model_dump().items():
            setattr(entity, field, value)
