from types import SimpleNamespace

import pytest

from src.core.exceptions import BusinessRuleError, ValidationError
from src.models import User
from src.services.catalog_service import (
    AdditionalService,
    FlavorService,
    ProductService,
    SizeService,
    ensure_default_categories,
)
from src.services.order_service import OrderService


@pytest.fixture
def catalog(session):
    sizes = SizeService(session)
    grande = sizes.create(name="Grande", slices=8, max_flavors=2, sort_order=2)
    broto = sizes.create(name="Broto", slices=4, max_flavors=1, sort_order=1)

    flavors = FlavorService(session)
    calabresa = flavors.create(name="Calabresa", prices={grande.id: 5000, broto.id: 3000})
    mussarela = flavors.create(name="Mussarela", prices={grande.id: 4000, broto.id: 2500})
    camarao = flavors.create(name="Camarão", prices={grande.id: 7000})

    borda = AdditionalService(session).create(
        name="Borda de catupiry", kind="crust", price_cents=1000
    )

    ensure_default_categories(session)
    products = ProductService(session)
    category = products.list_categories()[0]
    guarana = products.create(category_id=category.id, name="Guaraná 2L", price_cents=1000)

    user = User(name="Admin", username="admin", password_hash="x", role="admin")
    session.add(user)
    session.flush()

    return SimpleNamespace(
        grande=grande, broto=broto, calabresa=calabresa, mussarela=mussarela,
        camarao=camarao, borda=borda, guarana=guarana, user=user,
    )


def pizza_item(size, flavors, additionals=(), quantity=1):
    return {
        "kind": "pizza",
        "size_id": size.id,
        "flavor_ids": [flavor.id for flavor in flavors],
        "additional_ids": [additional.id for additional in additionals],
        "quantity": quantity,
    }


def product_item(product, quantity=1):
    return {"kind": "product", "product_id": product.id, "quantity": quantity}


def counter_order(service, catalog, items, **extra):
    return service.create_order(
        created_by=catalog.user.id, order_type="counter", items=items, **extra
    )


def test_whole_pizza_line_and_totals(session, catalog):
    order = counter_order(
        OrderService(session), catalog,
        [pizza_item(catalog.grande, [catalog.calabresa], quantity=2)],
    )
    item = order.items[0]
    assert item.name == "Pizza Grande"
    assert item.unit_price_cents == 5000
    assert order.subtotal_cents == 10000
    assert order.total_cents == 10000
    assert order.status == "received"


def test_half_and_half_charges_the_most_expensive_flavor(session, catalog):
    order = counter_order(
        OrderService(session), catalog,
        [pizza_item(catalog.grande, [catalog.mussarela, catalog.calabresa])],
    )
    item = order.items[0]
    assert item.unit_price_cents == 5000
    assert [(f.name, f.price_cents) for f in item.flavors] == [
        ("Mussarela", 4000),
        ("Calabresa", 5000),
    ]


def test_additionals_are_added_to_the_pizza_price(session, catalog):
    order = counter_order(
        OrderService(session), catalog,
        [pizza_item(catalog.grande, [catalog.calabresa], [catalog.borda])],
    )
    item = order.items[0]
    assert item.unit_price_cents == 6000
    assert [a.name for a in item.additionals] == ["Borda de catupiry"]


def test_pizza_not_sold_in_the_size_is_rejected(session, catalog):
    with pytest.raises(BusinessRuleError):
        counter_order(
            OrderService(session), catalog,
            [pizza_item(catalog.broto, [catalog.camarao])],
        )


def test_too_many_flavors_for_the_size_is_rejected(session, catalog):
    with pytest.raises(BusinessRuleError):
        counter_order(
            OrderService(session), catalog,
            [pizza_item(catalog.broto, [catalog.calabresa, catalog.mussarela])],
        )


def test_pizza_that_refuses_half_and_half_is_rejected(session, catalog):
    FlavorService(session).update(
        catalog.camarao.id,
        name="Camarão",
        allows_half=False,
        prices={catalog.grande.id: 7000},
    )
    with pytest.raises(BusinessRuleError) as error:
        counter_order(
            OrderService(session), catalog,
            [pizza_item(catalog.grande, [catalog.calabresa, catalog.camarao])],
        )
    assert "meio a meio" in str(error.value)


def test_delivery_order_with_product_discount_and_fee(session, catalog):
    order = OrderService(session).create_order(
        created_by=catalog.user.id,
        order_type="delivery",
        customer_name="Cliente Teste",
        customer_phone="11999990000",
        delivery_address="Rua das Flores, 10 - Centro",
        items=[product_item(catalog.guarana, quantity=2)],
        discount_cents=500,
        delivery_fee_cents=800,
    )
    assert (
        order.subtotal_cents,
        order.discount_cents,
        order.delivery_fee_cents,
        order.total_cents,
    ) == (2000, 500, 800, 2300)


def test_discount_greater_than_subtotal_is_rejected(session, catalog):
    with pytest.raises(BusinessRuleError):
        counter_order(
            OrderService(session), catalog,
            [product_item(catalog.guarana)], discount_cents=9999,
        )


def test_delivery_order_requires_an_address(session, catalog):
    with pytest.raises(ValidationError) as error:
        OrderService(session).create_order(
            created_by=catalog.user.id,
            order_type="delivery",
            customer_name="Cliente Teste",
            customer_phone="11999990000",
            items=[product_item(catalog.guarana)],
        )
    assert "endereço" in str(error.value)


def test_counter_order_cannot_have_a_delivery_fee(session, catalog):
    with pytest.raises(ValidationError):
        counter_order(
            OrderService(session), catalog,
            [product_item(catalog.guarana)], delivery_fee_cents=500,
        )


def test_order_keeps_prices_after_the_menu_changes(session, catalog):
    order = counter_order(
        OrderService(session), catalog,
        [pizza_item(catalog.grande, [catalog.calabresa])],
    )
    FlavorService(session).update(
        catalog.calabresa.id,
        name="Calabresa",
        prices={catalog.grande.id: 6000, catalog.broto.id: 3000},
    )
    item = order.items[0]
    assert item.unit_price_cents == 5000
    assert item.flavors[0].price_cents == 5000


def test_inactive_pizza_cannot_be_ordered(session, catalog):
    FlavorService(session).set_active(catalog.calabresa.id, False)
    with pytest.raises(BusinessRuleError):
        counter_order(
            OrderService(session), catalog,
            [pizza_item(catalog.grande, [catalog.calabresa])],
        )


def test_unknown_user_cannot_create_orders(session, catalog):
    with pytest.raises(BusinessRuleError):
        OrderService(session).create_order(
            created_by=999,
            order_type="counter",
            items=[product_item(catalog.guarana)],
        )
