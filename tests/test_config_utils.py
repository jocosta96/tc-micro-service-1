from src.config.app_config import app_config
from src.config.database import db_config

def test_app_config_str_and_cors():
    s = str(app_config)
    assert 'AppConfig' in s
    cors = app_config.cors_config
    assert 'allow_origins' in cors
    assert isinstance(cors['allow_methods'], list)

def test_database_config_str_and_connection_strings():
    s = str(db_config)
    assert 'DatabaseConfig' in s
    conn = db_config.connection_string
    async_conn = db_config.async_connection_string
    assert 'postgresql' in conn
    assert 'asyncpg' in async_conn
