from unittest.mock import patch, MagicMock
from src.config.aws_ssm import SSMParameterStore, set_aws_credentials, get_aws_credentials_status, clear_aws_credentials, get_ssm_client

def test_ssm_parameter_store_init_and_get_parameter():
    with patch('boto3.client') as mock_boto:
        mock_client = MagicMock()
        mock_boto.return_value = mock_client
        ssm = SSMParameterStore(region_name='us-east-1')
        mock_client.get_parameter.return_value = {'Parameter': {'Value': 'foo'}}
        assert ssm.get_parameter('param') == 'foo'

def test_set_and_clear_aws_credentials():
    assert set_aws_credentials('a', 'b', 'c') is True
    status = get_aws_credentials_status()
    assert status['credentials_set']
    clear_aws_credentials()
    status = get_aws_credentials_status()
    assert not status['credentials_set']

def test_get_ssm_client_returns_instance():
    client = get_ssm_client()
    assert isinstance(client, SSMParameterStore)
