from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

# Handle different database types
database_url = settings.DATABASE_URL

# Convert PostgreSQL URL to async version if needed
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")

# Create engine with appropriate configuration based on database type
if database_url.startswith("sqlite"):
    # SQLite doesn't support pool configuration
    engine = create_async_engine(
        database_url,
        echo=settings.DEBUG,
        pool_pre_ping=True
    )
else:
    # PostgreSQL and other databases with pool support
    engine = create_async_engine(
        database_url,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        pool_size=20,
        max_overflow=0
    )

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


async def get_db() -> AsyncSession:
    """Database dependency"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
