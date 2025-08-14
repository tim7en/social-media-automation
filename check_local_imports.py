#!/usr/bin/env python3
"""
Simple script to check for imports of non-existent local modules.
This helps identify modules that need to be created or imports that should be removed.
"""

import ast
import re
from pathlib import Path
from typing import List, Tuple

def find_local_module_imports():
    """Find imports of non-existent local modules (src.* modules)."""
    
    src_dir = Path("src")
    if not src_dir.exists():
        print("❌ 'src' directory not found!")
        return
    
    print("🔍 Checking for imports of non-existent local modules...")
    
    issues = []
    
    for py_file in src_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                imports_to_check = []
                
                # Regular imports
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith('src.'):
                            imports_to_check.append((alias.name, node.lineno))
                
                # From imports
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module.startswith('src.'):
                        imports_to_check.append((node.module, node.lineno))
                
                # String literals (for Celery includes, etc.)
                elif isinstance(node, (ast.Str, ast.Constant)):
                    value = getattr(node, 's', None) or getattr(node, 'value', None)
                    if (isinstance(value, str) and 
                        value.startswith('src.') and 
                        '/' not in value and
                        value.count('.') >= 2):
                        imports_to_check.append((value, node.lineno))
                
                # Check each import
                for module_name, line_no in imports_to_check:
                    if not module_exists_locally(module_name, src_dir):
                        issues.append((py_file, line_no, module_name))
        
        except Exception as e:
            print(f"Warning: Could not parse {py_file}: {e}")
    
    if issues:
        print(f"\n❌ Found {len(issues)} imports of non-existent local modules:")
        
        current_file = None
        for file_path, line_no, module_name in issues:
            if file_path != current_file:
                print(f"\n📄 {file_path}:")
                current_file = file_path
            print(f"   Line {line_no}: {module_name}")
        
        print(f"\n🔧 Action needed:")
        print(f"   1. Create the missing modules, or")
        print(f"   2. Remove/fix the import statements")
        
    else:
        print(f"\n✅ No imports of non-existent local modules found!")

def module_exists_locally(module_name: str, src_root: Path) -> bool:
    """Check if a local module (src.*) actually exists."""
    
    if not module_name.startswith('src.'):
        return True  # Not a local module
    
    # Convert module path to file path - skip the 'src' part since we're already in src_root
    module_parts = module_name.split('.')[1:]  # Remove 'src' from the beginning
    
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
    
    return file_path.exists()

if __name__ == "__main__":
    find_local_module_imports()
