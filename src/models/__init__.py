"""Importa todos os models para que o SQLAlchemy/Alembic conheçam as tabelas."""
from src.models.audit import AuditLog
from src.models.base import Base
from src.models.cashier import CashierMovement, CashierSession
from src.models.catalog import Additional, Category, Flavor, FlavorPrice, Product, Size
from src.models.customer import Address, Customer
from src.models.order import Order, OrderItem, OrderItemAdditional, OrderItemFlavor
from src.models.user import User

__all__ = [
    "Additional", "Address", "AuditLog", "Base", "CashierMovement", "CashierSession",
    "Category", "Customer", "Flavor", "FlavorPrice", "Order", "OrderItem",
    "OrderItemAdditional", "OrderItemFlavor", "Product", "Size", "User",
]
