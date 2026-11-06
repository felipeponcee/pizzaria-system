"""Tabela simples com seleção de linha, compatível com tema claro/escuro."""
from collections.abc import Callable, Sequence
from typing import NamedTuple

import customtkinter as ctk

from src.ui import theme


class TableRow(NamedTuple):
    id: int
    values: list[str]
    active: bool = True


class DataTable(ctk.CTkFrame):
    def __init__(
        self,
        master,
        columns: list[tuple[str, int]],
        on_select: Callable[[int | None], None],
        on_double_click: Callable[[int], None] | None = None,
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self._columns = columns
        self._on_select = on_select
        self._on_double_click = on_double_click
        self._rows: dict[int, ctk.CTkFrame] = {}
        self._selected_id: int | None = None

        header = ctk.CTkFrame(self, fg_color=theme.TABLE_HEADER_BG, corner_radius=8)
        header.pack(fill="x", padx=(0, 20))
        self._configure_columns(header)
        for index, (title, _width) in enumerate(columns):
            ctk.CTkLabel(
                header, text=title, anchor="w", font=theme.font(13, "bold"),
                text_color=theme.TEXT_MUTED,
            ).grid(row=0, column=index, sticky="ew", padx=theme.PAD_M, pady=theme.PAD_S)

        self._body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._body.pack(fill="both", expand=True, pady=(theme.PAD_S, 0))
        self._empty = ctk.CTkLabel(
            self._body, text="Nenhum registro encontrado.",
            font=theme.font(14), text_color=theme.TEXT_MUTED,
        )

    @property
    def selected_id(self) -> int | None:
        return self._selected_id

    def _configure_columns(self, frame: ctk.CTkFrame) -> None:
        for index, (_title, width) in enumerate(self._columns):
            frame.grid_columnconfigure(index, weight=width, minsize=width)

    def set_rows(self, rows: Sequence[TableRow]) -> None:
        previous = self._selected_id
        for frame in self._rows.values():
            frame.destroy()
        self._rows.clear()
        self._selected_id = None
        self._empty.pack_forget()
        for row in rows:
            self._add_row(row)
        if not rows:
            self._empty.pack(pady=theme.PAD_L)
        if previous in self._rows:
            self.select(previous)
        else:
            self._on_select(None)

    def select(self, row_id: int) -> None:
        if self._selected_id in self._rows:
            self._rows[self._selected_id].configure(fg_color="transparent")
        self._selected_id = row_id
        self._rows[row_id].configure(fg_color=theme.SELECTED_BG)
        self._on_select(row_id)

    def _add_row(self, row: TableRow) -> None:
        frame = ctk.CTkFrame(self._body, fg_color="transparent", corner_radius=8)
        frame.pack(fill="x", pady=1)
        self._configure_columns(frame)
        color = theme.TEXT if row.active else theme.TEXT_MUTED
        widgets: list = [frame]
        for index, value in enumerate(row.values):
            label = ctk.CTkLabel(
                frame, text=value, anchor="w", font=theme.font(14), text_color=color
            )
            label.grid(row=0, column=index, sticky="ew", padx=theme.PAD_M, pady=theme.PAD_S)
            widgets.append(label)
        for widget in widgets:
            widget.bind("<Button-1>", lambda _e, rid=row.id: self.select(rid), add="+")
            widget.bind("<Double-Button-1>", lambda _e, rid=row.id: self._double(rid), add="+")
        self._rows[row.id] = frame

    def _double(self, row_id: int) -> None:
        if self._on_double_click:
            self._on_double_click(row_id)
