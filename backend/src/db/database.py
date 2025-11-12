"""
Database configuration and session management.

CRITICAL: Uses Neon pooled endpoint (.pooler.neon.tech) with NullPool
to prevent connection exhaustion on serverless deployments.
"""
import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

load_dotenv()

# CRITICAL: Use pooled endpoint URL from environment
# Format: postgresql://user:pass@ep-xxx.pooler.neon.tech:5432/dbname?sslmode=require
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is required. "
        "IMPORTANT: Use Neon pooled endpoint (.pooler.neon.tech) not direct endpoint."
    )

# Verify pooled endpoint is being used
if ".pooler." not in DATABASE_URL:
    import warnings
    warnings.warn(
        "WARNING: DATABASE_URL does not contain '.pooler.' subdomain. "
        "For serverless deployments, use Neon pooled endpoint to prevent "
        "connection exhaustion. See quickstart.md for details.",
        stacklevel=2
    )

# Convert postgresql:// to postgresql+asyncpg:// for async support
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# asyncpg doesn't support sslmode parameter - use ssl=require instead
# Replace ?sslmode=require with ?ssl=require or &sslmode=require with &ssl=require
DATABASE_URL = DATABASE_URL.replace("?sslmode=require", "?ssl=require")
DATABASE_URL = DATABASE_URL.replace("&sslmode=require", "&ssl=require")
DATABASE_URL = DATABASE_URL.replace("?sslmode=disable", "")
DATABASE_URL = DATABASE_URL.replace("&sslmode=disable", "")

# Create async engine with NullPool (let Neon pgBouncer handle pooling)
engine = create_async_engine(
    DATABASE_URL,
    poolclass=NullPool,  # CRITICAL: No local pooling, use Neon's pgBouncer
    echo=os.getenv("DEBUG", "false").lower() == "true",  # SQL logging in debug mode
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Declarative base for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.

    Usage:
        @app.get("/api/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables (for development/testing)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections."""
    await engine.dispose()
