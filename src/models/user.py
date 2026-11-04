"""Usuários do sistema."""
from datetime import datetime

from sqlalchemy import CheckConstraint, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base
from src.models.constants import ROLES, in_list


class User(Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint(in_list("role", ROLES), name="role_valid"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20))
    active: Mapped[bool] = mapped_column(default=True, server_default="1")
    created_at: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
