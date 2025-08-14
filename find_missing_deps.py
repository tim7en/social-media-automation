#!/usr/bin/env python3
"""
Script to find all missing Python dependencies in the project.
"""

import ast
import os
import sys
import subprocess
from pathlib import Path
from typing import Set, List, Dict

# Known standard library modules (Python 3.11)
STDLIB_MODULES = {
    'abc', 'aifc', 'argparse', 'array', 'ast', 'asynchat', 'asyncio', 'asyncore',
    'atexit', 'audioop', 'base64', 'bdb', 'binascii', 'binhex', 'bisect', 'builtins',
    'bz2', 'calendar', 'cgi', 'cgitb', 'chunk', 'cmd', 'code', 'codecs', 'codeop',
    'collections', 'colorsys', 'compileall', 'concurrent', 'configparser', 'contextlib',
    'copy', 'copyreg', 'cProfile', 'csv', 'ctypes', 'curses', 'datetime', 'dbm',
    'decimal', 'difflib', 'dis', 'doctest', 'email', 'encodings', 'ensurepip',
    'enum', 'errno', 'faulthandler', 'fcntl', 'filecmp', 'fileinput', 'fnmatch',
    'fractions', 'ftplib', 'functools', 'gc', 'getopt', 'getpass', 'gettext',
    'glob', 'gzip', 'hashlib', 'heapq', 'hmac', 'html', 'http', 'imaplib',
    'imghdr', 'imp', 'importlib', 'inspect', 'io', 'ipaddress', 'itertools',
    'json', 'keyword', 'lib2to3', 'linecache', 'locale', 'logging', 'lzma',
    'mailbox', 'mailcap', 'marshal', 'math', 'mimetypes', 'mmap', 'modulefinder',
    'multiprocessing', 'netrc', 'nntplib', 'numbers', 'operator', 'optparse',
    'os', 'pathlib', 'pdb', 'pickle', 'pickletools', 'pipes', 'pkgutil',
    'platform', 'plistlib', 'poplib', 'posix', 'pprint', 'profile', 'pstats',
    'pty', 'pwd', 'py_compile', 'pyclbr', 'pydoc', 'queue', 'quopri', 'random',
    're', 'readline', 'reprlib', 'resource', 'rlcompleter', 'runpy', 'sched',
    'secrets', 'select', 'selectors', 'shelve', 'shlex', 'shutil', 'signal',
    'site', 'smtplib', 'sndhdr', 'socket', 'socketserver', 'sqlite3', 'ssl',
    'stat', 'statistics', 'string', 'stringprep', 'struct', 'subprocess',
    'sunau', 'symtable', 'sys', 'sysconfig', 'tabnanny', 'tarfile', 'telnetlib',
    'tempfile', 'termios', 'textwrap', 'threading', 'time', 'timeit', 'tkinter',
    'token', 'tokenize', 'trace', 'traceback', 'tracemalloc', 'tty', 'turtle',
    'types', 'typing', 'unicodedata', 'unittest', 'urllib', 'uu', 'uuid',
    'venv', 'warnings', 'wave', 'weakref', 'webbrowser', 'winreg', 'wsgiref',
    'xdrlib', 'xml', 'xmlrpc', 'zipapp', 'zipfile', 'zipimport', 'zlib',
    '__future__', '__main__'
}

# Module name mappings (PyPI package name -> import name)
MODULE_MAPPINGS = {
    'pillow': 'PIL',
    'opencv-python': 'cv2',
    'python-jose': 'jose',
    'python-jose[cryptography]': 'jose',
    'beautifulsoup4': 'bs4',
    'pyjwt': 'jwt',
    'google-api-python-client': 'googleapiclient',
    'google-auth': 'google.auth',
    'google-auth-oauthlib': 'google_auth_oauthlib',
    'google-auth-httplib2': 'google_auth_httplib2',
    'facebook-sdk': 'facebook',
    'python-multipart': 'multipart',
    'python-dotenv': 'dotenv',
    'pydantic-settings': 'pydantic_settings',
    'email-validator': 'email_validator',
    'passlib': 'passlib',
    'python-slugify': 'slugify',
    'python-crontab': 'crontab',
    'psycopg2-binary': 'psycopg2',
    'redis': 'redis',
    'celery': 'celery',
    'flower': 'flower',
    'structlog': 'structlog',
    'sentry-sdk': 'sentry_sdk',
    'prometheus-client': 'prometheus_client',
    'aiofiles': 'aiofiles',
    'httpx': 'httpx',
    'jinja2': 'jinja2',
    'ffmpeg-python': 'ffmpeg',
    'moviepy': 'moviepy',
    'elevenlabs': 'elevenlabs',
    'openai': 'openai',
    'anthropic': 'anthropic',
    'instagrapi': 'instagrapi',
    'TikTokApi': 'TikTokApi',
    'pytube': 'pytube',
    'scrapy': 'scrapy',
    'feedparser': 'feedparser',
    'APScheduler': 'apscheduler',
    'dramatiq': 'dramatiq',
    'boto3': 'boto3',
    'minio': 'minio',
    'asyncpg': 'asyncpg',
}

