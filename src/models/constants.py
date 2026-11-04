"""Valores permitidos (guardados em inglês no banco; a interface traduz)."""

ROLES = ("admin", "attendant")
ORDER_TYPES = ("counter", "delivery")
ORDER_STATUSES = ("received", "preparing", "ready", "delivered", "canceled")
PAYMENT_METHODS = ("cash", "pix", "credit_card", "debit_card")
ADDITIONAL_KINDS = ("crust", "extra")
ITEM_TYPES = ("pizza", "product")
MOVEMENT_TYPES = ("sale", "income", "expense")


def in_list(column: str, values: tuple[str, ...]) -> str:
    """Monta a expressão SQL: coluna IN ('a', 'b')."""
    items = ", ".join(f"'{v}'" for v in values)
    return f"{column} IN ({items})"
