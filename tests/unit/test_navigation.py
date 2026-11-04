from src.models.constants import ORDER_STATUSES
from src.ui import theme
from src.ui.navigation import NAV_ITEMS
from src.ui.views.base_view import BaseView


def test_navigation_keys_are_unique():
    keys = [key for key, _label, _view in NAV_ITEMS]
    assert len(keys) == len(set(keys))


def test_navigation_views_extend_base_view():
    assert all(issubclass(view, BaseView) for _key, _label, view in NAV_ITEMS)


def test_every_order_status_has_label_and_color():
    for status in ORDER_STATUSES:
        assert status in theme.STATUS_LABELS
        assert status in theme.STATUS_COLORS
