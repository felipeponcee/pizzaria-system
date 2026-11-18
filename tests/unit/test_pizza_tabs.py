from types import SimpleNamespace

from src.ui.views.pizza_tabs import build_pizza_columns


def test_pizza_columns_have_one_price_column_per_size():
    sizes = [
        SimpleNamespace(name="Broto", slices=4, active=True),
        SimpleNamespace(name="Grande", slices=8, active=True),
    ]
    assert build_pizza_columns(sizes) == [
        ("Pizza", 200),
        ("Descrição", 220),
        ("Meio a meio", 100),
        ("Broto (4 fatias)", 140),
        ("Grande (8 fatias)", 140),
        ("Situação", 100),
    ]


def test_inactive_size_is_marked_in_the_columns():
    sizes = [SimpleNamespace(name="Gigante", slices=12, active=False)]
    assert build_pizza_columns(sizes)[3][0] == "Gigante (12 fatias) (inativo)"
