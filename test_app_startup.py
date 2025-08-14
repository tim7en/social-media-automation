#!/usr/bin/env python3
"""
Quick test to check if the FastAPI app can start with our new workflow routes
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_app_startup():
    """Test if the FastAPI app can start with the new workflow routes"""
    try:
        from main import app
        print("✅ FastAPI app imported successfully")
        
        # Check if workflow routes are included
        routes = [route.path for route in app.routes]
        workflow_routes = [r for r in routes if 'workflow' in r]
        
        print(f"✅ Found {len(workflow_routes)} workflow routes:")
        for route in workflow_routes:
            print(f"  - {route}")
        
        # Check if our templates are accessible
        from workflows.templates import WORKFLOW_TEMPLATES
        print(f"✅ Workflow templates accessible: {len(WORKFLOW_TEMPLATES)} templates")
        
        return True
        
    except Exception as e:
        print(f"❌ App startup test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing FastAPI App Startup")
    print("=" * 50)
    
    success = test_app_startup()
    
    if success:
        print("\n🎉 App startup test passed!")
    else:
        print("\n💥 App startup test failed!")
        sys.exit(1)