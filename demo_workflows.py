#!/usr/bin/env python3
"""
Demonstration of the workflow engine capabilities
This shows how the workflow system would be used in practice
"""

import asyncio
import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from workflows.engine import WorkflowEngine
from workflows.nodes.processors import *
from workflows.nodes.triggers import *
from workflows.templates import WORKFLOW_TEMPLATES
from automation.scheduler import ContentScheduler
from studio.templates import ContentTemplateManager
from studio.presets import PresetManager

async def demo_instagram_reel_workflow():
    """Demonstrate Instagram Reel creation workflow"""
    print("\n🎬 DEMO: Instagram Reel Creation Workflow")
    print("=" * 60)
    
    # Initialize workflow engine
    engine = WorkflowEngine()
    
    # Register all node types
    engine.register_node_type("ManualTrigger", ManualTrigger)
    engine.register_node_type("ContentGeneratorNode", ContentGeneratorNode)
    engine.register_node_type("VideoProcessorNode", VideoProcessorNode)
    engine.register_node_type("SocialMediaPostNode", SocialMediaPostNode)
    
    # Use the Instagram Reel template
    workflow = WORKFLOW_TEMPLATES["instagram_reel"]
    
    # Mock load workflow
    async def load_workflow(workflow_id):
        return workflow
    
    engine.load_workflow = load_workflow
    
    # Execution context
    context = {
        "user_id": "content_creator_123",
        "topic": "productivity tips",
        "video_path": "/tmp/source_video.mp4",
        "current_time": "2024-08-14T10:00:00Z"
    }
    
    print(f"📋 Workflow: {workflow['name']}")
    print(f"📝 Description: {workflow['description']}")
    print(f"🔢 Nodes: {len(workflow['nodes'])}")
    print(f"🎯 Topic: {context['topic']}")
    
    # Execute workflow
    try:
        result = await engine.execute_workflow("instagram_reel", context)
        
        print("\n✅ Workflow executed successfully!")
        print("\n📊 Results:")
        for node_id, node_result in result.items():
            print(f"  🔸 {node_id}:")
            for key, value in node_result.items():
                if isinstance(value, str) and len(value) > 50:
                    value = value[:50] + "..."
                print(f"    - {key}: {value}")
    
    except Exception as e:
        print(f"❌ Workflow execution failed: {e}")

async def demo_multi_platform_workflow():
    """Demonstrate multi-platform publishing workflow"""
    print("\n🌐 DEMO: Multi-Platform Publishing Workflow")
    print("=" * 60)
    
    # Initialize workflow engine
    engine = WorkflowEngine()
    
    # Register node types
    engine.register_node_type("ContentGeneratorNode", ContentGeneratorNode)
    engine.register_node_type("BatchProcessorNode", BatchProcessorNode)
    engine.register_node_type("MultiPlatformPostNode", MultiPlatformPostNode)
    
    # Use multi-platform template
    workflow = WORKFLOW_TEMPLATES["multi_platform"]
    
    async def load_workflow(workflow_id):
        return workflow
    
    engine.load_workflow = load_workflow
    
    context = {
        "topic": "sustainable living",
        "target_platforms": ["instagram", "tiktok", "youtube"],
        "content_style": "educational"
    }
    
    print(f"📋 Workflow: {workflow['name']}")
    print(f"🎯 Topic: {context['topic']}")
    print(f"📱 Platforms: {', '.join(context['target_platforms'])}")
    
    # Execute workflow
    try:
        result = await engine.execute_workflow("multi_platform", context)
        
        print("\n✅ Multi-platform workflow executed!")
        print("\n📊 Publishing Results:")
        
        if "multi_post" in result and "post_results" in result["multi_post"]:
            for post_result in result["multi_post"]["post_results"]:
                platform = post_result.get("platform", "unknown")
                status = post_result.get("status", "unknown")
                print(f"  📱 {platform}: {status}")
    
    except Exception as e:
        print(f"❌ Multi-platform workflow failed: {e}")

