from src.app.config import APP_NAME, get_data_dir


def test_data_dir_is_created():
    path = get_data_dir()
    assert path.exists()
    assert path.name == APP_NAME