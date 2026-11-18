import pytest

from src.core.exceptions import BusinessRuleError, ValidationError
from src.services.pricing import (
    HalfAndHalfRule,
    calculate_totals,
    percent_discount,
    pizza_unit_price,
)


def test_whole_pizza_uses_its_flavor_price():
    assert pizza_unit_price([5000]) == 5000


def test_half_and_half_uses_the_most_expensive_flavor():
    assert pizza_unit_price([4000, 5000]) == 5000


def test_average_rule_rounds_half_up():
    assert pizza_unit_price([5000, 4000], HalfAndHalfRule.AVERAGE) == 4500
    assert pizza_unit_price([5000, 4001], HalfAndHalfRule.AVERAGE) == 4501


def test_pizza_requires_at_least_one_flavor():
    with pytest.raises(ValidationError):
        pizza_unit_price([])


def test_percent_discount():
    assert percent_discount(2050, 10) == 205
    assert percent_discount(1000, 100) == 1000
    assert percent_discount(1000, 0) == 0


def test_percent_discount_rejects_invalid_percent():
    with pytest.raises(ValidationError):
        percent_discount(1000, 101)


def test_totals_add_delivery_fee_after_discount():
    totals = calculate_totals([5000, 2000], discount_cents=500, delivery_fee_cents=800)
    assert totals.subtotal_cents == 7000
    assert totals.discount_cents == 500
    assert totals.delivery_fee_cents == 800
    assert totals.total_cents == 7300


def test_discount_cannot_exceed_subtotal():
    with pytest.raises(BusinessRuleError):
        calculate_totals([1000], discount_cents=1001)


def test_negative_values_are_rejected():
    with pytest.raises(ValidationError):
        calculate_totals([1000], discount_cents=-1)
    with pytest.raises(ValidationError):
        calculate_totals([1000], delivery_fee_cents=-1)
