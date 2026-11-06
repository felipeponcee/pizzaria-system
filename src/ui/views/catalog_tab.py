"""Base das abas de cadastro: busca, filtro de inativos, tabela e botões."""
import logging
from tkinter import messagebox
from typing import Any

import customtkinter as ctk
from sqlalchemy.orm import Session

from src.core.database import session_scope
from src.core.exceptions import AppError
from src.services.base_service import CatalogService
from src.ui import theme
from src.ui.components.buttons import primary_button, secondary_button
from src.ui.components.data_table import DataTable, TableRow
from src.ui.components.form_dialog import FormDialog
from src.ui.components.form_fields import Field

logger = logging.getLogger(__name__)


def status_text(active: bool) -> str:
    return "Ativo" if active else "Inativo"


class CatalogTab(ctk.CTkFrame):
    """Cada aba concreta define colunas, formulário e como ler/gravar."""

    singular = "item"
    columns: list[tuple[str, int]] = []
    service_class: type[CatalogService]

    def __init__(self, master) -> None:
        super().__init__(master, fg_color="transparent")
        self._all_rows: list[TableRow] = []

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, theme.PAD_M))

        self._search = ctk.CTkEntry(
            toolbar, placeholder_text="Pesquisar...", width=260, height=36,
            font=theme.font(14),
        )
        self._search.pack(side="left")
        self._search.bind("<KeyRelease>", lambda _e: self._apply_filter())

        self._inactive_switch = ctk.CTkSwitch(
            toolbar, text="Mostrar inativos", font=theme.font(13),
            text_color=theme.TEXT, command=self.refresh,
        )
        self._inactive_switch.pack(side="left", padx=theme.PAD_L)

        self._toggle_button = secondary_button(toolbar, "Desativar", self._toggle_active)
        self._toggle_button.pack(side="right")
        self._edit_button = secondary_button(toolbar, "Editar", self._edit, width=90)
        self._edit_button.pack(side="right", padx=theme.PAD_S)
        primary_button(toolbar, f"Novo {self.singular}", self._new).pack(side="right")

        self._table = DataTable(
            self, self.columns, on_select=self._on_select,
            on_double_click=lambda _id: self._edit(),
        )
        self._table.pack(fill="both", expand=True)
        self._on_select(None)

    # ---- A implementar nas abas concretas ----
    def load_rows(self, session: Session, include_inactive: bool) -> list[TableRow]:
        raise NotImplementedError

    def form_fields(self, session: Session) -> list[Field]:
        raise NotImplementedError

    def initial_values(self, session: Session, entity_id: int) -> dict[str, Any]:
        raise NotImplementedError

    def default_values(self) -> dict[str, Any]:
        return {}

    def to_service_data(self, session: Session, values: dict[str, Any]) -> dict[str, Any]:
        return values

    def can_create(self, session: Session) -> str | None:
        """Retorne uma mensagem se ainda não for possível criar (ex.: falta um pré-requisito)."""
        return None

    # ---- Ações ----
    def refresh(self) -> None:
        try:
            with session_scope() as session:
                self._all_rows = self.load_rows(session, bool(self._inactive_switch.get()))
        except Exception:
            logger.exception("Falha ao carregar %s", self.singular)
            messagebox.showerror("Erro", "Não foi possível carregar os dados.")
            return
        self._apply_filter()

    def _apply_filter(self) -> None:
        text = self._search.get().strip().casefold()
        rows = [
            row for row in self._all_rows
            if not text or text in " ".join(row.values).casefold()
        ]
        self._table.set_rows(rows)

    def _on_select(self, row_id: int | None) -> None:
        state = "normal" if row_id is not None else "disabled"
        self._edit_button.configure(state=state)
        self._toggle_button.configure(state=state)
        row = self._find_row(row_id)
        if row is not None:
            self._toggle_button.configure(text="Desativar" if row.active else "Ativar")

    def _find_row(self, row_id: int | None) -> TableRow | None:
        return next((row for row in self._all_rows if row.id == row_id), None)

    def _new(self) -> None:
        try:
            with session_scope() as session:
                message = self.can_create(session)
                if message:
                    messagebox.showinfo("Atenção", message, parent=self.winfo_toplevel())
                    return
                fields = self.form_fields(session)
        except Exception:
            logger.exception("Falha ao abrir o formulário")
            messagebox.showerror("Erro", "Não foi possível abrir o formulário.")
            return
        self._open_form(f"Novo {self.singular}", fields, self.default_values(), None)

    def _edit(self) -> None:
        entity_id = self._table.selected_id
        if entity_id is None:
            return
        try:
            with session_scope() as session:
                fields = self.form_fields(session)
                initial = self.initial_values(session, entity_id)
        except AppError as exc:
            messagebox.showerror("Erro", str(exc))
            self.refresh()
            return
        except Exception:
            logger.exception("Falha ao abrir o formulário de edição")
            messagebox.showerror("Erro", "Não foi possível abrir o formulário.")
            return
        self._open_form(f"Editar {self.singular}", fields, initial, entity_id)

    def _open_form(
        self, title: str, fields: list[Field], initial: dict[str, Any], entity_id: int | None
    ) -> None:
        FormDialog(
            self.winfo_toplevel(), title, fields, initial,
            on_submit=lambda values: self._save(entity_id, values),
        )

    def _save(self, entity_id: int | None, values: dict[str, Any]) -> None:
        with session_scope() as session:
            data = self.to_service_data(session, values)
            service = self.service_class(session)
            if entity_id is None:
                service.create(**data)
            else:
                service.update(entity_id, **data)
        self.refresh()

    def _toggle_active(self) -> None:
        row = self._find_row(self._table.selected_id)
        if row is None:
            return
        new_active = not row.active
        verb = "ativar" if new_active else "desativar"
        confirmed = messagebox.askyesno(
            "Confirmar",
            f"Deseja {verb} este {self.singular}?\n\n{row.values[0]}",
            parent=self.winfo_toplevel(),
        )
        if not confirmed:
            return
        try:
            with session_scope() as session:
                self.service_class(session).set_active(row.id, new_active)
        except AppError as exc:
            messagebox.showerror("Erro", str(exc))
        except Exception:
            logger.exception("Falha ao alterar situação")
            messagebox.showerror("Erro", "Não foi possível alterar a situação.")
        self.refresh()
