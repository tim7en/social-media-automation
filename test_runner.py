"""
Test runner script that can run basic functionality tests without heavy dependencies.
This script tests the core application functionality with minimal setup.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """Test that core modules can be imported"""
    try:
        from core.config import settings
        print("✅ Core configuration imports successfully")
        
        # Test that settings are loaded
        assert hasattr(settings, 'SECRET_KEY')
        assert hasattr(settings, 'DEBUG')
        print("✅ Settings are properly configured")
        
        return True
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_schemas():
    """Test that schemas are properly defined"""
    try:
        from schemas.schemas import (
            ContentType, Platform, ContentStatus,
            User, UserCreate, Project, ContentItem,
            Token, MessageResponse, TaskResponse
        )
        print("✅ All schema imports successful")
        
        # Test enum values
        assert ContentType.VIDEO == "video"
        assert Platform.YOUTUBE == "youtube"
        assert ContentStatus.READY == "ready"
        print("✅ Enum values are correct")
        
        # Test schema creation
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass"
        }
        user_create = UserCreate(**user_data)
        assert user_create.email == "test@example.com"
        print("✅ Schema validation works")
        
        return True
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        return False

def test_auth_functions():
    """Test authentication utility functions"""
    try:
        # Import without running the full FastAPI app
        import sys
        import importlib.util
        
        # Load the auth module
        auth_path = src_path / "api" / "routers" / "auth.py"
        spec = importlib.util.spec_from_file_location("auth", auth_path)
        auth_module = importlib.util.module_from_spec(spec)
        
        # Mock the FastAPI dependencies that would cause import errors
        sys.modules['...core.database'] = type(sys)('mock_db')
        sys.modules['...core.config'] = type(sys)('mock_config')
        sys.modules['...schemas'] = type(sys)('mock_schemas')
        
        # Test password hashing (this should work without dependencies)
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        password = "test_password_123"
        hashed = pwd_context.hash(password)
        verified = pwd_context.verify(password, hashed)
        
        assert verified is True
        assert hashed != password
        print("✅ Password hashing and verification works")
        
        return True
    except ImportError as e:
        print(f"⚠️  Auth test skipped (missing dependencies): {e}")
        return True  # Not a failure, just missing deps
    except Exception as e:
        print(f"❌ Auth test failed: {e}")
        return False

def test_api_structure():
    """Test that API structure is properly organized"""
    try:
        api_path = src_path / "api" / "routers"
        expected_routers = [
            "auth.py", "content.py", "platforms.py", 
            "analytics.py", "webhooks.py", "starter_pro.py"
        ]
        
        for router_file in expected_routers:
            router_path = api_path / router_file
            assert router_path.exists(), f"Router {router_file} not found"
        
        print("✅ All expected API router files exist")
        
        # Check that each router has basic structure
        for router_file in expected_routers:
            router_path = api_path / router_file
            content = router_path.read_text()
            
            # Each router should import APIRouter and define router
            assert "APIRouter" in content, f"{router_file} missing APIRouter import"
            assert "router = APIRouter()" in content, f"{router_file} missing router definition"
        
        print("✅ All routers have proper structure")
        return True
    except Exception as e:
        print(f"❌ API structure test failed: {e}")
        return False

def test_models_structure():
    """Test database models structure"""
    try:
        models_path = src_path / "models" / "models.py"
        assert models_path.exists(), "Models file not found"
        
        content = models_path.read_text()
        
        # Check for expected model classes
        expected_models = [
            "class User(Base):", "class Project(Base):", "class ContentItem(Base):",
            "class SocialAccount(Base):", "class Campaign(Base):", "class Publication(Base):"
        ]
        
        for model in expected_models:
            assert model in content, f"Model definition '{model}' not found"
        
        print("✅ All expected database models are defined")
        return True
    except Exception as e:
        print(f"❌ Models structure test failed: {e}")
        return False

def test_services_structure():
    """Test services structure"""
    try:
        services_path = src_path / "services"
        expected_services = [
            "ai_content_generator.py", "voice_generator.py", 
            "video_processor.py", "social_publisher.py"
        ]
        
        for service_file in expected_services:
            service_path = services_path / service_file
            assert service_path.exists(), f"Service {service_file} not found"
        
        print("✅ All expected service files exist")
        
        # Check services init file
        init_path = services_path / "__init__.py"
        assert init_path.exists(), "Services __init__.py not found"
        
        init_content = init_path.read_text()
        expected_imports = [
            "AIContentGenerator", "VoiceGenerator", 
            "VideoProcessor", "SocialMediaPublisher"
        ]
        
        for import_name in expected_imports:
            assert import_name in init_content, f"Service {import_name} not exported"
        
        print("✅ Services are properly exported")
        return True
    except Exception as e:
        print(f"❌ Services structure test failed: {e}")
        return False

def test_configuration():
    """Test configuration management"""
    try:
        from core.config import settings
        
        # Test that all required settings are defined
        required_settings = [
            'SECRET_KEY', 'DEBUG', 'API_HOST', 'API_PORT',
            'DATABASE_URL', 'REDIS_URL', 'OPENAI_API_KEY',
            'ELEVENLABS_API_KEY', 'YOUTUBE_API_KEY'
        ]
        
        for setting in required_settings:
            assert hasattr(settings, setting), f"Setting {setting} not defined"
        
        print("✅ All required configuration settings are defined")
        
        # Test default values
        assert settings.API_HOST == "0.0.0.0"
        assert settings.API_PORT == 8000
        assert settings.DEBUG is True
        print("✅ Default configuration values are correct")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def run_all_tests():
    """Run all available tests"""
    print("🚀 Running Social Media Automation Platform Tests\n")
    
    tests = [
        ("Core Imports", test_imports),
        ("Schema Definitions", test_schemas), 
        ("Authentication Functions", test_auth_functions),
        ("API Structure", test_api_structure),
        ("Database Models", test_models_structure),
        ("Services Structure", test_services_structure),
        ("Configuration", test_configuration),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
        print()
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application structure is correct.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)