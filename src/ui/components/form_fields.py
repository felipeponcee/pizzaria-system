"""Definição dos campos de formulário e conversão dos valores digitados.

Não depende de widgets, então pode ser testado sem abrir janelas.
"""
from dataclasses import dataclass

from src.core.exceptions import ValidationError
from src.core.money import parse_brl


@dataclass
class Field:
    key: str
    label: str
    kind: str = "text"  # text | money | int | choice
    required: bool = True
    choices: list[str] | None = None
    help: str | None = None


def convert_value(field: Field, raw: str):
    """Converte o texto digitado: dinheiro vira centavos, inteiro vira int."""
    text = (raw or "").strip()
    if not text:
        if field.required:
            raise ValidationError(f"Preencha o campo '{field.label}'.")
        return None
    if field.kind == "money":
        try:
            return parse_brl(text)
        except ValidationError as exc:
            raise ValidationError(f"{field.label}: {exc}") from None
    if field.kind == "int":
        try:
            return int(text)
        except ValueError:
            raise ValidationError(
                f"O campo '{field.label}' deve ser um número inteiro."
            ) from None
    return text


def format_initial(field: Field, value) -> str:
    """Texto que aparece no campo ao editar (dinheiro mostra 45,90)."""
    if value is None:
        return ""
    if field.kind == "money":
        return f"{value // 100},{value % 100:02d}"
    return str(value)
