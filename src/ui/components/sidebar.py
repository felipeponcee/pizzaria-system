"""Menu lateral de navegação."""
from collections.abc import Callable

import customtkinter as ctk

from src.app.config import APP_VERSION
from src.ui import theme


class Sidebar(ctk.CTkFrame):
    def __init__(
        self,
        master,
        items: list[tuple[str, str]],
        on_navigate: Callable[[str], None],
        on_toggle_dark: Callable[[bool], None],
    ) -> None:
        super().__init__(
            master, width=theme.SIDEBAR_WIDTH, corner_radius=0, fg_color=theme.SIDEBAR_BG
        )
        self.pack_propagate(False)
        self._buttons: dict[str, ctk.CTkButton] = {}

        ctk.CTkLabel(
            self, text="Pizzaria", font=theme.font(24, "bold"), text_color="#FFFFFF"
        ).pack(padx=theme.PAD_L, pady=(theme.PAD_L, theme.PAD_L), anchor="w")

        for key, label in items:
            button = ctk.CTkButton(
                self, text=label, anchor="w", height=42, corner_radius=8,
                fg_color="transparent", hover_color=theme.SIDEBAR_HOVER,
                text_color=theme.SIDEBAR_TEXT, font=theme.font(15),
                command=lambda k=key: on_navigate(k),
            )
            button.pack(fill="x", padx=theme.PAD_M, pady=2)
            self._buttons[key] = button

        ctk.CTkLabel(
            self, text=f"Versão {APP_VERSION}", font=theme.font(12), text_color="#9CA3AF"
        ).pack(side="bottom", padx=theme.PAD_L, pady=(0, theme.PAD_M), anchor="w")

        self._dark_switch = ctk.CTkSwitch(
            self, text="Tema escuro", text_color=theme.SIDEBAR_TEXT,
            font=theme.font(13),
            command=lambda: on_toggle_dark(bool(self._dark_switch.get())),
        )
        if ctk.get_appearance_mode() == "Dark":
            self._dark_switch.select()
        self._dark_switch.pack(side="bottom", padx=theme.PAD_L, pady=theme.PAD_S, anchor="w")

    def set_active(self, key: str) -> None:
        """Destaca o item do menu da tela atual."""
        for button_key, button in self._buttons.items():
            active = button_key == key
            button.configure(
                fg_color=theme.PRIMARY if active else "transparent",
                hover_color=theme.PRIMARY_HOVER if active else theme.SIDEBAR_HOVER,
            )
