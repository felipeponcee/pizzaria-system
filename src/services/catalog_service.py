"""Serviços do cardápio: tamanhos, sabores, produtos e adicionais."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.exceptions import BusinessRuleError
from src.models import (
    Additional,
    Category,
    Flavor,
    FlavorPrice,
    OrderItem,
    OrderItemAdditional,
    OrderItemFlavor,
    Product,
    Size,
)
from src.repositories.catalog_repository import (
    AdditionalRepository,
    CategoryRepository,
    FlavorRepository,
    ProductRepository,
    SizeRepository,
)
from src.schemas.base import Schema
from src.schemas.catalog import AdditionalIn, FlavorIn, ProductIn, SizeIn
from src.services.base_service import CatalogService

DEFAULT_CATEGORIES = ("Bebidas", "Sobremesas", "Combos")


class SizeService(CatalogService[Size]):
    repository_class = SizeRepository
    schema = SizeIn

    def _is_used(self, entity_id: int) -> bool:
        return self._exists(select(OrderItem.id).where(OrderItem.size_id == entity_id))


class AdditionalService(CatalogService[Additional]):
    repository_class = AdditionalRepository
    schema = AdditionalIn

    def _is_used(self, entity_id: int) -> bool:
        return self._exists(
            select(OrderItemAdditional.id).where(OrderItemAdditional.additional_id == entity_id)
        )


class ProductService(CatalogService[Product]):
    repository_class = ProductRepository
    schema = ProductIn

    def _is_used(self, entity_id: int) -> bool:
        return self._exists(select(OrderItem.id).where(OrderItem.product_id == entity_id))

    def list_categories(self) -> list[Category]:
        return CategoryRepository(self.session).list_all()

    def _check(self, dto: Schema, ignore_id: int | None = None) -> None:
        super()._check(dto, ignore_id)
        if self.session.get(Category, dto.category_id) is None:
            raise BusinessRuleError("Categoria não encontrada.")


class FlavorService(CatalogService[Flavor]):
    """Sabor com um preço por tamanho (ex.: Calabresa: Grande 50,00 / Broto 30,00)."""

    repository_class = FlavorRepository
    schema = FlavorIn

    def _is_used(self, entity_id: int) -> bool:
        return self._exists(
            select(OrderItemFlavor.id).where(OrderItemFlavor.flavor_id == entity_id)
        )

    def _check(self, dto: Schema, ignore_id: int | None = None) -> None:
        super()._check(dto, ignore_id)
        wanted = set(dto.prices)
        found = set(self.session.scalars(select(Size.id).where(Size.id.in_(wanted))))
        if wanted - found:
            raise BusinessRuleError("Um dos tamanhos informados não existe.")

    def _build(self, dto: Schema) -> Flavor:
        return Flavor(
            name=dto.name,
            description=dto.description,
            allows_half=dto.allows_half,
            prices=[FlavorPrice(size_id=s, price_cents=p) for s, p in dto.prices.items()],
        )

    def _apply(self, entity: Flavor, dto: Schema) -> None:
        entity.name = dto.name
        entity.description = dto.description
        entity.allows_half = dto.allows_half
        current = {price.size_id: price for price in entity.prices}
        for size_id, cents in dto.prices.items():
            if size_id in current:
                current[size_id].price_cents = cents
            else:
                entity.prices.append(FlavorPrice(size_id=size_id, price_cents=cents))
        for size_id, price in current.items():
            if size_id not in dto.prices:
                entity.prices.remove(price)


def ensure_default_categories(session: Session) -> None:
    """Cria as categorias iniciais se ainda não existir nenhuma."""
    repo = CategoryRepository(session)
    if repo.list_all():
        return
    for name in DEFAULT_CATEGORIES:
        repo.add(Category(name=name))


DEFAULT_SIZES = (  # (nome, fatias, máximo de sabores, ordem)
    ("Broto", 4, 2, 1),
    ("Grande", 8, 2, 2),
)


def ensure_default_sizes(session: Session) -> None:
    """Garante que os tamanhos Broto e Grande existam (cria só os que faltarem)."""
    repo = SizeRepository(session)
    existing = {size.name.casefold() for size in repo.list_all(include_inactive=True)}
    for name, slices, max_flavors, sort_order in DEFAULT_SIZES:
        if name.casefold() not in existing:
            repo.add(
                Size(name=name, slices=slices, max_flavors=max_flavors, sort_order=sort_order)
            )
