"""Janela de formulário genérica, criada a partir de uma lista de campos."""
import logging
from collections.abc import Callable
from typing import Any

import customtkinter as ctk

from src.core.exceptions import AppError
from src.ui import theme
from src.ui.components.buttons import primary_button, secondary_button
from src.ui.components.form_fields import Field, convert_value, format_initial

logger = logging.getLogger(__name__)

FIELD_WIDTH = 380


class FormDialog(ctk.CTkToplevel):
    """Mostra os campos; ao salvar chama on_submit(valores).

    Se on_submit levantar AppError, a mensagem aparece na janela e ela continua aberta.
    """

    def __init__(
        self,
        master,
        title: str,
        fields: list[Field],
        initial: dict[str, Any],
        on_submit: Callable[[dict[str, Any]], None],
    ) -> None:
        super().__init__(master)
        self.title(title)
        self.resizable(False, False)
        self.configure(fg_color=theme.BACKGROUND)
        self._fields = fields
        self._on_submit = on_submit
        self._widgets: dict[str, Any] = {}

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=theme.PAD_L, pady=theme.PAD_L)
        body.grid_columnconfigure(0, weight=1)

        row = 0
        for field in fields:
            suffix = "" if field.required else " (opcional)"
            ctk.CTkLabel(
                body, text=f"{field.label}{suffix}", anchor="w",
                font=theme.font(13, "bold"), text_color=theme.TEXT,
            ).grid(row=row, column=0, sticky="w", pady=(theme.PAD_M, 2))
            row += 1
            widget = self._make_widget(body, field, initial.get(field.key))
            widget.grid(row=row, column=0, sticky="ew")
            self._widgets[field.key] = widget
            row += 1
            if field.help:
                ctk.CTkLabel(
                    body, text=field.help, anchor="w", justify="left",
                    font=theme.font(12), text_color=theme.TEXT_MUTED,
                    wraplength=FIELD_WIDTH,
                ).grid(row=row, column=0, sticky="w")
                row += 1

        self._error = ctk.CTkLabel(
            body, text="", anchor="w", justify="left",
            text_color=theme.DANGER, font=theme.font(13), wraplength=FIELD_WIDTH,
        )
        self._error.grid(row=row, column=0, sticky="ew", pady=(theme.PAD_M, 0))

        buttons = ctk.CTkFrame(body, fg_color="transparent")
        buttons.grid(row=row + 1, column=0, sticky="e", pady=(theme.PAD_M, 0))
        secondary_button(buttons, "Cancelar", self.destroy).pack(
            side="left", padx=(0, theme.PAD_S)
        )
        primary_button(buttons, "Salvar", self._submit, width=110).pack(side="left")

        self.bind("<Return>", lambda _e: self._submit())
        self.bind("<Escape>", lambda _e: self.destroy())
        self.after(50, self._show)

    def _make_widget(self, parent, field: Field, value: Any):
        if field.kind == "choice":
            choices = field.choices or []
            box = ctk.CTkComboBox(
                parent, values=choices, state="readonly",
                width=FIELD_WIDTH, height=36, font=theme.font(14),
            )
            box.set(str(value) if value in choices else (choices[0] if choices else ""))
            return box
        entry = ctk.CTkEntry(parent, width=FIELD_WIDTH, height=36, font=theme.font(14))
        entry.insert(0, format_initial(field, value))
        return entry

    def _show(self) -> None:
        """Centraliza sobre a janela principal, bloqueia a janela de trás e foca o 1º campo."""
        self.update_idletasks()
        parent = self.master.winfo_toplevel()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 3
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        self.transient(parent)
        self.wait_visibility()
        self.grab_set()
        for widget in self._widgets.values():
            widget.focus()
            break

    def _submit(self) -> None:
        try:
            values = {
                field.key: convert_value(field, self._widgets[field.key].get())
                for field in self._fields
            }
            self._on_submit(values)
        except AppError as exc:
            self._error.configure(text=str(exc))
            return
        except Exception as exc:
            logger.exception("Erro inesperado ao salvar o formulário")
            self._error.configure(
                text=f"Erro inesperado ({type(exc).__name__}). Consulte o arquivo de log."
            )
            return
        self.destroy()
