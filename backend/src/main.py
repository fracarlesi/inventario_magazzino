"""FastAPI application setup with CORS middleware and exception handlers."""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from src.api.errors import InventoryException
from src.db.database import close_db, init_db
from src.models.schemas import ErrorResponse

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    # Note: In production with Alembic, we don't call init_db()
    # Tables are created via migrations
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title=os.getenv("APP_NAME", "Warehouse Inventory Management API"),
    version=os.getenv("API_VERSION", "1.0.0"),
    description="Sistema di gestione inventario magazzino officina auto",
    debug=os.getenv("DEBUG", "false").lower() == "true",
    lifespan=lifespan,
)

# CORS middleware configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers for custom errors
@app.exception_handler(InventoryException)
async def inventory_exception_handler(request: Request, exc: InventoryException) -> JSONResponse:
    """Handle custom inventory exceptions with Italian error messages."""
    # Map error codes to HTTP status codes
    status_code_map = {
        "ITEM_NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "INSUFFICIENT_STOCK": status.HTTP_409_CONFLICT,
        "VALIDATION_ERROR": status.HTTP_400_BAD_REQUEST,
        "DUPLICATE_ITEM_NAME": status.HTTP_409_CONFLICT,
        "ITEM_HAS_MOVEMENTS": status.HTTP_409_CONFLICT,
        "ITEM_HAS_STOCK": status.HTTP_409_CONFLICT,
        "CONFIRMATION_REQUIRED": status.HTTP_400_BAD_REQUEST,
        "ADJUSTMENT_NOT_NEEDED": status.HTTP_400_BAD_REQUEST,
        "INVALID_DATE_RANGE": status.HTTP_400_BAD_REQUEST,
    }

    status_code = status_code_map.get(exc.error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            detail=exc.detail,
            error_code=exc.error_code,
            context=exc.context
        ).model_dump()
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring and UptimeRobot."""
    return {
        "status": "ok",
        "app": os.getenv("APP_NAME", "Warehouse Inventory Management API"),
        "version": os.getenv("API_VERSION", "1.0.0")
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Warehouse Inventory Management API",
        "docs": "/docs",
        "health": "/health"
    }


# Import and register API routers
from src.api.items import router as items_router
from src.api.dashboard import router as dashboard_router
from src.api.movements import router as movements_router
from src.api.export import router as export_router

app.include_router(items_router, prefix="/api", tags=["Items"])
app.include_router(dashboard_router, prefix="/api", tags=["Dashboard"])
app.include_router(movements_router, prefix="/api", tags=["Movements"])
app.include_router(export_router, prefix="/api", tags=["Export"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("RELOAD", "true").lower() == "true"
    )
