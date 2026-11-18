from src.services.catalog_service import SizeService, ensure_default_sizes


def test_missing_default_size_is_added(session):
    SizeService(session).create(name="Grande", slices=8, max_flavors=2, sort_order=2)
    ensure_default_sizes(session)
    sizes = SizeService(session).list_all()
    assert [(size.name, size.slices) for size in sizes] == [("Broto", 4), ("Grande", 8)]


def test_default_sizes_are_not_duplicated(session):
    ensure_default_sizes(session)
    ensure_default_sizes(session)
    assert len(SizeService(session).list_all(include_inactive=True)) == 2
