"""Tela Produtos: abas de Tamanhos, Sabores, Produtos e Adicionais."""
import customtkinter as ctk

from src.ui import theme
from src.ui.views.base_view import BaseView
from src.ui.views.catalog_tab import CatalogTab
from src.ui.views.catalog_tabs import AdditionalsTab, FlavorsTab, ProductsTab, SizesTab

TABS: list[tuple[str, type[CatalogTab]]] = [
    ("Tamanhos", SizesTab),
    ("Sabores", FlavorsTab),
    ("Produtos", ProductsTab),
    ("Adicionais", AdditionalsTab),
]


class ProductsView(BaseView):
    title = "Produtos"
    subtitle = "Cardápio, sabores, tamanhos e adicionais"

    def build(self, parent: ctk.CTkFrame) -> None:
        self._tabs = ctk.CTkTabview(
            parent, fg_color="transparent",
            segmented_button_selected_color=theme.PRIMARY,
            segmented_button_selected_hover_color=theme.PRIMARY_HOVER,
            command=self._refresh_current,
        )
        self._tabs.pack(fill="both", expand=True, padx=theme.PAD_M, pady=theme.PAD_S)
        self._tab_views: dict[str, CatalogTab] = {}
        for name, tab_class in TABS:
            view = tab_class(self._tabs.add(name))
            view.pack(fill="both", expand=True)
            self._tab_views[name] = view

    def on_show(self) -> None:
        self._refresh_current()

    def _refresh_current(self) -> None:
        self._tab_views[self._tabs.get()].refresh()
