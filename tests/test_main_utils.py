from src.main import create_application

def test_create_application():
    app = create_application()
    assert hasattr(app, 'include_router')
    assert hasattr(app, 'middleware_stack')
