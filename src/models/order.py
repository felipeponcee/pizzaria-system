"""Pedidos e itens. Valores e nomes são copiados (snapshot) no momento da venda."""
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.constants import ITEM_TYPES, ORDER_STATUSES, ORDER_TYPES, PAYMENT_METHODS, in_list


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint(in_list("order_type", ORDER_TYPES), name="type_valid"),
        CheckConstraint(in_list("status", ORDER_STATUSES), name="status_valid"),
        CheckConstraint(
            "payment_method IS NULL OR " + in_list("payment_method", PAYMENT_METHODS),
            name="payment_valid",
        ),
        CheckConstraint(
            "subtotal_cents >= 0 AND discount_cents >= 0 "
            "AND delivery_fee_cents >= 0 AND total_cents >= 0",
            name="amounts_positive",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id", ondelete="SET NULL"))
    address_id: Mapped[int | None] = mapped_column(ForeignKey("addresses.id", ondelete="SET NULL"))
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    order_type: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(
        String(20), default="received", server_default="received", index=True
    )
    customer_name: Mapped[str | None] = mapped_column(String(120))
    customer_phone: Mapped[str | None] = mapped_column(String(20))
    delivery_address: Mapped[str | None] = mapped_column(String(400))
    subtotal_cents: Mapped[int] = mapped_column()
    discount_cents: Mapped[int] = mapped_column(default=0, server_default="0")
    delivery_fee_cents: Mapped[int] = mapped_column(default=0, server_default="0")
    total_cents: Mapped[int] = mapped_column()
    payment_method: Mapped[str | None] = mapped_column(String(20))
    notes: Mapped[str | None] = mapped_column(String(500))
    cancel_reason: Mapped[str | None] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.current_timestamp(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.current_timestamp(), onupdate=func.current_timestamp()
    )

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    """unit_price_cents é o preço final de 1 unidade (sabores + adicionais já somados)."""

    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint(in_list("item_type", ITEM_TYPES), name="type_valid"),
        CheckConstraint("quantity > 0", name="quantity_positive"),
        CheckConstraint("unit_price_cents >= 0", name="price_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    item_type: Mapped[str] = mapped_column(String(20))
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id", ondelete="SET NULL"))
    size_id: Mapped[int | None] = mapped_column(ForeignKey("sizes.id", ondelete="SET NULL"))
    name: Mapped[str] = mapped_column(String(200))
    quantity: Mapped[int] = mapped_column()
    unit_price_cents: Mapped[int] = mapped_column()
    notes: Mapped[str | None] = mapped_column(String(300))

    order: Mapped["Order"] = relationship(back_populates="items")
    flavors: Mapped[list["OrderItemFlavor"]] = relationship(
        back_populates="item", cascade="all, delete-orphan"
    )
    additionals: Mapped[list["OrderItemAdditional"]] = relationship(
        back_populates="item", cascade="all, delete-orphan"
    )


class OrderItemFlavor(Base):
    __tablename__ = "order_item_flavors"
    __table_args__ = (CheckConstraint("price_cents >= 0", name="price_positive"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    order_item_id: Mapped[int] = mapped_column(
        ForeignKey("order_items.id", ondelete="CASCADE"), index=True
    )
    flavor_id: Mapped[int | None] = mapped_column(ForeignKey("flavors.id", ondelete="SET NULL"))
    name: Mapped[str] = mapped_column(String(120))
    price_cents: Mapped[int] = mapped_column()

    item: Mapped["OrderItem"] = relationship(back_populates="flavors")


class OrderItemAdditional(Base):
    __tablename__ = "order_item_additionals"
    __table_args__ = (CheckConstraint("price_cents >= 0", name="price_positive"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    order_item_id: Mapped[int] = mapped_column(
        ForeignKey("order_items.id", ondelete="CASCADE"), index=True
    )
    additional_id: Mapped[int | None] = mapped_column(
        ForeignKey("additionals.id", ondelete="SET NULL")
    )
    name: Mapped[str] = mapped_column(String(120))
    price_cents: Mapped[int] = mapped_column()

    item: Mapped["OrderItem"] = relationship(back_populates="additionals")
