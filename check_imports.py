#!/usr/bin/env python3
"""
Script to find imports of non-existent modules in the codebase.
"""

import ast
import os
import sys
from pathlib import Path
from typing import Set, List, Dict, Tuple, Optional

def extract_imports_from_file(file_path: Path) -> List[Tuple[str, int]]:
    """Extract all import statements from a Python file with line numbers."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append((alias.name, node.lineno))
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    # Handle "from module import ..." 
                    imports.append((node.module, node.lineno))
                    # Also check individual imports like "from module import submodule"
                    for alias in node.names:
                        if alias.name != '*':
                            full_import = f"{node.module}.{alias.name}"
                            imports.append((full_import, node.lineno))
            elif isinstance(node, ast.Str):
                # Check for string literals that look like module paths (for Celery includes, etc.)
                if ('src.' in node.s and 
                    '/' not in node.s and 
                    node.s.count('.') >= 2 and
                    not node.s.startswith('http')):
                    imports.append((node.s, node.lineno))
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                # Python 3.8+ uses ast.Constant instead of ast.Str
                if ('src.' in node.value and 
                    '/' not in node.value and 
                    node.value.count('.') >= 2 and
                    not node.value.startswith('http')):
                    imports.append((node.value, node.lineno))
        
        return imports
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []

def module_exists(module_name: str, src_root: Path) -> bool:
    """Check if a module exists either as a Python file or package."""
    
    # Skip standard library modules
    stdlib_modules = {
        'os', 'sys', 'json', 'datetime', 'typing', 'pathlib', 'asyncio',
        'logging', 'uuid', 'base64', 're', 'secrets', 'functools', 'itertools',
        'collections', 'dataclasses', 'enum', 'abc', 'contextlib', 'hashlib',
        'shutil', 'subprocess', 'tempfile', 'time', 'traceback', 'importlib',
        'inspect', 'copy', 'pickle', 'math', 'random', 'string', 'io',
        'threading', 'multiprocessing', 'queue', 'warnings', 'operator'
    }
    
    if module_name.split('.')[0] in stdlib_modules:
        return True
    
    # Skip third-party packages (they should be in requirements.txt)
    third_party_prefixes = {
        'fastapi', 'uvicorn', 'pydantic', 'sqlalchemy', 'celery', 'redis',
        'httpx', 'requests', 'openai', 'anthropic', 'elevenlabs', 'PIL',
        'cv2', 'numpy', 'moviepy', 'ffmpeg', 'pydub', 'whisper', 'bs4',
        'boto3', 'minio', 'pytest', 'jinja2', 'slugify', 'dotenv', 'jose',
        'passlib', 'cryptography', 'google', 'facebook', 'instagrapi',
        'TikTokApi', 'pytube', 'structlog', 'sentry_sdk', 'prometheus_client',
        'apscheduler', 'dramatiq', 'flower', 'psutil', 'asyncpg', 'psycopg2',
        'alembic', 'scrapy', 'feedparser', 'crontab', 'multipart', 'starlette',
        'email_validator', 'pydantic_settings'
    }
    
    if any(module_name.startswith(prefix) for prefix in third_party_prefixes):
        return True
    
    # Check if it's a local module (starts with 'src.')
    if module_name.startswith('src.'):
        # Convert module path to file path
        module_parts = module_name.split('.')
        
        # Try as a package (directory with __init__.py)
        package_path = src_root
        for part in module_parts:
            package_path = package_path / part
        
        if package_path.is_dir() and (package_path / '__init__.py').exists():
            return True
        
        # Try as a Python file
        file_path = src_root
        for part in module_parts[:-1]:  # All but the last part
            file_path = file_path / part
        file_path = file_path / f"{module_parts[-1]}.py"
        
        if file_path.exists():
            return True
        
        return False
    
    # For other modules, assume they exist (might be installed packages)
    return True

def find_missing_imports():
    """Find all imports of non-existent modules."""
    src_root = Path("src")
    if not src_root.exists():
        print("❌ 'src' directory not found!")
        return
    
    print("🔍 Scanning for imports of non-existent modules...")
    
    missing_imports = {}
    all_files = []
    
    # Get all Python files
    for py_file in src_root.rglob("*.py"):
        if "__pycache__" not in str(py_file):
            all_files.append(py_file)
    
    print(f"📁 Found {len(all_files)} Python files to check")
    
    for py_file in all_files:
        imports = extract_imports_from_file(py_file)
        
        for module_name, line_no in imports:
            if not module_exists(module_name, src_root):
                if py_file not in missing_imports:
                    missing_imports[py_file] = []
                missing_imports[py_file].append((module_name, line_no))
    
    # Report results
    if missing_imports:
        print(f"\n❌ Found imports of non-existent modules in {len(missing_imports)} files:")
        
        for file_path, imports in missing_imports.items():
            print(f"\n📄 {file_path}:")
            for module_name, line_no in imports:
                print(f"   Line {line_no}: {module_name}")
                
        print(f"\n🔧 Total missing imports: {sum(len(imports) for imports in missing_imports.values())}")
        
        # Show files with content for easy fixing
        print(f"\n📝 Files that need fixing:")
        for file_path in missing_imports.keys():
            print(f"   - {file_path}")
            
    else:
        print(f"\n✅ No imports of non-existent modules found!")

def show_file_with_line_numbers(file_path: Path, highlight_lines: Optional[Set[int]] = None):
    """Show file content with line numbers, highlighting specific lines."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"\n📄 {file_path}:")
        print("=" * 60)
        
        for i, line in enumerate(lines, 1):
            marker = ">>> " if highlight_lines and i in highlight_lines else "    "
            print(f"{marker}{i:3d}: {line.rstrip()}")
            
        print("=" * 60)
        
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

if __name__ == "__main__":
    find_missing_imports()
    
    # If user wants to see specific files
    if len(sys.argv) > 1 and sys.argv[1] == "--show-files":
        print(f"\n" + "="*80)
        print("DETAILED FILE CONTENT")
        print("="*80)
        
        src_root = Path("src")
        for py_file in src_root.rglob("*.py"):
            if "__pycache__" not in str(py_file):
                imports = extract_imports_from_file(py_file)
                missing_lines = set()
                
                for module_name, line_no in imports:
                    if not module_exists(module_name, src_root):
                        missing_lines.add(line_no)
                
                if missing_lines:
                    show_file_with_line_numbers(py_file, missing_lines)
