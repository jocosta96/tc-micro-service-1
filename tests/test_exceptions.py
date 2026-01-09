import pytest
from src.application import exceptions

def test_application_exceptions_instantiation():
    # Test all custom exceptions can be instantiated and raised
    exception_classes = [
        exceptions.ApplicationException,
        exceptions.CustomerNotFoundException,
        exceptions.CustomerAlreadyExistsException,
        exceptions.CustomerValidationException,
        exceptions.CustomerBusinessRuleException,
        exceptions.CustomerOperationException,
        exceptions.AuthenticationException,
        exceptions.AuthorizationException,
        exceptions.DatabaseException,
        exceptions.IngredientNotFoundException,
        exceptions.IngredientAlreadyExistsException,
        exceptions.IngredientValidationException,
        exceptions.IngredientBusinessRuleException,
        exceptions.ProductNotFoundException,
        exceptions.ProductAlreadyExistsException,
        exceptions.ProductValidationException,
        exceptions.ProductBusinessRuleException,
    ]
    for exc in exception_classes:
        with pytest.raises(exc):
            raise exc("test error")
