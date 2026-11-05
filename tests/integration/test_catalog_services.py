import pytest

from src.core.exceptions import BusinessRuleError, ValidationError
from src.services.catalog_service import (
    AdditionalService,
    FlavorService,
    ProductService,
    SizeService,
    ensure_default_categories,
)


def test_sizes_are_listed_in_sort_order(session):
    service = SizeService(session)
    service.create(name="Grande", slices=8, max_flavors=2, sort_order=2)
    service.create(name="Broto", slices=4, max_flavors=1, sort_order=1)
    assert [size.name for size in service.list_all()] == ["Broto", "Grande"]


def test_size_rejects_invalid_slices_with_clear_message(session):
    with pytest.raises(ValidationError) as error:
        SizeService(session).create(name="Gigante", slices=0)
    assert "fatias" in str(error.value)


def test_size_name_must_be_unique_ignoring_case(session):
    service = SizeService(session)
    service.create(name="Grande", slices=8)
    with pytest.raises(BusinessRuleError):
        service.create(name="grande", slices=8)


def test_flavor_has_one_price_per_size(session):
    sizes = SizeService(session)
    grande = sizes.create(name="Grande", slices=8, max_flavors=2)
    broto = sizes.create(name="Broto", slices=4)
    flavor = FlavorService(session).create(
        name="Calabresa", prices={grande.id: 5000, broto.id: 3000}
    )
    prices = {price.size_id: price.price_cents for price in flavor.prices}
    assert prices == {grande.id: 5000, broto.id: 3000}


def test_flavor_requires_at_least_one_price(session):
    with pytest.raises(ValidationError):
        FlavorService(session).create(name="Mussarela", prices={})


def test_flavor_rejects_unknown_size(session):
    with pytest.raises(BusinessRuleError):
        FlavorService(session).create(name="Mussarela", prices={999: 4000})


def test_flavor_update_replaces_prices(session):
    sizes = SizeService(session)
    grande = sizes.create(name="Grande", slices=8, max_flavors=2)
    broto = sizes.create(name="Broto", slices=4)
    service = FlavorService(session)
    flavor = service.create(name="Calabresa", prices={grande.id: 5000, broto.id: 3000})

    service.update(flavor.id, name="Calabresa", prices={grande.id: 5500})

    prices = {price.size_id: price.price_cents for price in flavor.prices}
    assert prices == {grande.id: 5500}


def test_product_requires_existing_category(session):
    with pytest.raises(BusinessRuleError):
        ProductService(session).create(category_id=999, name="Guaraná 2L", price_cents=1000)


def test_deactivated_product_is_hidden_by_default(session):
    ensure_default_categories(session)
    service = ProductService(session)
    category = service.list_categories()[0]
    product = service.create(category_id=category.id, name="Guaraná 2L", price_cents=1000)

    service.set_active(product.id, False)

    assert service.list_all() == []
    assert len(service.list_all(include_inactive=True)) == 1


def test_default_categories_are_created_only_once(session):
    ensure_default_categories(session)
    ensure_default_categories(session)
    names = [category.name for category in ProductService(session).list_categories()]
    assert names == ["Bebidas", "Combos", "Sobremesas"]


def test_additional_rejects_invalid_kind(session):
    with pytest.raises(ValidationError):
        AdditionalService(session).create(name="Bacon", kind="outro", price_cents=800)


def test_additional_is_created(session):
    additional = AdditionalService(session).create(
        name="Borda de catupiry", kind="crust", price_cents=1000
    )
    assert additional.id is not None
    assert additional.active is True
