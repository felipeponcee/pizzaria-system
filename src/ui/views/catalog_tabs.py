"""Abas concretas do cadastro do cardápio."""
from typing import Any

from sqlalchemy.orm import Session

from src.core.money import format_brl
from src.services.catalog_service import (
    AdditionalService,
    FlavorService,
    ProductService,
    SizeService,
)
from src.ui.components.data_table import TableRow
from src.ui.components.form_fields import Field
from src.ui.views.catalog_tab import CatalogTab, status_text

ADDITIONAL_KIND_LABELS = {"crust": "Borda recheada", "extra": "Adicional"}


class SizesTab(CatalogTab):
    singular = "tamanho"
    columns = [("Nome", 220), ("Fatias", 90), ("Máx. sabores", 120), ("Situação", 110)]
    service_class = SizeService

    def load_rows(self, session: Session, include_inactive: bool) -> list[TableRow]:
        return [
            TableRow(
                size.id,
                [size.name, str(size.slices), str(size.max_flavors), status_text(size.active)],
                size.active,
            )
            for size in SizeService(session).list_all(include_inactive)
        ]

    def form_fields(self, session: Session) -> list[Field]:
        return [
            Field("name", "Nome", help="Ex.: Grande, Broto"),
            Field("slices", "Número de fatias", kind="int"),
            Field(
                "max_flavors", "Máximo de sabores", kind="int",
                help="1 = apenas um sabor; 2 = permite meio a meio.",
            ),
            Field(
                "sort_order", "Ordem no cardápio", kind="int",
                help="Número menor aparece primeiro (ex.: Broto 1, Grande 2).",
            ),
        ]

    def default_values(self) -> dict[str, Any]:
        return {"slices": 8, "max_flavors": 1, "sort_order": 0}

    def initial_values(self, session: Session, entity_id: int) -> dict[str, Any]:
        size = SizeService(session).get(entity_id)
        return {
            "name": size.name, "slices": size.slices,
            "max_flavors": size.max_flavors, "sort_order": size.sort_order,
        }


class FlavorsTab(CatalogTab):
    singular = "sabor"
    columns = [("Nome", 200), ("Preços por tamanho", 420), ("Situação", 110)]
    service_class = FlavorService

    def load_rows(self, session: Session, include_inactive: bool) -> list[TableRow]:
        sizes = SizeService(session).list_all(include_inactive=True)
        names = {size.id: size.name for size in sizes}
        order = {size.id: index for index, size in enumerate(sizes)}
        rows = []
        for flavor in FlavorService(session).list_all(include_inactive):
            prices = sorted(flavor.prices, key=lambda price: order[price.size_id])
            text = "  ·  ".join(
                f"{names[price.size_id]} {format_brl(price.price_cents)}" for price in prices
            )
            rows.append(TableRow(flavor.id, [flavor.name, text, status_text(flavor.active)], flavor.active))
        return rows

    def can_create(self, session: Session) -> str | None:
        if not SizeService(session).list_all():
            return "Cadastre pelo menos um tamanho antes de criar sabores."
        return None

    def form_fields(self, session: Session) -> list[Field]:
        fields = [
            Field("name", "Nome"),
            Field("description", "Descrição", required=False),
        ]
        for index, size in enumerate(SizeService(session).list_all(include_inactive=True)):
            suffix = "" if size.active else " (tamanho inativo)"
            fields.append(
                Field(
                    f"price_{size.id}", f"Preço - {size.name}{suffix}",
                    kind="money", required=False,
                    help="Deixe em branco nos tamanhos em que o sabor não é vendido."
                    if index == 0 else None,
                )
            )
        return fields

    def initial_values(self, session: Session, entity_id: int) -> dict[str, Any]:
        flavor = FlavorService(session).get(entity_id)
        values: dict[str, Any] = {"name": flavor.name, "description": flavor.description}
        for price in flavor.prices:
            values[f"price_{price.size_id}"] = price.price_cents
        return values

    def to_service_data(self, session: Session, values: dict[str, Any]) -> dict[str, Any]:
        prices = {
            int(key.removeprefix("price_")): cents
            for key, cents in values.items()
            if key.startswith("price_") and cents is not None
        }
        return {
            "name": values["name"],
            "description": values["description"],
            "prices": prices,
        }


class ProductsTab(CatalogTab):
    singular = "produto"
    columns = [("Nome", 240), ("Categoria", 150), ("Preço", 110), ("Situação", 110)]
    service_class = ProductService

    def load_rows(self, session: Session, include_inactive: bool) -> list[TableRow]:
        service = ProductService(session)
        categories = {category.id: category.name for category in service.list_categories()}
        return [
            TableRow(
                product.id,
                [
                    product.name,
                    categories.get(product.category_id, "-"),
                    format_brl(product.price_cents),
                    status_text(product.active),
                ],
                product.active,
            )
            for product in service.list_all(include_inactive)
        ]

    def form_fields(self, session: Session) -> list[Field]:
        names = [category.name for category in ProductService(session).list_categories()]
        return [
            Field("category", "Categoria", kind="choice", choices=names),
            Field("name", "Nome", help="Ex.: Guaraná 2L"),
            Field("description", "Descrição", required=False),
            Field("price", "Preço", kind="money", help="Ex.: 12,50"),
        ]

    def initial_values(self, session: Session, entity_id: int) -> dict[str, Any]:
        service = ProductService(session)
        product = service.get(entity_id)
        categories = {category.id: category.name for category in service.list_categories()}
        return {
            "category": categories.get(product.category_id),
            "name": product.name,
            "description": product.description,
            "price": product.price_cents,
        }

    def to_service_data(self, session: Session, values: dict[str, Any]) -> dict[str, Any]:
        categories = {
            category.name: category.id for category in ProductService(session).list_categories()
        }
        return {
            "category_id": categories[values["category"]],
            "name": values["name"],
            "description": values["description"],
            "price_cents": values["price"],
        }


class AdditionalsTab(CatalogTab):
    singular = "adicional"
    columns = [("Nome", 240), ("Tipo", 150), ("Preço", 110), ("Situação", 110)]
    service_class = AdditionalService

    def load_rows(self, session: Session, include_inactive: bool) -> list[TableRow]:
        return [
            TableRow(
                item.id,
                [
                    item.name,
                    ADDITIONAL_KIND_LABELS.get(item.kind, item.kind),
                    format_brl(item.price_cents),
                    status_text(item.active),
                ],
                item.active,
            )
            for item in AdditionalService(session).list_all(include_inactive)
        ]

    def form_fields(self, session: Session) -> list[Field]:
        return [
            Field("kind", "Tipo", kind="choice", choices=list(ADDITIONAL_KIND_LABELS.values())),
            Field("name", "Nome", help="Ex.: Borda de catupiry, Bacon extra"),
            Field("price", "Preço", kind="money"),
        ]

    def initial_values(self, session: Session, entity_id: int) -> dict[str, Any]:
        item = AdditionalService(session).get(entity_id)
        return {
            "kind": ADDITIONAL_KIND_LABELS.get(item.kind),
            "name": item.name,
            "price": item.price_cents,
        }

    def to_service_data(self, session: Session, values: dict[str, Any]) -> dict[str, Any]:
        codes = {label: code for code, label in ADDITIONAL_KIND_LABELS.items()}
        return {
            "kind": codes[values["kind"]],
            "name": values["name"],
            "price_cents": values["price"],
        }
