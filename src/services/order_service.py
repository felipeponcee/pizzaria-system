"""Criação de pedidos: valida contra o cardápio, calcula valores e grava o histórico."""
import logging
from typing import Any

from sqlalchemy.orm import Session

from src.core.exceptions import BusinessRuleError
from src.models import (
    Additional,
    Customer,
    Flavor,
    Order,
    OrderItem,
    OrderItemAdditional,
    OrderItemFlavor,
    Product,
    Size,
    User,
)
from src.schemas.base import validate_or_raise
from src.schemas.order import OrderIn, OrderItemIn
from src.services.pricing import HalfAndHalfRule, calculate_totals, pizza_unit_price

logger = logging.getLogger(__name__)


class OrderService:
    def __init__(
        self, session: Session, half_rule: HalfAndHalfRule = HalfAndHalfRule.HIGHEST
    ) -> None:
        self.session = session
        self.half_rule = half_rule

    def create_order(self, **data: Any) -> Order:
        """Cria o pedido completo em uma única transação, com nomes e preços copiados."""
        dto = validate_or_raise(OrderIn, **data)
        self._get_active(User, dto.created_by, "Usuário")
        if dto.customer_id is not None and self.session.get(Customer, dto.customer_id) is None:
            raise BusinessRuleError("Cliente não encontrado.")

        items = [self._build_item(item) for item in dto.items]
        totals = calculate_totals(
            [item.unit_price_cents * item.quantity for item in items],
            dto.discount_cents,
            dto.delivery_fee_cents,
        )
        order = Order(
            created_by=dto.created_by,
            order_type=dto.order_type,
            status="received",
            customer_id=dto.customer_id,
            address_id=dto.address_id,
            customer_name=dto.customer_name,
            customer_phone=dto.customer_phone,
            delivery_address=dto.delivery_address if dto.order_type == "delivery" else None,
            subtotal_cents=totals.subtotal_cents,
            discount_cents=totals.discount_cents,
            delivery_fee_cents=totals.delivery_fee_cents,
            total_cents=totals.total_cents,
            payment_method=dto.payment_method,
            notes=dto.notes,
            items=items,
        )
        self.session.add(order)
        self.session.flush()
        logger.info("Pedido criado: id=%s total=%s centavos", order.id, order.total_cents)
        return order

    def _get_active(self, model, entity_id: int | None, label: str):
        entity = self.session.get(model, entity_id)
        if entity is None or not entity.active:
            raise BusinessRuleError(f"{label} indisponível.")
        return entity

    def _build_item(self, dto: OrderItemIn) -> OrderItem:
        if dto.kind == "pizza":
            return self._build_pizza(dto)
        return self._build_product(dto)

    def _build_product(self, dto: OrderItemIn) -> OrderItem:
        product = self._get_active(Product, dto.product_id, "Produto")
        return OrderItem(
            item_type="product",
            product_id=product.id,
            name=product.name,
            quantity=dto.quantity,
            unit_price_cents=product.price_cents,
            notes=dto.notes,
        )

    def _build_pizza(self, dto: OrderItemIn) -> OrderItem:
        size = self._get_active(Size, dto.size_id, "Tamanho")
        flavors = [self._get_active(Flavor, flavor_id, "Pizza") for flavor_id in dto.flavor_ids]
        if len(flavors) > 1:
            for flavor in flavors:
                if not flavor.allows_half:
                    raise BusinessRuleError(f"A pizza '{flavor.name}' não aceita meio a meio.")
        if len(flavors) > size.max_flavors:
            raise BusinessRuleError(
                f"O tamanho {size.name} aceita no máximo {size.max_flavors} sabor(es)."
            )

        flavor_rows = []
        for flavor in flavors:
            price = next((p.price_cents for p in flavor.prices if p.size_id == size.id), None)
            if price is None:
                raise BusinessRuleError(
                    f"A pizza '{flavor.name}' não é vendida no tamanho {size.name}."
                )
            flavor_rows.append(
                OrderItemFlavor(flavor_id=flavor.id, name=flavor.name, price_cents=price)
            )

        additional_rows = []
        for additional_id in dto.additional_ids:
            additional = self._get_active(Additional, additional_id, "Adicional")
            additional_rows.append(
                OrderItemAdditional(
                    additional_id=additional.id,
                    name=additional.name,
                    price_cents=additional.price_cents,
                )
            )

        unit_price = pizza_unit_price(
            [row.price_cents for row in flavor_rows], self.half_rule
        ) + sum(row.price_cents for row in additional_rows)
        return OrderItem(
            item_type="pizza",
            size_id=size.id,
            name=f"Pizza {size.name}",
            quantity=dto.quantity,
            unit_price_cents=unit_price,
            notes=dto.notes,
            flavors=flavor_rows,
            additionals=additional_rows,
        )
