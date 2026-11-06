import pytest

from src.core.exceptions import ValidationError
from src.ui.components.form_fields import Field, convert_value, format_initial


def test_required_text_cannot_be_empty():
    with pytest.raises(ValidationError) as error:
        convert_value(Field("name", "Nome"), "   ")
    assert "Nome" in str(error.value)


def test_optional_empty_text_becomes_none():
    assert convert_value(Field("d", "Descrição", required=False), "") is None


def test_text_is_stripped():
    assert convert_value(Field("name", "Nome"), "  Calabresa ") == "Calabresa"


def test_money_is_converted_to_cents():
    assert convert_value(Field("p", "Preço", kind="money"), "R$ 12,50") == 1250


def test_invalid_money_message_mentions_the_field():
    with pytest.raises(ValidationError) as error:
        convert_value(Field("p", "Preço", kind="money"), "abc")
    assert "Preço" in str(error.value)


def test_int_is_converted_and_invalid_int_is_rejected():
    field = Field("s", "Fatias", kind="int")
    assert convert_value(field, "8") == 8
    with pytest.raises(ValidationError):
        convert_value(field, "oito")


def test_initial_values_are_formatted_for_the_form():
    assert format_initial(Field("p", "Preço", kind="money"), 4590) == "45,90"
    assert format_initial(Field("n", "Nome"), None) == ""
    assert format_initial(Field("s", "Fatias", kind="int"), 8) == "8"
