"""Botões padrão do sistema."""
from collections.abc import Callable

import customtkinter as ctk

from src.ui import theme


def primary_button(
    master, text: str, command: Callable[[], None], width: int = 130
) -> ctk.CTkButton:
    return ctk.CTkButton(
        master, text=text, command=command, width=width, height=36,
        corner_radius=8, fg_color=theme.PRIMARY, hover_color=theme.PRIMARY_HOVER,
        text_color="#FFFFFF", font=theme.font(14, "bold"),
    )


def secondary_button(
    master, text: str, command: Callable[[], None], width: int = 110
) -> ctk.CTkButton:
    return ctk.CTkButton(
        master, text=text, command=command, width=width, height=36,
        corner_radius=8, fg_color=theme.SECONDARY_BG, hover_color=theme.SECONDARY_HOVER,
        text_color=theme.TEXT, text_color_disabled=theme.TEXT_MUTED,
        font=theme.font(14),
    )


def danger_button(
    master, text: str, command: Callable[[], None], width: int = 100
) -> ctk.CTkButton:
    return ctk.CTkButton(
        master, text=text, command=command, width=width, height=36,
        corner_radius=8, fg_color=theme.DANGER, hover_color="#B91C1C",
        text_color="#FFFFFF", text_color_disabled="#FECACA",
        font=theme.font(14),
    )
