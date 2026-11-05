"""Schemas de validação do cardápio."""
from pydantic import field_validator

from src.models.constants import ADDITIONAL_KINDS
from src.schemas.base import Schema, check_price, check_text


class SizeIn(Schema):
    name: str
    slices: int = 8
    max_flavors: int = 1
    sort_order: int = 0

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return check_text(value, "nome do tamanho", 50)

    @field_validator("slices")
    @classmethod
    def validate_slices(cls, value: int) -> int:
        if not 1 <= value <= 24:
            raise ValueError("Número de fatias deve estar entre 1 e 24.")
        return value

    @field_validator("max_flavors")
    @classmethod
    def validate_max_flavors(cls, value: int) -> int:
        if not 1 <= value <= 4:
            raise ValueError("Máximo de sabores deve estar entre 1 e 4.")
        return value


class FlavorIn(Schema):
    name: str
    description: str | None = None
    prices: dict[int, int]  # id do tamanho -> preço em centavos

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return check_text(value, "nome do sabor", 120)

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        return check_text(value, "descrição", 300, required=False)

    @field_validator("prices")
    @classmethod
    def validate_prices(cls, value: dict[int, int]) -> dict[int, int]:
        if not value:
            raise ValueError("Informe o preço em pelo menos um tamanho.")
        for cents in value.values():
            check_price(cents, "Preço do sabor")
        return value


class ProductIn(Schema):
    category_id: int
    name: str
    description: str | None = None
    price_cents: int
    photo_path: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return check_text(value, "nome do produto", 120)

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        return check_text(value, "descrição", 300, required=False)

    @field_validator("price_cents")
    @classmethod
    def validate_price(cls, value: int) -> int:
        return check_price(value, "Preço do produto")

    @field_validator("photo_path")
    @classmethod
    def validate_photo(cls, value: str | None) -> str | None:
        return check_text(value, "caminho da foto", 255, required=False)


class AdditionalIn(Schema):
    name: str
    kind: str
    price_cents: int

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return check_text(value, "nome do adicional", 120)

    @field_validator("kind")
    @classmethod
    def validate_kind(cls, value: str) -> str:
        if value not in ADDITIONAL_KINDS:
            raise ValueError("Tipo de adicional inválido.")
        return value

    @field_validator("price_cents")
    @classmethod
    def validate_price(cls, value: int) -> int:
        return check_price(value, "Preço do adicional")
