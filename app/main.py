from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .core.config import settings
from .core.exceptions import ServiceError
from .api.repository_routes import router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="GitHub Repository Bridge API")
    app.include_router(router)

    @app.exception_handler(ServiceError)
    async def service_error_handler(request, exc: ServiceError):
        """Convert service-level errors into JSON HTTP responses."""
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return app


app = create_app()
