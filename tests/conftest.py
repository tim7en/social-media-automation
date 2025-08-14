import pytest
import asyncio
import os
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator, Generator
import tempfile
import shutil

from src.main import app
from src.core.config import settings
from src.core.database import get_db
from src.models import Base


# Test database URL (use SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with dependency overrides"""
    
    def override_get_db():
        return test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # Clean up dependency overrides
    app.dependency_overrides.clear()


@pytest.fixture
def temp_content_dir():
    """Create temporary directory for content generation tests"""
    temp_dir = tempfile.mkdtemp()
    original_content_dir = settings.CONTENT_OUTPUT_DIR
    settings.CONTENT_OUTPUT_DIR = temp_dir
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)
    settings.CONTENT_OUTPUT_DIR = original_content_dir


@pytest.fixture
def mock_api_keys():
    """Mock API keys for testing"""
    test_keys = {
        "OPENAI_API_KEY": "test_openai_key",
        "ELEVENLABS_API_KEY": "test_elevenlabs_key", 
        "YOUTUBE_API_KEY": "test_youtube_key",
        "FACEBOOK_ACCESS_TOKEN": "test_facebook_token",
        "INSTAGRAM_ACCESS_TOKEN": "test_instagram_token",
        "ELEVENLABS_VOICE_ID": "test_voice_id"
    }
    
    # Store original values
    original_values = {}
    for key, value in test_keys.items():
        original_values[key] = getattr(settings, key, None)
        setattr(settings, key, value)
    
    yield test_keys
    
    # Restore original values
    for key, value in original_values.items():
        setattr(settings, key, value)


@pytest.fixture
def mock_user_token():
    """Mock user authentication token"""
    return "test_bearer_token"


@pytest.fixture
def sample_content_request():
    """Sample content generation request"""
    return {
        "title": "Test AI Content",
        "topic": "Testing AI content generation",
        "content_type": "video",
        "duration": 30,
        "style": "educational",
        "target_platforms": ["youtube", "instagram"],
        "project_id": 1
    }


@pytest.fixture
def sample_user_data():
    """Sample user registration data"""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123"
    }