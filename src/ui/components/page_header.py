"""Cabeçalho padrão das telas: título e subtítulo."""
import customtkinter as ctk

from src.ui import theme


class PageHeader(ctk.CTkFrame):
    def __init__(self, master, title: str, subtitle: str = "") -> None:
        super().__init__(master, fg_color="transparent")
        ctk.CTkLabel(
            self, text=title, font=theme.font(26, "bold"),
            text_color=theme.TEXT, anchor="w",
        ).pack(fill="x")
        if subtitle:
            ctk.CTkLabel(
                self, text=subtitle, font=theme.font(14),
                text_color=theme.TEXT_MUTED, anchor="w",
            ).pack(fill="x")
