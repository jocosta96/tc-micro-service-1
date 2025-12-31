from src.adapters.gateways.shared_base import Base

def test_shared_base_is_declarative():
    # The Base should be a SQLAlchemy declarative base
    assert hasattr(Base, 'metadata')
    assert callable(getattr(Base, 'metadata').create_all)
