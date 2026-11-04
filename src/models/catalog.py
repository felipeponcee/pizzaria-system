"""Cardápio: categorias, produtos de preço fixo, tamanhos, sabores e adicionais."""
from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.constants import ADDITIONAL_KINDS, in_list


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)


class Product(Base):
    """Item de preço fixo: bebida, sobremesa, combo."""

    __tablename__ = "products"
    __table_args__ = (CheckConstraint("price_cents >= 0", name="price_positive"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(String(300))
    price_cents: Mapped[int] = mapped_column()
    photo_path: Mapped[str | None] = mapped_column(String(255))
    active: Mapped[bool] = mapped_column(default=True, server_default="1")


class Size(Base):
    """Tamanho de pizza (Pequena, Média, Grande...)."""

    __tablename__ = "sizes"
    __table_args__ = (CheckConstraint("max_flavors >= 1", name="flavors_positive"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    max_flavors: Mapped[int] = mapped_column(default=1, server_default="1")
    slices: Mapped[int] = mapped_column(default=8, server_default="8")
    sort_order: Mapped[int] = mapped_column(default=0, server_default="0")
    active: Mapped[bool] = mapped_column(default=True, server_default="1")


class Flavor(Base):
    __tablename__ = "flavors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    description: Mapped[str | None] = mapped_column(String(300))
    active: Mapped[bool] = mapped_column(default=True, server_default="1")

    prices: Mapped[list["FlavorPrice"]] = relationship(
        back_populates="flavor", cascade="all, delete-orphan"
    )


class FlavorPrice(Base):
    """Preço de um sabor em um tamanho específico."""

    __tablename__ = "flavor_prices"
    __table_args__ = (
        UniqueConstraint("flavor_id", "size_id"),
        CheckConstraint("price_cents >= 0", name="price_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    flavor_id: Mapped[int] = mapped_column(ForeignKey("flavors.id", ondelete="CASCADE"))
    size_id: Mapped[int] = mapped_column(ForeignKey("sizes.id", ondelete="CASCADE"))
    price_cents: Mapped[int] = mapped_column()

    flavor: Mapped["Flavor"] = relationship(back_populates="prices")


class Additional(Base):
    """Borda recheada ou adicional (queijo extra, bacon...)."""

    __tablename__ = "additionals"
    __table_args__ = (
        CheckConstraint(in_list("kind", ADDITIONAL_KINDS), name="kind_valid"),
        CheckConstraint("price_cents >= 0", name="price_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    kind: Mapped[str] = mapped_column(String(20))
    price_cents: Mapped[int] = mapped_column()
    active: Mapped[bool] = mapped_column(default=True, server_default="1")
