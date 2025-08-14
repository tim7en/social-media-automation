"""
Test utilities and fixtures for the social media automation platform.
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient
import redis.asyncio as redis

from src.main import app
from src.core.database import get_db, Base
from src.core.config import settings
from src.utils.performance import init_performance_utils


# Test database URL (use in-memory SQLite for fast tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True
)

# Test session maker
TestingSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def client(db_session: AsyncSession) -> Generator:
    """Create a test client with database dependency override."""
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client."""
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def redis_client() -> AsyncGenerator[redis.Redis, None]:
    """Create a Redis client for testing."""
    client = redis.from_url("redis://localhost:6379/1")  # Use different DB for tests
    try:
        await client.ping()
        yield client
    except redis.ConnectionError:
        pytest.skip("Redis not available for testing")
    finally:
        await client.flushdb()  # Clean up test data
        await client.close()


@pytest.fixture
def sample_content_data() -> dict:
    """Sample content generation request data."""
    return {
        "title": "Test Content Title",
        "topic": "This is a test content topic for automated testing",
        "content_type": "video",
        "duration": 60,
        "style": "educational",
        "target_platforms": ["youtube", "instagram"],
        "project_id": 1
    }


@pytest.fixture
def sample_user_data() -> dict:
    """Sample user registration data."""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
        "terms_accepted": True
    }


@pytest.fixture
def sample_project_data() -> dict:
    """Sample project creation data."""
    return {
        "name": "Test Project",
        "description": "A test project for automated testing",
        "target_audience": "Tech enthusiasts",
        "content_themes": ["technology", "AI", "automation"],
        "brand_guidelines": {
            "tone": "professional",
            "colors": ["#FF0000", "#00FF00"],
            "fonts": ["Arial", "Helvetica"]
        }
    }


class MockAIService:
    """Mock AI service for testing without API calls."""
    
    async def generate_content(self, prompt: str, **kwargs) -> str:
        return f"Generated content for: {prompt}"
    
    async def generate_voice(self, text: str, voice_id: str = None) -> bytes:
        return b"mock_audio_data"
    
    async def analyze_sentiment(self, text: str) -> dict:
        return {
            "sentiment": "positive",
            "confidence": 0.95,
            "emotions": ["joy", "excitement"]
        }


@pytest.fixture
def mock_ai_service() -> MockAIService:
    """Provide mock AI service for testing."""
    return MockAIService()


class MockSocialMediaAPI:
    """Mock social media API for testing without real API calls."""
    
    def __init__(self, platform: str):
        self.platform = platform
        self.posts = []
    
    async def post_content(self, content: dict) -> dict:
        post_id = f"mock_{self.platform}_{len(self.posts)}"
        post = {
            "id": post_id,
            "platform": self.platform,
            "status": "published",
            "url": f"https://{self.platform}.com/post/{post_id}",
            **content
        }
        self.posts.append(post)
        return post
    
    async def get_analytics(self, post_id: str) -> dict:
        return {
            "post_id": post_id,
            "views": 1000,
            "likes": 50,
            "shares": 10,
            "comments": 5,
            "engagement_rate": 6.5
        }


@pytest.fixture
def mock_social_apis() -> dict:
    """Provide mock social media APIs for testing."""
    return {
        "youtube": MockSocialMediaAPI("youtube"),
        "instagram": MockSocialMediaAPI("instagram"),
        "facebook": MockSocialMediaAPI("facebook"),
        "tiktok": MockSocialMediaAPI("tiktok")
    }


# Test utilities
def assert_response_structure(response_data: dict, required_fields: list):
    """Assert that response has required structure."""
    assert isinstance(response_data, dict)
    for field in required_fields:
        assert field in response_data, f"Missing required field: {field}"


def assert_error_response(response_data: dict):
    """Assert that response is a properly formatted error."""
    required_fields = ["success", "error", "timestamp"]
    assert_response_structure(response_data, required_fields)
    assert response_data["success"] is False
    assert "code" in response_data["error"]
    assert "message" in response_data["error"]


def assert_success_response(response_data: dict, data_fields: list = None):
    """Assert that response is a properly formatted success response."""
    assert isinstance(response_data, dict)
    if "success" in response_data:
        assert response_data["success"] is True
    
    if data_fields:
        for field in data_fields:
            assert field in response_data, f"Missing required data field: {field}"


async def create_test_user(db: AsyncSession, user_data: dict = None) -> dict:
    """Create a test user in the database."""
    from src.services.auth_service import AuthService
    
    if not user_data:
        user_data = {
            "email": "test@example.com",
            "password": "TestPassword123!",
            "full_name": "Test User"
        }
    
    auth_service = AuthService(db)
    user = await auth_service.create_user(**user_data)
    return user


async def create_test_project(db: AsyncSession, user_id: int, project_data: dict = None) -> dict:
    """Create a test project in the database."""
    # This would depend on your project service implementation
    if not project_data:
        project_data = {
            "name": "Test Project",
            "description": "A test project",
            "user_id": user_id
        }
    
    # Mock implementation - replace with actual project service
    return {"id": 1, **project_data}


# Performance test utilities
class PerformanceTestRunner:
    """Utility for running performance tests."""
    
    def __init__(self, client: AsyncClient):
        self.client = client
        self.results = []
    
    async def run_concurrent_requests(self, endpoint: str, payload: dict = None, count: int = 10):
        """Run multiple concurrent requests and measure performance."""
        import time
        
        async def make_request():
            start = time.time()
            if payload:
                response = await self.client.post(endpoint, json=payload)
            else:
                response = await self.client.get(endpoint)
            end = time.time()
            
            return {
                "status_code": response.status_code,
                "response_time_ms": (end - start) * 1000,
                "success": 200 <= response.status_code < 300
            }
        
        tasks = [make_request() for _ in range(count)]
        results = await asyncio.gather(*tasks)
        
        self.results.extend(results)
        return results
    
    def get_performance_summary(self) -> dict:
        """Get summary of performance test results."""
        if not self.results:
            return {}
        
        response_times = [r["response_time_ms"] for r in self.results]
        success_count = sum(1 for r in self.results if r["success"])
        
        return {
            "total_requests": len(self.results),
            "successful_requests": success_count,
            "success_rate_percent": (success_count / len(self.results)) * 100,
            "avg_response_time_ms": sum(response_times) / len(response_times),
            "min_response_time_ms": min(response_times),
            "max_response_time_ms": max(response_times),
            "p95_response_time_ms": sorted(response_times)[int(len(response_times) * 0.95)]
        }


@pytest.fixture
def performance_runner(async_client: AsyncClient) -> PerformanceTestRunner:
    """Provide performance test runner."""
    return PerformanceTestRunner(async_client)


# Custom pytest markers
pytest_plugins = []

def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )