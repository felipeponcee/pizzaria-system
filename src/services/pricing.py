"""Regras de cálculo de preço do pedido. Funções puras: sem banco e sem telas."""
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum

from src.core.exceptions import BusinessRuleError, ValidationError


class HalfAndHalfRule(str, Enum):
    """Como cobrar uma pizza com mais de um sabor."""

    HIGHEST = "highest"  # cobra o preço do sabor mais caro (regra da pizzaria)
    AVERAGE = "average"  # cobra a média dos preços dos sabores


def pizza_unit_price(
    flavor_prices: Sequence[int], rule: HalfAndHalfRule = HalfAndHalfRule.HIGHEST
) -> int:
    """Preço de uma pizza (em centavos) a partir do preço de cada sabor no tamanho."""
    if not flavor_prices:
        raise ValidationError("Escolha pelo menos um sabor.")
    if rule is HalfAndHalfRule.HIGHEST:
        return max(flavor_prices)
    count = len(flavor_prices)
    return (2 * sum(flavor_prices) + count) // (2 * count)  # média, arredondada para cima


def percent_discount(subtotal_cents: int, percent: int) -> int:
    """Converte um desconto em percentual para centavos."""
    if not 0 <= percent <= 100:
        raise ValidationError("O percentual de desconto deve estar entre 0 e 100.")
    return (subtotal_cents * percent + 50) // 100


@dataclass(frozen=True)
class OrderTotals:
    subtotal_cents: int
    discount_cents: int
    delivery_fee_cents: int
    total_cents: int


def calculate_totals(
    line_totals: Sequence[int], discount_cents: int = 0, delivery_fee_cents: int = 0
) -> OrderTotals:
    """Subtotal, desconto (sobre o subtotal) e taxa de entrega (somada no fim)."""
    if discount_cents < 0 or delivery_fee_cents < 0:
        raise ValidationError("Desconto e taxa de entrega não podem ser negativos.")
    subtotal = sum(line_totals)
    if discount_cents > subtotal:
        raise BusinessRuleError("O desconto não pode ser maior que o subtotal do pedido.")
    return OrderTotals(
        subtotal_cents=subtotal,
        discount_cents=discount_cents,
        delivery_fee_cents=delivery_fee_cents,
        total_cents=subtotal - discount_cents + delivery_fee_cents,
    )
