"""Cadastro de pizzas em uma única tela: nome, descrição, meio a meio e preço por tamanho."""
import logging
from tkinter import messagebox
from typing import Any

from sqlalchemy.orm import Session

from src.core.database import session_scope
from src.core.money import format_brl
from src.services.catalog_service import FlavorService, SizeService
from src.ui.components.data_table import TableRow
from src.ui.components.form_fields import Field
from src.ui.views.catalog_tab import CatalogTab, status_text

logger = logging.getLogger(__name__)

YES = "Sim"
NO = "Não"
FIXED_COLUMNS = [("Pizza", 200), ("Descrição", 220), ("Meio a meio", 100)]


def build_pizza_columns(sizes) -> list[tuple[str, int]]:
    """Colunas fixas + uma coluna de preço para cada tamanho cadastrado."""
    columns = list(FIXED_COLUMNS)
    for size in sizes:
        suffix = "" if size.active else " (inativo)"
        columns.append((f"{size.name} ({size.slices} fatias){suffix}", 140))
    columns.append(("Situação", 100))
    return columns


class PizzasTab(CatalogTab):
    """Uma pizza = nome, descrição, aceita meio a meio e um preço por tamanho."""

    singular = "pizza"
    new_word = "Nova"
    this_word = "esta"
    columns = [*FIXED_COLUMNS, ("Situação", 100)]  # as colunas de tamanho entram no refresh
    service_class = FlavorService

    def __init__(self, master) -> None:
        super().__init__(master)
        self._current_columns = list(self.columns)

    def refresh(self) -> None:
        try:
            with session_scope() as session:
                sizes = SizeService(session).list_all(include_inactive=True)
                columns = build_pizza_columns(sizes)
        except Exception:
            logger.exception("Falha ao carregar os tamanhos")
            messagebox.showerror("Erro", "Não foi possível carregar os dados.")
            return
        if columns != self._current_columns:
            self._table.set_columns(columns)
            self._current_columns = columns
        super().refresh()

    def load_rows(self, session: Session, include_inactive: bool) -> list[TableRow]:
        sizes = SizeService(session).list_all(include_inactive=True)
        rows = []
        for pizza in FlavorService(session).list_all(include_inactive):
            prices = {price.size_id: price.price_cents for price in pizza.prices}
            values = [pizza.name, pizza.description or "-", YES if pizza.allows_half else NO]
            values += [
                format_brl(prices[size.id]) if size.id in prices else "-" for size in sizes
            ]
            values.append(status_text(pizza.active))
            rows.append(TableRow(pizza.id, values, pizza.active))
        return rows

    def default_values(self) -> dict[str, Any]:
        return {"half": YES}

    def form_fields(self, session: Session) -> list[Field]:
        fields = [
            Field("name", "Nome da pizza"),
            Field("description", "Descrição", required=False, help="Ex.: ingredientes da pizza"),
            Field("half", "Aceita meio a meio?", kind="choice", choices=[YES, NO]),
        ]
        sizes = SizeService(session).list_all(include_inactive=True)
        for index, size in enumerate(sizes):
            suffix = "" if size.active else " (tamanho inativo)"
            fields.append(
                Field(
                    f"price_{size.id}",
                    f"Preço - {size.name} ({size.slices} fatias){suffix}",
                    kind="money",
                    required=False,
                    help="Preencha os tamanhos que a pizzaria vende. "
                    "Deixe em branco o que não é vendido."
                    if index == 0 else None,
                )
            )
        return fields

    def initial_values(self, session: Session, entity_id: int) -> dict[str, Any]:
        pizza = FlavorService(session).get(entity_id)
        values: dict[str, Any] = {
            "name": pizza.name,
            "description": pizza.description,
            "half": YES if pizza.allows_half else NO,
        }
        for price in pizza.prices:
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
            "allows_half": values["half"] == YES,
            "prices": prices,
        }
