"""Janela principal: menu lateral + área de conteúdo com as telas."""
import customtkinter as ctk

from src.app.config import APP_NAME, APP_VERSION
from src.ui import theme
from src.ui.components.sidebar import Sidebar
from src.ui.navigation import NAV_ITEMS
from src.ui.views.base_view import BaseView


class MainWindow(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry("1200x720")
        self.minsize(1000, 650)
        self.configure(fg_color=theme.BACKGROUND)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._views: dict[str, BaseView] = {}

        self._sidebar = Sidebar(
            self,
            [(key, label) for key, label, _ in NAV_ITEMS],
            self.show_view,
            self._set_dark_mode,
        )
        self._sidebar.grid(row=0, column=0, sticky="ns")

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=1, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

        for key, _label, view_class in NAV_ITEMS:
            view = view_class(container)
            view.grid(row=0, column=0, sticky="nsew")
            self._views[key] = view

        self.show_view(NAV_ITEMS[0][0])
        self.after(50, lambda: self.state("zoomed"))

    def show_view(self, key: str) -> None:
        view = self._views[key]
        view.tkraise()
        view.on_show()
        self._sidebar.set_active(key)

    @staticmethod
    def _set_dark_mode(enabled: bool) -> None:
        ctk.set_appearance_mode("dark" if enabled else "light")
