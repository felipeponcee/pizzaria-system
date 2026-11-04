"""Tela base: cabeçalho + cartão de conteúdo. Todas as telas herdam dela."""
import customtkinter as ctk

from src.ui import theme
from src.ui.components.page_header import PageHeader


class BaseView(ctk.CTkFrame):
    title = ""
    subtitle = ""

    def __init__(self, master) -> None:
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        PageHeader(self, self.title, self.subtitle).grid(
            row=0, column=0, sticky="ew",
            padx=theme.PAD_L, pady=(theme.PAD_L, theme.PAD_M),
        )
        self.content = ctk.CTkFrame(
            self, fg_color=theme.SURFACE, corner_radius=theme.RADIUS,
            border_width=1, border_color=theme.BORDER,
        )
        self.content.grid(
            row=1, column=0, sticky="nsew",
            padx=theme.PAD_L, pady=(0, theme.PAD_L),
        )
        self.build(self.content)

    def build(self, parent: ctk.CTkFrame) -> None:
        """Monta o conteúdo da tela. As telas reais sobrescrevem este método."""
        ctk.CTkLabel(
            parent, text="Em construção", font=theme.font(16),
            text_color=theme.TEXT_MUTED,
        ).place(relx=0.5, rely=0.5, anchor="center")

    def on_show(self) -> None:
        """Chamado toda vez que a tela é exibida (use para recarregar dados)."""
