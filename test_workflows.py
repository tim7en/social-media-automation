#!/usr/bin/env python3
"""
Test script for the workflow engine implementation
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from workflows.engine import WorkflowEngine
from workflows.nodes.processors import ContentGeneratorNode, VideoProcessorNode, SocialMediaPostNode
from workflows.nodes.triggers import ManualTrigger
from workflows.templates import WORKFLOW_TEMPLATES
from automation.queue_manager import QueueManager
from automation.scheduler import ContentScheduler

async def test_workflow_engine():
    """Test the workflow engine"""
    print("🚀 Testing Workflow Engine")
    print("=" * 50)
    
    # Initialize engine
    engine = WorkflowEngine()
    
    # Register node types
    engine.register_node_type("ManualTrigger", ManualTrigger)
    engine.register_node_type("ContentGeneratorNode", ContentGeneratorNode)
    engine.register_node_type("VideoProcessorNode", VideoProcessorNode)
    engine.register_node_type("SocialMediaPostNode", SocialMediaPostNode)
    
    print("✅ Engine initialized and node types registered")
    
    # Test simple workflow
    simple_workflow = {
        "id": "test_workflow",
        "name": "Test Workflow",
        "nodes": [
            {
                "id": "trigger",
                "type": "ManualTrigger",
                "config": {},
                "inputs": {},
                "outputs": ["trigger_data"]
            },
            {
                "id": "content_gen",
                "type": "ContentGeneratorNode",
                "config": {
                    "platform": "instagram",
                    "content_type": "caption",
                    "prompt": "Create a motivational post about success"
                },
                "inputs": {},
                "outputs": ["content"]
            }
        ]
    }
    
    # Mock the load_workflow method for testing
    async def mock_load_workflow(workflow_id):
        return simple_workflow
    
    engine.load_workflow = mock_load_workflow
    
    try:
        result = await engine.execute_workflow("test_workflow", {"user_id": "test_user"})
        print(f"✅ Workflow executed successfully: {result}")
    except Exception as e:
        print(f"❌ Workflow execution failed: {e}")

def test_workflow_templates():
    """Test workflow templates"""
    print("\n📋 Testing Workflow Templates")
    print("=" * 50)
    
    print(f"✅ Found {len(WORKFLOW_TEMPLATES)} workflow templates:")
    
    for template_id, template in WORKFLOW_TEMPLATES.items():
        print(f"  - {template_id}: {template['name']} ({len(template['nodes'])} nodes)")
    
    # Test a specific template
    reel_template = WORKFLOW_TEMPLATES.get("instagram_reel")
    if reel_template:
        print(f"\n📱 Instagram Reel Template Details:")
        print(f"  Name: {reel_template['name']}")
        print(f"  Description: {reel_template['description']}")
        print(f"  Nodes: {len(reel_template['nodes'])}")
        for node in reel_template['nodes']:
            print(f"    - {node['id']} ({node['type']})")

def test_queue_manager():
    """Test queue manager"""
    print("\n📬 Testing Queue Manager")
    print("=" * 50)
    
    queue_manager = QueueManager()
    
    # Add jobs to queue
    job_id1 = queue_manager.add_to_queue("content_generation", {
        "type": "generate_content",
        "prompt": "Create a viral TikTok video"
    }, priority=8)
    
    job_id2 = queue_manager.add_to_queue("content_generation", {
        "type": "process_video", 
        "video_path": "/tmp/video.mp4"
    }, priority=5)
    
    print(f"✅ Added jobs to queue: {job_id1}, {job_id2}")
    
    # Get queue stats
    stats = queue_manager.get_queue_stats("content_generation")
    print(f"✅ Queue stats: {stats}")
    
    # Get next job
    next_job = queue_manager.get_next_job("content_generation")
    if next_job:
        print(f"✅ Next job: {next_job['id']} (priority: {next_job['priority']})")

async def test_scheduler():
    """Test content scheduler"""
    print("\n📅 Testing Content Scheduler")
    print("=" * 50)
    
    scheduler = ContentScheduler()
    
    # Schedule content
    scheduled_items = await scheduler.schedule_content(
        content_id="test_content_123",
        platforms=["instagram", "youtube"],
        schedule_type="optimal"
    )
    
    print(f"✅ Scheduled {len(scheduled_items)} items:")
    for item in scheduled_items:
        print(f"  - {item['platform']}: {item['scheduled_time']}")
    
    # Get scheduled content
    scheduled_content = scheduler.get_scheduled_content()
    print(f"✅ Found {len(scheduled_content)} scheduled items")

def test_connectors():
    """Test connectors"""
    print("\n🔌 Testing Connectors")
    print("=" * 50)
    
    # Test imports
    try:
        from connectors.ffmpeg import FFmpegConnector
        from connectors.ai_services import OpenAIConnector
        from connectors.social_media import SocialMediaConnector
        
        print("✅ All connectors imported successfully")
        
        # Test basic initialization
        ffmpeg = FFmpegConnector()
        ai = OpenAIConnector("test_key")
        social = SocialMediaConnector()
        
        print("✅ All connectors initialized successfully")
        
    except Exception as e:
        print(f"❌ Connector test failed: {e}")

def test_studio_components():
    """Test studio components"""
    print("\n🎨 Testing Studio Components")
    print("=" * 50)
    
    try:
        from studio.templates import ContentTemplateManager
        from studio.assets import AssetManager
        from studio.presets import PresetManager
        
        print("✅ All studio components imported successfully")
        
        # Test template manager
        template_manager = ContentTemplateManager()
        templates = template_manager.list_templates()
        print(f"✅ Template manager loaded {len(templates)} templates")
        
        # Test asset manager
        asset_manager = AssetManager()
        stats = asset_manager.get_storage_stats()
        print(f"✅ Asset manager initialized - {stats['total_assets']} assets")
        
        # Test preset manager
        preset_manager = PresetManager()
        presets = preset_manager.list_presets()
        print(f"✅ Preset manager loaded {len(presets)} presets")
        
    except Exception as e:
        print(f"❌ Studio components test failed: {e}")

async def main():
    """Run all tests"""
    print("🧪 Social Media Automation - Workflow Engine Tests")
    print("=" * 60)
    
    # Test workflow engine
    await test_workflow_engine()
    
    # Test templates
    test_workflow_templates()
    
    # Test queue manager
    test_queue_manager()
    
    # Test scheduler
    await test_scheduler()
    
    # Test connectors
    test_connectors()
    
    # Test studio components
    test_studio_components()
    
    print("\n🎉 All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())