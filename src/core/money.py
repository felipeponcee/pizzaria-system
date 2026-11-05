"""Conversão entre texto em reais (R$) e centavos inteiros."""
import re

from src.core.exceptions import ValidationError

MAX_PRICE_CENTS = 1_000_000  # R$ 10.000,00


def parse_brl(text: str) -> int:
    """Converte '45,90', 'R$ 1.234,56' ou '45.90' em centavos (ex.: 4590)."""
    cleaned = re.sub(r"[Rr]\$|\s", "", text or "")
    if not cleaned:
        raise ValidationError("Informe um valor.")
    if "," in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    match = re.fullmatch(r"(\d+)(?:\.(\d{1,2}))?", cleaned)
    if not match:
        raise ValidationError("Valor inválido. Use o formato 45,90.")
    reais = int(match.group(1))
    centavos = int((match.group(2) or "0").ljust(2, "0"))
    return reais * 100 + centavos


def format_brl(cents: int) -> str:
    """Formata centavos como moeda brasileira (ex.: 4590 -> 'R$ 45,90')."""
    sign = "-" if cents < 0 else ""
    reais, centavos = divmod(abs(cents), 100)
    return f"{sign}R$ {reais:,}".replace(",", ".") + f",{centavos:02d}"
