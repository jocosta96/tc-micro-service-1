import pytest
from src.application.exceptions import (
    ApplicationException,
    CustomerNotFoundException,
    CustomerAlreadyExistsException,
    CustomerValidationException,
    CustomerBusinessRuleException,
)

def test_application_exceptions():
    for exc in [
        ApplicationException,
        CustomerNotFoundException,
        CustomerAlreadyExistsException,
        CustomerValidationException,
        CustomerBusinessRuleException,
    ]:
        with pytest.raises(exc):
            raise exc("error")
