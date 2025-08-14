#!/usr/bin/env python3
"""
Dependency installer script for Social Media Automation Platform
Automatically detects and installs missing Python packages
"""

import subprocess
import sys
import os
import ast
import importlib
from pathlib import Path
from typing import Set, List, Dict, Optional
import re

class DependencyInstaller:
    def __init__(self, venv_path: str = ".venv"):
        self.venv_path = Path(venv_path)
        self.python_exe = self.venv_path / "bin" / "python"
        self.pip_exe = self.venv_path / "bin" / "pip"
        self.project_root = Path(__file__).parent
        
        # Common package name mappings (import name -> pip package name)
        self.package_mappings = {
            'cv2': 'opencv-python',
            'PIL': 'Pillow',
            'sklearn': 'scikit-learn',
            'yaml': 'PyYAML',
            'dotenv': 'python-dotenv',
            'jose': 'python-jose[cryptography]',
            'multipart': 'python-multipart',
            'bcrypt': 'passlib[bcrypt]',
            'jwt': 'PyJWT',
            'redis': 'redis',
            'celery': 'celery',
            'flower': 'flower',
            'structlog': 'structlog',
            'sqlalchemy': 'sqlalchemy',
            'alembic': 'alembic',
            'asyncpg': 'asyncpg',
            'psycopg2': 'psycopg2-binary',
            'boto3': 'boto3',
            'minio': 'minio',
            'elevenlabs': 'elevenlabs',
            'moviepy': 'moviepy',
            'pydub': 'pydub',
            'ffmpeg': 'ffmpeg-python',
            'whisper': 'openai-whisper',
            'pytube': 'pytube',
            'instagrapi': 'instagrapi',
            'TikTokApi': 'TikTokApi',
            'facebook': 'facebook-sdk',
            'google': 'google-api-python-client',
            'googleapiclient': 'google-api-python-client',
            'google_auth_oauthlib': 'google-auth-oauthlib',
            'google_auth_httplib2': 'google-auth-httplib2',
            'bs4': 'beautifulsoup4',
            'scrapy': 'scrapy',
            'feedparser': 'feedparser',
            'APScheduler': 'APScheduler',
            'dramatiq': 'dramatiq',
            'sentry_sdk': 'sentry-sdk',
            'prometheus_client': 'prometheus-client',
            'pytest': 'pytest',
            'aiofiles': 'aiofiles',
            'httpx': 'httpx',
            'jinja2': 'Jinja2',
            'slugify': 'python-slugify',
            'crontab': 'python-crontab',
            'numpy': 'numpy',
            'cryptography': 'cryptography',
            'psutil': 'psutil',
            'passlib': 'passlib[bcrypt]',
            'email_validator': 'email-validator',
        }
        
        # Standard library modules (don't need installation)
        self.stdlib_modules = {
            'os', 'sys', 'json', 'datetime', 'time', 'logging', 'asyncio',
            'typing', 'pathlib', 'subprocess', 'threading', 'multiprocessing',
            'collections', 'itertools', 'functools', 'contextlib', 'base64',
            'hashlib', 'hmac', 'uuid', 'urllib', 're', 'math', 'random',
            'string', 'io', 'tempfile', 'shutil', 'glob', 'pickle', 'csv',
            'configparser', 'argparse', 'dataclasses', 'enum', 'warnings',
            'weakref', 'gc', 'copy', 'operator', 'heapq', 'bisect', 'array',
            'struct', 'zlib', 'gzip', 'bz2', 'lzma', 'zipfile', 'tarfile',
            'calendar', 'decimal', 'fractions', 'statistics', 'socket',
            'select', 'asyncio', 'concurrent', 'queue', 'sched'
        }

    def ensure_venv_exists(self):
        """Ensure virtual environment exists"""
        if not self.venv_path.exists():
            print(f"Creating virtual environment at {self.venv_path}")
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)], check=True)
        
        if not self.python_exe.exists():
            raise FileNotFoundError(f"Python executable not found at {self.python_exe}")

    def get_installed_packages(self) -> Set[str]:
        """Get list of currently installed packages"""
        try:
            result = subprocess.run(
                [str(self.pip_exe), "list", "--format=freeze"],
                capture_output=True, text=True, check=True
            )
            packages = set()
            for line in result.stdout.strip().split('\n'):
                if '==' in line:
                    package_name = line.split('==')[0].lower()
                    packages.add(package_name)
            return packages
        except subprocess.CalledProcessError:
            return set()

    def extract_imports_from_file(self, file_path: Path) -> Set[str]:
        """Extract import statements from a Python file"""
        imports = set()
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Parse the AST to extract imports
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.add(alias.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.add(node.module.split('.')[0])
            except SyntaxError:
                # If AST parsing fails, use regex as fallback
                import_pattern = r'^\s*(?:from\s+(\S+)\s+)?import\s+(\S+)'
                for line in content.split('\n'):
                    match = re.match(import_pattern, line.strip())
                    if match:
                        if match.group(1):  # from X import Y
                            imports.add(match.group(1).split('.')[0])
                        else:  # import X
                            imports.add(match.group(2).split('.')[0])
                            
        except Exception as e:
            print(f"Warning: Could not parse {file_path}: {e}")
        
        return imports

    def find_python_files(self) -> List[Path]:
        """Find all Python files in the project"""
        python_files = []
        for pattern in ['**/*.py']:
            python_files.extend(self.project_root.glob(pattern))
        
        # Exclude virtual environment and cache directories
        excluded_dirs = {'.venv', '__pycache__', '.git', 'node_modules', '.pytest_cache'}
        return [
            f for f in python_files 
            if not any(part in excluded_dirs for part in f.parts)
        ]

    def get_all_imports(self) -> Set[str]:
        """Get all import statements from all Python files"""
        all_imports = set()
        python_files = self.find_python_files()
        
        print(f"Scanning {len(python_files)} Python files for imports...")
        for file_path in python_files:
            imports = self.extract_imports_from_file(file_path)
            all_imports.update(imports)
        
        return all_imports

    def filter_third_party_imports(self, imports: Set[str]) -> Set[str]:
        """Filter out standard library and local imports"""
        third_party = set()
        
        # Local modules specific to this project
        local_modules = {
            'src', 'tests', 'ui-tests', 'main', 'auth', 'content', 'platforms', 
            'analytics', 'webhooks', 'starter_pro', 'workflows', 'api_keys',
            'content_generation', 'social_publishing', 'ai_content_generator',
            'processors', 'api_key_service', 'video_processor', 'ai_services',
            'social_media_templates', 'presets', 'scheduler', 'triggers',
            'queue_manager', 'assets', 'social_publisher', 'nodes',
            'voice_generator', 'config', 'logger', 'engine', 'templates',
            'conditions', 'actions', 'monitoring', 'database', 'redis',
            'celery_app', 'models', 'schemas', 'utils', 'validators',
            'error_handler', 'health_check', 'security', 'performance',
            'test_utils', 'input_validation', 'ffmpeg', 'social_media',
            'conftest'
        }
        
        for imp in imports:
            # Skip standard library modules
            if imp in self.stdlib_modules:
                continue
            
            # Skip relative imports and known local modules
            if imp.startswith('.') or imp in local_modules:
                continue
                
            # Skip if it's likely a local module (exists as directory in project)
            if (self.project_root / imp).exists() or (self.project_root / 'src' / imp).exists():
                continue
                
            third_party.add(imp)
        
        return third_party

    def get_pip_package_name(self, import_name: str) -> str:
        """Convert import name to pip package name"""
        # Check our mappings first
        if import_name in self.package_mappings:
            return self.package_mappings[import_name]
        
        # For most packages, the import name matches the pip name
        return import_name

    def install_packages(self, packages: List[str]) -> bool:
        """Install packages using pip"""
        if not packages:
            print("No packages to install.")
            return True
        
        print(f"Installing packages: {', '.join(packages)}")
        try:
            cmd = [str(self.pip_exe), "install"] + packages
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("Installation successful!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Installation failed: {e}")
            print(f"Error output: {e.stderr}")
            return False

    def install_from_requirements(self) -> bool:
        """Install packages from requirements.txt if it exists"""
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            print("No requirements.txt found.")
            return True
        
        print("Installing from requirements.txt...")
        try:
            cmd = [str(self.pip_exe), "install", "-r", str(requirements_file)]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("Requirements installation successful!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Requirements installation failed: {e}")
            print(f"Error output: {e.stderr}")
            
            # Try installing packages one by one
            print("Attempting to install packages individually...")
            return self.install_requirements_individually(requirements_file)

    def install_requirements_individually(self, requirements_file: Path) -> bool:
        """Install requirements one by one to handle version conflicts"""
        failed_packages = []
        
        with open(requirements_file, 'r') as f:
            lines = f.readlines()
        
        packages = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                packages.append(line)
        
        for package in packages:
            print(f"Installing {package}...")
            try:
                cmd = [str(self.pip_exe), "install", package]
                subprocess.run(cmd, check=True, capture_output=True, text=True)
                print(f"✓ {package} installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"✗ Failed to install {package}: {e}")
                failed_packages.append(package)
        
        if failed_packages:
            print(f"\nFailed to install: {', '.join(failed_packages)}")
            return False
        
        return True

    def check_missing_imports(self) -> List[str]:
        """Check which imports are missing and need to be installed"""
        print("Checking for missing imports...")
        
        # Try to import each detected third-party package
        all_imports = self.get_all_imports()
        third_party_imports = self.filter_third_party_imports(all_imports)
        
        missing_packages = []
        installed_packages = self.get_installed_packages()
        
        for imp in third_party_imports:
            pip_package = self.get_pip_package_name(imp)
            package_name = pip_package.split('[')[0].lower()  # Remove extras like [cryptography]
            
            if package_name not in installed_packages:
                try:
                    importlib.import_module(imp)
                    print(f"✓ {imp} is available")
                except ImportError:
                    print(f"✗ {imp} is missing (pip package: {pip_package})")
                    missing_packages.append(pip_package)
        
        return missing_packages

    def run(self):
        """Main execution method"""
        print("=== Social Media Automation Platform - Dependency Installer ===\n")
        
        # Ensure virtual environment exists
        self.ensure_venv_exists()
        
        # First, try to install from requirements.txt
        requirements_success = self.install_from_requirements()
        
        # Then check for any remaining missing imports
        missing_packages = self.check_missing_imports()
        
        if missing_packages:
            print(f"\nFound {len(missing_packages)} missing packages.")
            success = self.install_packages(missing_packages)
            if not success:
                return False
        else:
            print("\nAll required packages are already installed!")
        
        # Final check
        print("\n=== Final Import Check ===")
        final_missing = self.check_missing_imports()
        
        if final_missing:
            print(f"\nWarning: Some packages are still missing: {', '.join(final_missing)}")
            print("You may need to install them manually or check for name conflicts.")
            return False
        else:
            print("\n✅ All dependencies are installed successfully!")
            return True

def main():
    installer = DependencyInstaller()
    success = installer.run()
    
    if success:
        print("\n🚀 You can now try launching the application:")
        print("source .venv/bin/activate && python -m src.main")
    else:
        print("\n❌ Some dependencies could not be installed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
