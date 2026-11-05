"""Base dos schemas de validação (Pydantic) e conversão de erros para o usuário."""
from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict
from pydantic import ValidationError as PydanticValidationError

from src.core.exceptions import ValidationError
from src.core.money import MAX_PRICE_CENTS, format_brl


class Schema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


S = TypeVar("S", bound=Schema)


def validate_or_raise(model_class: type[S], **data: Any) -> S:
    """Valida os dados; em caso de erro, levanta ValidationError com mensagem clara."""
    try:
        return model_class(**data)
    except PydanticValidationError as exc:
        first = exc.errors()[0]
        original = first.get("ctx", {}).get("error")
        if original is not None:
            raise ValidationError(str(original)) from exc
        raise ValidationError(f"Valor inválido no campo '{first['loc'][-1]}'.") from exc


def check_text(
    value: str | None, label: str, max_length: int, required: bool = True
) -> str | None:
    """Valida um texto. Texto vazio opcional vira None."""
    if not value:
        if required:
            raise ValueError(f"Campo obrigatório: {label}.")
        return None
    if len(value) > max_length:
        raise ValueError(f"{label.capitalize()}: máximo de {max_length} caracteres.")
    return value


def check_price(cents: int, label: str) -> int:
    if not 0 <= cents <= MAX_PRICE_CENTS:
        raise ValueError(f"{label} deve estar entre R$ 0,00 e {format_brl(MAX_PRICE_CENTS)}.")
    return cents
