"""Registro das telas do menu lateral (chave, rótulo, classe da tela)."""
from src.ui.views.base_view import BaseView
from src.ui.views.cashier_view import CashierView
from src.ui.views.customers_view import CustomersView
from src.ui.views.dashboard_view import DashboardView
from src.ui.views.orders_view import OrdersView
from src.ui.views.products_view import ProductsView
from src.ui.views.settings_view import SettingsView

NAV_ITEMS: list[tuple[str, str, type[BaseView]]] = [
    ("dashboard", "Dashboard", DashboardView),
    ("orders", "Pedidos", OrdersView),
    ("products", "Produtos", ProductsView),
    ("customers", "Clientes", CustomersView),
    ("cashier", "Caixa", CashierView),
    ("settings", "Configurações", SettingsView),
]