async def demo_content_scheduling():
    """Demonstrate content scheduling capabilities"""
    print("\n📅 DEMO: Content Scheduling System")
    print("=" * 60)
    
    scheduler = ContentScheduler()
    
    # Schedule content for optimal times
    print("🕐 Scheduling content for optimal posting times...")
    
    scheduled_items = await scheduler.schedule_content(
        content_id="demo_content_001",
        platforms=["instagram", "youtube", "tiktok"],
        schedule_type="optimal"
    )
    
    print(f"✅ Scheduled {len(scheduled_items)} posts:")
    for item in scheduled_items:
        platform = item["platform"]
        time = item["scheduled_time"]
        print(f"  📱 {platform}: {time}")
    
    # Schedule recurring content
    print("\n🔄 Setting up recurring content schedule...")
    
    recurring_items = await scheduler.schedule_content(
        content_id="demo_recurring_001",
        platforms=["instagram"],
        schedule_type="recurring",
        recurrence={
            "frequency": "daily",
            "interval": 1,
            "start_time": "2024-08-14T09:00:00Z",
            "end_date": "2024-08-21T09:00:00Z"
        }
    )
    
    print(f"✅ Set up recurring schedule: {len(recurring_items)} items")

def demo_template_system():
    """Demonstrate template management system"""
    print("\n📋 DEMO: Template Management System")
    print("=" * 60)
    
    template_manager = ContentTemplateManager()
    
    # List available templates
    templates = template_manager.list_templates()
    print(f"📚 Available templates: {len(templates)}")
    
    for template in templates:
        print(f"  📄 {template['name']} ({template['platform']}, {template['type']})")
    
    # Create custom template
    print("\n✨ Creating custom template...")
    
    custom_template = {
        "name": "Motivational Quote Post",
        "platform": "instagram",
        "type": "post",
        "template": {
            "quote": '"{quote}"',
            "author": "- {author}",
            "caption": "{quote}\n\n- {author}\n\n{motivation_hashtags}",
            "hashtags": ["#motivation", "#quotes", "#inspiration", "{topic}"]
        },
        "variables": ["quote", "author", "motivation_hashtags", "topic"]
    }
    
    template_id = template_manager.create_template(custom_template)
    print(f"✅ Created template: {template_id}")
    
    # Render template with variables
    rendered = template_manager.render_template(template_id, {
        "quote": "The only way to do great work is to love what you do",
        "author": "Steve Jobs",
        "motivation_hashtags": "#mondaymotivation #success",
        "topic": "entrepreneur"
    })
    
    print(f"📝 Rendered template:")
    print(f"  Caption: {rendered['content']['caption']}")

def demo_preset_system():
    """Demonstrate preset management system"""
    print("\n⚙️ DEMO: Preset Management System")
    print("=" * 60)
    
    preset_manager = PresetManager()
    
    # List available presets
    presets = preset_manager.list_presets()
    print(f"🎛️ Available presets: {len(presets)}")
    
    for preset in presets:
        print(f"  ⚙️ {preset['name']} ({preset['platform']}, {preset['type']})")
    
    # Apply a preset
    print("\n🎯 Applying 'Viral Reel Generator' preset...")
    
    applied_preset = preset_manager.apply_preset("viral_reel", {
        "topic": "AI automation",
        "target_audience": "tech enthusiasts"
    })
    
    print(f"✅ Applied preset: {applied_preset['preset_name']}")
    print(f"📱 Platform: {applied_preset['platform']}")
    print(f"🎨 Tone: {applied_preset['config'].get('tone', 'N/A')}")
    print(f"🔥 Hooks: {applied_preset['config'].get('hooks', [])}")
    
    # Get recommendations
    print("\n💡 Getting preset recommendations...")
    
    recommendations = preset_manager.get_preset_recommendations({
        "platform": "youtube",
        "content_type": "educational",
        "experience_level": "beginner"
    })
    
    print(f"📋 Found {len(recommendations)} recommendations:")
    for rec in recommendations[:3]:
        score = rec.get("recommendation_score", 0)
        print(f"  💡 {rec['name']} (score: {score})")

async def main():
    """Run all demonstrations"""
    print("🎭 Social Media Automation - Workflow Engine Demo")
    print("=" * 70)
    print("This demonstration shows the capabilities of the implemented")
    print("workflow engine for social media automation.")
    print("=" * 70)
    
    # Workflow demos
    await demo_instagram_reel_workflow()
    await demo_multi_platform_workflow()
    await demo_content_scheduling()
    
    # Management system demos
    demo_template_system()
    demo_preset_system()
    
    print("\n" + "=" * 70)
    print("🎉 Demo completed! The workflow engine is ready for production use.")
    print("🚀 Next steps:")
    print("  1. Install dependencies: pip install -r requirements.txt")
    print("  2. Set up external services (FFmpeg, Redis, OpenAI API)")
    print("  3. Configure database connections")
    print("  4. Start the API server: uvicorn src.main:app --reload")
    print("  5. Access workflow API at http://localhost:8000/docs")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())