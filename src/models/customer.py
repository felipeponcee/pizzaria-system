"""Clientes e endereços de entrega."""
from datetime import datetime

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str] = mapped_column(String(20), index=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())

    addresses: Mapped[list["Address"]] = relationship(
        back_populates="customer", cascade="all, delete-orphan"
    )


class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"), index=True
    )
    street: Mapped[str] = mapped_column(String(200))
    number: Mapped[str] = mapped_column(String(20))
    neighborhood: Mapped[str] = mapped_column(String(100))
    city: Mapped[str] = mapped_column(String(100))
    reference: Mapped[str | None] = mapped_column(String(200))
    is_default: Mapped[bool] = mapped_column(default=False, server_default="0")

    customer: Mapped["Customer"] = relationship(back_populates="addresses")
