from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.app_logs import configure_logging, LogLevels
from src.config.app_config import app_config
from src.adapters.routes.customer_routes import customer_router
from src.adapters.routes.health_routes import health_router
from src.adapters.routes.ingredient_routes import ingredient_router
from src.adapters.routes.product_routes import product_router

configure_logging(LogLevels.info.value)


def create_application() -> FastAPI:
    app = FastAPI(
        title=app_config.api_title,
        version=app_config.api_version,
        description=app_config.api_description,
        prefix=app_config.api_prefix,
    )

    app.add_middleware(CORSMiddleware, **app_config.cors_config)
    app.include_router(router=health_router)
    app.include_router(router=customer_router)
    app.include_router(router=ingredient_router)
    app.include_router(router=product_router)
    return app


app = create_application()
