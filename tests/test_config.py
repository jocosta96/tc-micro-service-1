from src.config.app_config import app_config, AppConfig
from src.config.database import db_config, DatabaseConfig

def test_app_config_properties():
    assert isinstance(app_config.api_prefix, str)
    assert isinstance(app_config.allowed_origins, list)
    assert isinstance(app_config.cors_config, dict)
    assert 'allow_origins' in app_config.cors_config
    assert str(app_config).startswith('AppConfig')

def test_database_config_properties():
    assert isinstance(db_config.host, str)
    assert isinstance(db_config.port, int)
    assert isinstance(db_config.connection_string, str)
    assert isinstance(db_config.async_connection_string, str)
    assert 'postgresql' in db_config.connection_string
    assert str(db_config).startswith('DatabaseConfig')

def test_database_config_health_check():
    health = db_config.health_check()
    assert 'ssm_enabled' in health
    assert 'configuration_source' in health

def test_database_config_get_ssm_parameters():
    params = db_config.get_ssm_parameters()
    assert isinstance(params, dict)
    assert 'host' in params
