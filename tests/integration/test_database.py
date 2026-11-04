import pytest
from sqlalchemy import inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.core.database import make_engine, run_migrations
from src.models import (
    Address, Category, Order, OrderItem, Product, User,
)

EXPECTED_TABLES = {
    "users", "customers", "addresses", "categories", "products", "sizes",
    "flavors", "flavor_prices", "additionals", "orders", "order_items",
    "order_item_flavors", "order_item_additionals", "cashier_sessions",
    "cashier_movements", "audit_logs",
}


@pytest.fixture
def engine(tmp_path):
    db_path = tmp_path / "test.db"
    run_migrations(db_path)
    engine = make_engine(db_path)
    yield engine
    engine.dispose()


def test_migrations_create_all_tables(engine):
    assert EXPECTED_TABLES <= set(inspect(engine).get_table_names())


def test_foreign_keys_are_enforced(engine):
    with Session(engine) as session:
        session.add(
            Address(customer_id=999, street="Rua A", number="1", neighborhood="Centro", city="SP")
        )
        with pytest.raises(IntegrityError):
            session.commit()


def test_invalid_role_is_rejected(engine):
    with Session(engine) as session:
        session.add(User(name="A", username="a", password_hash="x", role="hacker"))
        with pytest.raises(IntegrityError):
            session.commit()


def test_order_keeps_price_after_product_changes(engine):
    with Session(engine) as session:
        user = User(name="Admin", username="admin", password_hash="x", role="admin")
        category = Category(name="Bebidas")
        session.add_all([user, category])
        session.flush()

        product = Product(category_id=category.id, name="Guaraná 2L", price_cents=1000)
        session.add(product)
        session.flush()

        order = Order(
            created_by=user.id, order_type="counter", subtotal_cents=1000, total_cents=1000
        )
        order.items.append(
            OrderItem(
                item_type="product", product_id=product.id, name=product.name,
                quantity=1, unit_price_cents=product.price_cents,
            )
        )
        session.add(order)
        session.commit()

        product.price_cents = 1500
        session.commit()

        assert session.scalar(select(OrderItem.unit_price_cents)) == 1000
