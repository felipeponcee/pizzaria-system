import pytest

from src.core.exceptions import BusinessRuleError
from src.services.catalog_service import FlavorService, SizeService, ensure_default_sizes


def grande_size(session):
    ensure_default_sizes(session)
    return SizeService(session).list_all()[-1]


def test_default_sizes_are_created_only_once(session):
    ensure_default_sizes(session)
    ensure_default_sizes(session)
    sizes = SizeService(session).list_all()
    assert [(size.name, size.slices) for size in sizes] == [("Broto", 4), ("Grande", 8)]


def test_pizza_accepts_half_and_half_by_default(session):
    grande = grande_size(session)
    pizza = FlavorService(session).create(name="Calabresa", prices={grande.id: 5000})
    assert pizza.allows_half is True


def test_pizza_can_refuse_half_and_half_and_be_changed_later(session):
    grande = grande_size(session)
    service = FlavorService(session)
    pizza = service.create(name="Camarão", allows_half=False, prices={grande.id: 7000})
    assert pizza.allows_half is False

    service.update(pizza.id, name="Camarão", allows_half=True, prices={grande.id: 7000})
    assert pizza.allows_half is True


def test_duplicate_pizza_message_explains_what_to_do(session):
    grande = grande_size(session)
    service = FlavorService(session)
    service.create(name="Calabresa", prices={grande.id: 5000})
    with pytest.raises(BusinessRuleError) as error:
        service.create(name="calabresa", prices={grande.id: 5000})
    assert "Editar" in str(error.value)


def test_duplicate_message_for_inactive_pizza_mentions_activating(session):
    grande = grande_size(session)
    service = FlavorService(session)
    pizza = service.create(name="Calabresa", prices={grande.id: 5000})
    service.set_active(pizza.id, False)
    with pytest.raises(BusinessRuleError) as error:
        service.create(name="Calabresa", prices={grande.id: 5000})
    assert "inativo" in str(error.value)
