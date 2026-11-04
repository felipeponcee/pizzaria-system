"""Caixa: sessões (abertura/fechamento) e movimentações."""
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base
from src.models.constants import MOVEMENT_TYPES, in_list


class CashierSession(Base):
    __tablename__ = "cashier_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    opened_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    closed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    opened_at: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    closed_at: Mapped[datetime | None] = mapped_column()
    opening_cents: Mapped[int] = mapped_column(default=0, server_default="0")
    closing_cents: Mapped[int | None] = mapped_column()
    notes: Mapped[str | None] = mapped_column(String(500))


class CashierMovement(Base):
    """amount_cents é sempre positivo; o sinal vem de movement_type."""

    __tablename__ = "cashier_movements"
    __table_args__ = (
        CheckConstraint(in_list("movement_type", MOVEMENT_TYPES), name="type_valid"),
        CheckConstraint("amount_cents > 0", name="amount_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("cashier_sessions.id"), index=True)
    order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id", ondelete="SET NULL"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    movement_type: Mapped[str] = mapped_column(String(20))
    amount_cents: Mapped[int] = mapped_column()
    description: Mapped[str | None] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
