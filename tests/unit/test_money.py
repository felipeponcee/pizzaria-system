import pytest

from src.core.exceptions import ValidationError
from src.core.money import format_brl, parse_brl


@pytest.mark.parametrize(
    "text, expected",
    [
        ("45,90", 4590),
        ("R$ 45,90", 4590),
        ("1.234,56", 123456),
        ("45.90", 4590),
        ("45", 4500),
        ("45,9", 4590),
        ("0", 0),
    ],
)
def test_parse_brl(text, expected):
    assert parse_brl(text) == expected


@pytest.mark.parametrize("text", ["", "abc", "-5", "45,905", "1.234", "1e3"])
def test_parse_brl_rejects_invalid_values(text):
    with pytest.raises(ValidationError):
        parse_brl(text)


def test_format_brl():
    assert format_brl(4590) == "R$ 45,90"
    assert format_brl(123456) == "R$ 1.234,56"
    assert format_brl(0) == "R$ 0,00"
    assert format_brl(5) == "R$ 0,05"