def extract_imports_from_file(filepath: Path) -> Set[str]:
    """Extract all import statements from a Python file."""
    imports = set()
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content, filename=str(filepath))
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split('.')[0]
                    imports.add(module_name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_name = node.module.split('.')[0]
                    imports.add(module_name)
                    
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"Warning: Could not parse {filepath}: {e}")
    
    return imports

def find_all_imports(src_dir: Path) -> Set[str]:
    """Find all imports in the source directory."""
    all_imports = set()
    
    for py_file in src_dir.rglob("*.py"):
        if "__pycache__" not in str(py_file):
            imports = extract_imports_from_file(py_file)
            all_imports.update(imports)
    
    return all_imports

def get_installed_packages() -> Set[str]:
    """Get list of installed packages."""
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--format=freeze'], 
                              capture_output=True, text=True, check=True)
        installed = set()
        for line in result.stdout.strip().split('\n'):
            if '==' in line:
                package_name = line.split('==')[0].lower()
                installed.add(package_name)
        return installed
    except subprocess.CalledProcessError:
        print("Warning: Could not get installed packages list")
        return set()

def load_requirements(req_file: Path) -> Set[str]:
    """Load requirements from requirements.txt file."""
    requirements = set()
    
    if not req_file.exists():
        return requirements
    
    try:
        with open(req_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Remove version specifiers
                    package = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].split('!=')[0]
                    package = package.split('[')[0]  # Remove extras like [email]
                    requirements.add(package.lower())
    except Exception as e:
        print(f"Warning: Could not read requirements.txt: {e}")
    
    return requirements

def reverse_lookup_package_name(import_name: str, module_mappings: Dict[str, str]) -> List[str]:
    """Find package names that provide the given import name."""
    candidates = []
    
    # Direct match
    candidates.append(import_name)
    
    # Check mappings
    for package, module in module_mappings.items():
        if module == import_name or module.startswith(f"{import_name}."):
            candidates.append(package)
    
    return candidates

def analyze_dependencies():
    """Main analysis function."""
    src_dir = Path("src")
    req_file = Path("requirements.txt")
    
    if not src_dir.exists():
        print("Error: src directory not found")
        return
    
    print("🔍 Analyzing Python imports...")
    all_imports = find_all_imports(src_dir)
    
    print("📋 Loading requirements.txt...")
    requirements = load_requirements(req_file)
    
    print("📦 Getting installed packages...")
    installed = get_installed_packages()
    
    # Filter out standard library modules and relative imports
    third_party_imports = {
        imp for imp in all_imports 
        if imp not in STDLIB_MODULES and not imp.startswith('.')
    }
    
    print(f"\n📊 Analysis Results:")
    print(f"   Total imports found: {len(all_imports)}")
    print(f"   Third-party imports: {len(third_party_imports)}")
    print(f"   Requirements in file: {len(requirements)}")
    print(f"   Installed packages: {len(installed)}")
    
    print(f"\n🔍 Third-party imports found:")
    for imp in sorted(third_party_imports):
        print(f"   - {imp}")
    
    # Find potentially missing dependencies
    missing_deps = []
    
    for import_name in third_party_imports:
        # Check if this import has a corresponding package
        candidates = reverse_lookup_package_name(import_name, MODULE_MAPPINGS)
        
        found_in_requirements = any(pkg in requirements for pkg in candidates)
        found_in_installed = any(pkg in installed for pkg in candidates)
        
        if not found_in_requirements:
            missing_deps.append({
                'import': import_name,
                'candidates': candidates,
                'in_installed': found_in_installed
            })
    
    if missing_deps:
        print(f"\n❌ Potentially missing dependencies:")
        for dep in missing_deps:
            status = "✓ Installed" if dep['in_installed'] else "✗ Not installed"
            print(f"   - {dep['import']} -> {dep['candidates']} ({status})")
        
        print(f"\n💡 Suggested additions to requirements.txt:")
        suggested = set()
        for dep in missing_deps:
            # Use the most common package name
            best_candidate = dep['candidates'][0]
            if best_candidate in MODULE_MAPPINGS.values():
                # Find the package name for this module
                for pkg, mod in MODULE_MAPPINGS.items():
                    if mod == dep['import']:
                        best_candidate = pkg
                        break
            suggested.add(best_candidate)
        
        for pkg in sorted(suggested):
            print(f"   {pkg}")
    else:
        print(f"\n✅ All dependencies appear to be satisfied!")

if __name__ == "__main__":
    analyze_dependencies()
