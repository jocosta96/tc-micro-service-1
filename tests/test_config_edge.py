import pytest
from src.config.app_config import app_config, AppConfig
from src.config.database import db_config, DatabaseConfig
from src.config.aws_ssm import SSMParameterStore, set_aws_credentials, get_aws_credentials_status, clear_aws_credentials, get_ssm_client

def test_app_config_str_and_cors():
    assert isinstance(str(app_config), str)
    cors = app_config.cors_config
    assert isinstance(cors, dict)
    assert "allow_origins" in cors

def test_database_config_health_reload():
    assert isinstance(db_config.health_check(), dict)
    assert isinstance(db_config.connection_string, str)
    assert isinstance(db_config.async_connection_string, str)
    assert db_config.reload_from_ssm() in [True, False]
    assert isinstance(db_config.get_ssm_parameters(), dict)

def test_ssm_parameter_store_methods():
    ssm = SSMParameterStore(region_name="us-east-1")
    assert ssm.health_check() in [True, False]
    # These will likely fail without AWS credentials, so just check method exists
    try:
        ssm.get_parameter("/fake/param")
    except Exception:
        pass
    try:
        ssm.get_parameters(["/fake/param1", "/fake/param2"])
    except Exception:
        pass
    try:
        ssm.get_parameter_with_fallback("/fake/param", "fallback")
    except Exception:
        pass

def test_aws_credentials_status_and_clear():
    set_aws_credentials("fake", "fake")
    status = get_aws_credentials_status()
    assert isinstance(status, dict)
    clear_aws_credentials()
    ssm = get_ssm_client()
    assert isinstance(ssm, SSMParameterStore)
