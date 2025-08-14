#!/usr/bin/env python3
"""
Simplified script to find missing third-party dependencies.
"""

import re
from pathlib import Path

def extract_third_party_imports():
    """Extract known third-party imports from source files."""
    
    # Known third-party packages and their import names
    KNOWN_PACKAGES = {
        # Web framework
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'starlette': 'starlette',
        
        # Data validation
        'pydantic': 'pydantic',
        'pydantic-settings': 'pydantic_settings',
        'email-validator': 'email_validator',
        
        # Database
        'sqlalchemy': 'sqlalchemy',
        'asyncpg': 'asyncpg',
        'psycopg2-binary': 'psycopg2',
        'alembic': 'alembic',
        
        # Cache/Queue
        'redis': 'redis',
        'celery': 'celery',
        'flower': 'flower',
        
        # Authentication/Security
        'python-jose': 'jose',
        'passlib': 'passlib',
        'cryptography': 'cryptography',
        
        # HTTP clients
        'httpx': 'httpx',
        'requests': 'requests',
        'aiofiles': 'aiofiles',
        
        # AI services
        'openai': 'openai',
        'anthropic': 'anthropic',
        'elevenlabs': 'elevenlabs',
        
        # Social media APIs
        'google-api-python-client': 'googleapiclient',
        'google-auth': 'google',
        'google-auth-oauthlib': 'google_auth_oauthlib',
        'google-auth-httplib2': 'google_auth_httplib2',
        'facebook-sdk': 'facebook',
        'instagrapi': 'instagrapi',
        'TikTokApi': 'TikTokApi',
        'pytube': 'pytube',
        
        # Image/Video processing
        'Pillow': 'PIL',
        'opencv-python': 'cv2',
        'moviepy': 'moviepy',
        'ffmpeg-python': 'ffmpeg',
        'numpy': 'numpy',
        
        # Audio
        'pydub': 'pydub',
        'whisper': 'whisper',
        
        # Web scraping
        'beautifulsoup4': 'bs4',
        'scrapy': 'scrapy',
        'feedparser': 'feedparser',
        
        # Background tasks
        'APScheduler': 'apscheduler',
        'dramatiq': 'dramatiq',
        
        # Storage
        'boto3': 'boto3',
        'minio': 'minio',
        
        # Monitoring/Logging
        'structlog': 'structlog',
        'sentry-sdk': 'sentry_sdk',
        'prometheus-client': 'prometheus_client',
        
        # Development/Testing
        'pytest': 'pytest',
        'pytest-asyncio': 'pytest_asyncio',
        'black': 'black',
        'flake8': 'flake8',
        'mypy': 'mypy',
        'pre-commit': 'pre_commit',
        
        # Utilities
        'jinja2': 'jinja2',
        'python-slugify': 'slugify',
        'python-crontab': 'crontab',
        'python-multipart': 'multipart',
        'python-dotenv': 'dotenv',
        
        # System
        'psutil': 'psutil',
    }
    
    # Read all Python files and find imports
    src_dir = Path("src")
    found_imports = set()
    
    for py_file in src_dir.rglob("*.py"):
        if "__pycache__" not in str(py_file):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find import statements
                import_patterns = [
                    r'^from\s+(\w+)',
                    r'^import\s+(\w+)',
                ]
                
                for pattern in import_patterns:
                    matches = re.findall(pattern, content, re.MULTILINE)
                    found_imports.update(matches)
                    
            except Exception as e:
                print(f"Warning: Could not read {py_file}: {e}")
    
    # Match found imports with known packages
    required_packages = set()
    missing_imports = []
    
    for import_name in found_imports:
        package_found = False
        for package, module in KNOWN_PACKAGES.items():
            if import_name == module or import_name.startswith(f"{module}."):
                required_packages.add(package)
                package_found = True
                break
        
        if not package_found and import_name not in {
            'src', 'typing', 'datetime', 'os', 'sys', 'json', 'uuid', 'base64',
            're', 'pathlib', 'asyncio', 'logging', 'secrets', 'functools',
            'itertools', 'collections', 'dataclasses', 'enum', 'abc'
        }:
            missing_imports.append(import_name)
    
    return required_packages, missing_imports

def load_current_requirements():
    """Load current requirements.txt."""
    req_file = Path("requirements.txt")
    requirements = set()
    
    if req_file.exists():
        with open(req_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract package name (remove version specifiers)
                    package = re.split(r'[=<>!~]', line)[0]
                    package = package.split('[')[0]  # Remove extras
                    requirements.add(package)
    
    return requirements

def main():
    print("🔍 Analyzing dependencies...")
    
    required_packages, unknown_imports = extract_third_party_imports()
    current_requirements = load_current_requirements()
    
    missing = required_packages - current_requirements
    
    print(f"\n📦 Required packages: {len(required_packages)}")
    print(f"📋 Current requirements: {len(current_requirements)}")
    print(f"❌ Missing packages: {len(missing)}")
    
    if missing:
        print(f"\n❌ Missing from requirements.txt:")
        for package in sorted(missing):
            print(f"   - {package}")
    
    if unknown_imports:
        print(f"\n❓ Unknown imports (may need manual review):")
        for imp in sorted(unknown_imports):
            print(f"   - {imp}")
    
    if not missing:
        print(f"\n✅ All known dependencies are in requirements.txt!")

if __name__ == "__main__":
    main()
