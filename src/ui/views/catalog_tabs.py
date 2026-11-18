"""Abas concretas do cadastro do cardápio."""
from typing import Any

from sqlalchemy.orm import Session

from src.core.money import format_brl
from src.services.catalog_service import (
    AdditionalService,
    ProductService,
)
from src.ui.components.data_table import TableRow
from src.ui.components.form_fields import Field
from src.ui.views.catalog_tab import CatalogTab, status_text

ADDITIONAL_KIND_LABELS = {"crust": "Borda recheada", "extra": "Adicional"}


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
