"""Schemas de validação do pedido."""
from pydantic import field_validator, model_validator

from src.models.constants import ITEM_TYPES, ORDER_TYPES, PAYMENT_METHODS
from src.schemas.base import Schema, check_price, check_text


class OrderItemIn(Schema):
    kind: str  # "pizza" ou "product"
    quantity: int = 1
    notes: str | None = None
    # pizza
    size_id: int | None = None
    flavor_ids: list[int] = []
    additional_ids: list[int] = []
    # produto de preço fixo (bebida, sobremesa, combo)
    product_id: int | None = None

    @field_validator("kind")
    @classmethod
    def validate_kind(cls, value: str) -> str:
        if value not in ITEM_TYPES:
            raise ValueError("Tipo de item inválido.")
        return value

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, value: int) -> int:
        if not 1 <= value <= 99:
            raise ValueError("A quantidade deve estar entre 1 e 99.")
        return value

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, value: str | None) -> str | None:
        return check_text(value, "observações do item", 300, required=False)

    @model_validator(mode="after")
    def validate_by_kind(self) -> "OrderItemIn":
        if self.kind == "pizza":
            if self.size_id is None:
                raise ValueError("Escolha o tamanho da pizza.")
            if not self.flavor_ids:
                raise ValueError("Escolha pelo menos uma pizza.")
            if len(set(self.flavor_ids)) != len(self.flavor_ids):
                raise ValueError("Escolha pizzas diferentes no meio a meio.")
            if len(set(self.additional_ids)) != len(self.additional_ids):
                raise ValueError("Adicional repetido no mesmo item.")
            if self.product_id is not None:
                raise ValueError("Pizza não aceita produto.")
        else:
            if self.product_id is None:
                raise ValueError("Escolha o produto.")
            if self.size_id is not None or self.flavor_ids or self.additional_ids:
                raise ValueError("Produto não aceita tamanho, sabores ou adicionais.")
        return self


class OrderIn(Schema):
    created_by: int
    order_type: str
    items: list[OrderItemIn]
    customer_id: int | None = None
    address_id: int | None = None
    customer_name: str | None = None
    customer_phone: str | None = None
    delivery_address: str | None = None
    discount_cents: int = 0
    delivery_fee_cents: int = 0
    payment_method: str | None = None
    notes: str | None = None

    @field_validator("order_type")
    @classmethod
    def validate_order_type(cls, value: str) -> str:
        if value not in ORDER_TYPES:
            raise ValueError("Tipo de pedido inválido.")
        return value

    @field_validator("items")
    @classmethod
    def validate_items(cls, value: list[OrderItemIn]) -> list[OrderItemIn]:
        if not value:
            raise ValueError("Adicione pelo menos um item ao pedido.")
        if len(value) > 50:
            raise ValueError("Um pedido pode ter no máximo 50 itens.")
        return value

    @field_validator("customer_name")
    @classmethod
    def validate_customer_name(cls, value: str | None) -> str | None:
        return check_text(value, "nome do cliente", 120, required=False)

    @field_validator("customer_phone")
    @classmethod
    def validate_customer_phone(cls, value: str | None) -> str | None:
        return check_text(value, "telefone do cliente", 20, required=False)

    @field_validator("delivery_address")
    @classmethod
    def validate_delivery_address(cls, value: str | None) -> str | None:
        return check_text(value, "endereço de entrega", 400, required=False)

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, value: str | None) -> str | None:
        return check_text(value, "observações do pedido", 500, required=False)

    @field_validator("discount_cents")
    @classmethod
    def validate_discount(cls, value: int) -> int:
        return check_price(value, "Desconto")

    @field_validator("delivery_fee_cents")
    @classmethod
    def validate_delivery_fee(cls, value: int) -> int:
        return check_price(value, "Taxa de entrega")

    @field_validator("payment_method")
    @classmethod
    def validate_payment_method(cls, value: str | None) -> str | None:
        if value is not None and value not in PAYMENT_METHODS:
            raise ValueError("Forma de pagamento inválida.")
        return value

    @model_validator(mode="after")
    def validate_by_type(self) -> "OrderIn":
        if self.order_type == "delivery":
            if not self.customer_name:
                raise ValueError("Informe o nome do cliente para a entrega.")
            if not self.customer_phone:
                raise ValueError("Informe o telefone do cliente para a entrega.")
            if not self.delivery_address:
                raise ValueError("Informe o endereço de entrega.")
        elif self.delivery_fee_cents > 0:
            raise ValueError("Pedido de balcão não tem taxa de entrega.")
        return self
