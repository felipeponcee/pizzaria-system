import pytest
from sqlalchemy import func, select

from src.core.exceptions import BusinessRuleError
from src.models import FlavorPrice, Order, OrderItem, User
from src.services.catalog_service import (
    FlavorService,
    ProductService,
    SizeService,
    ensure_default_categories,
)


def add_order_with_item(session, **item_fields):
    user = User(name="Admin", username="admin", password_hash="x", role="admin")
    session.add(user)
    session.flush()
    order = Order(
        created_by=user.id, order_type="counter", subtotal_cents=1000, total_cents=1000
    )
    order.items.append(
        OrderItem(name="Item", quantity=1, unit_price_cents=1000, **item_fields)
    )
    session.add(order)
    session.flush()


def create_product(session):
    ensure_default_categories(session)
    service = ProductService(session)
    category = service.list_categories()[0]
    product = service.create(category_id=category.id, name="Guaraná 2L", price_cents=1000)
    return service, product


def test_unused_product_can_be_deleted(session):
    service, product = create_product(session)
    service.delete(product.id)
    assert service.list_all(include_inactive=True) == []


def test_product_used_in_an_order_cannot_be_deleted(session):
    service, product = create_product(session)
    add_order_with_item(session, item_type="product", product_id=product.id)
    with pytest.raises(BusinessRuleError) as error:
        service.delete(product.id)
    assert "Desative" in str(error.value)
    assert len(service.list_all(include_inactive=True)) == 1


def test_size_used_in_an_order_cannot_be_deleted(session):
    sizes = SizeService(session)
    grande = sizes.create(name="Grande", slices=8)
    add_order_with_item(session, item_type="pizza", size_id=grande.id)
    with pytest.raises(BusinessRuleError):
        sizes.delete(grande.id)


def test_deleting_a_pizza_removes_its_prices(session):
    grande = SizeService(session).create(name="Grande", slices=8)
    flavors = FlavorService(session)
    flavor = flavors.create(name="Calabresa", prices={grande.id: 5000})
    flavors.delete(flavor.id)
    assert flavors.list_all(include_inactive=True) == []
    assert session.scalar(select(func.count(FlavorPrice.id))) == 0


def test_deleting_a_size_removes_pizza_prices_for_it(session):
    sizes = SizeService(session)
    grande = sizes.create(name="Grande", slices=8)
    broto = sizes.create(name="Broto", slices=4)
    flavor = FlavorService(session).create(
        name="Calabresa", prices={grande.id: 5000, broto.id: 3000}
    )
    sizes.delete(broto.id)
    session.expire_all()
    assert [price.size_id for price in flavor.prices] == [grande.id]
