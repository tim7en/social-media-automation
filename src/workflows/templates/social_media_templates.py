"""Pre-built workflow templates for common social media tasks"""

INSTAGRAM_REEL_WORKFLOW = {
    "id": "instagram-reel-template",
    "name": "Instagram Reel Creator",
    "description": "Create Instagram Reel with AI-generated content",
    "nodes": [
        {
            "id": "content_gen",
            "type": "ContentGeneratorNode",
            "config": {
                "platform": "instagram",
                "content_type": "reel",
                "prompt": "Create engaging reel script about {topic}"
            },
            "inputs": {},
            "outputs": ["content"]
        },
        {
            "id": "video_resize",
            "type": "VideoProcessorNode",
            "config": {
                "operation": "resize",
                "platform": "instagram_reel"
            },
            "inputs": {
                "video_path": "$trigger.video_path"
            },
            "outputs": ["video_path"]
        },
        {
            "id": "generate_captions",
            "type": "ContentGeneratorNode",
            "config": {
                "platform": "instagram",
                "content_type": "caption"
            },
            "inputs": {
                "context": "$content_gen.content"
            },
            "outputs": ["caption"]
        },
        {
            "id": "post_to_instagram",
            "type": "SocialMediaPostNode",
            "config": {
                "platform": "instagram",
                "post_type": "reel"
            },
            "inputs": {
                "video_path": "$video_resize.video_path",
                "caption": "$generate_captions.caption"
            },
            "outputs": ["post_id", "url"]
        }
    ]
}

MULTI_PLATFORM_WORKFLOW = {
    "id": "multi-platform-template",
    "name": "Multi-Platform Content Publisher",
    "description": "Publish content to multiple platforms simultaneously",
    "nodes": [
        {
            "id": "content_gen",
            "type": "ContentGeneratorNode",
            "config": {
                "prompt": "Create content about {topic}"
            },
            "inputs": {},
            "outputs": ["content"]
        },
        {
            "id": "platform_optimizer",
            "type": "BatchProcessorNode",
            "config": {
                "node_type": "PlatformOptimizerNode",
                "platforms": ["instagram", "tiktok", "youtube"]
            },
            "inputs": {
                "content": "$content_gen.content"
            },
            "outputs": ["optimized_content"]
        },
        {
            "id": "multi_post",
            "type": "MultiPlatformPostNode",
            "config": {
                "platforms": ["instagram", "tiktok", "youtube"],
                "schedule": "immediate"
            },
            "inputs": {
                "content": "$platform_optimizer.optimized_content"
            },
            "outputs": ["post_results"]
        }
    ]
}

CONTENT_REPURPOSE_WORKFLOW = {
    "id": "content-repurpose-template",
    "name": "Content Repurposing Pipeline",
    "description": "Transform long-form content into multiple short-form pieces",
    "nodes": [
        {
            "id": "extract_audio",
            "type": "VideoProcessorNode",
            "config": {
                "operation": "extract_audio"
            },
            "inputs": {
                "video_path": "$trigger.video_path"
            },
            "outputs": ["audio_path"]
        },
        {
            "id": "transcribe",
            "type": "TranscriptionNode",
            "config": {
                "language": "auto"
            },
            "inputs": {
                "audio_path": "$extract_audio.audio_path"
            },
            "outputs": ["transcript"]
        },
        {
            "id": "generate_clips",
            "type": "ContentGeneratorNode",
            "config": {
                "prompt": "Identify 5 best 30-second clips from this transcript"
            },
            "inputs": {
                "transcript": "$transcribe.transcript"
            },
            "outputs": ["clips"]
        },
        {
            "id": "create_shorts",
            "type": "BatchProcessorNode",
            "config": {
                "node_type": "VideoClipperNode"
            },
            "inputs": {
                "clips": "$generate_clips.clips",
                "video_path": "$trigger.video_path"
            },
            "outputs": ["short_videos"]
        }
    ]
}

SCHEDULED_CONTENT_WORKFLOW = {
    "id": "scheduled-content-template",
    "name": "Scheduled Content Generator",
    "description": "Generate and schedule content automatically",
    "nodes": [
        {
            "id": "schedule_trigger",
            "type": "ScheduleTrigger",
            "config": {
                "schedule_time": "daily_9am"
            },
            "inputs": {},
            "outputs": ["trigger_data"]
        },
        {
            "id": "content_check",
            "type": "ExistsCondition",
            "config": {
                "field_name": "topic",
                "check_empty": True
            },
            "inputs": {
                "topic": "$schedule_trigger.topic"
            },
            "outputs": ["condition_result"]
        },
        {
            "id": "generate_content",
            "type": "ContentGeneratorNode",
            "config": {
                "platform": "instagram",
                "content_type": "post"
            },
            "inputs": {
                "topic": "$schedule_trigger.topic"
            },
            "outputs": ["content"]
        },
        {
            "id": "create_thumbnail",
            "type": "ImageProcessorNode",
            "config": {
                "operation": "create_thumbnail",
                "width": 1080,
                "height": 1080
            },
            "inputs": {
                "text": "$generate_content.content"
            },
            "outputs": ["image_path"]
        },
        {
            "id": "schedule_post",
            "type": "SocialMediaPostNode",
            "config": {
                "platform": "instagram",
                "schedule_time": "optimal"
            },
            "inputs": {
                "image_path": "$create_thumbnail.image_path",
                "caption": "$generate_content.content"
            },
            "outputs": ["post_id"]
        }
    ]
}

ANALYTICS_WORKFLOW = {
    "id": "analytics-workflow-template",
    "name": "Analytics Collection and Reporting",
    "description": "Collect analytics data and generate reports",
    "nodes": [
        {
            "id": "schedule_trigger",
            "type": "ScheduleTrigger",
            "config": {
                "schedule_time": "daily_8pm"
            },
            "inputs": {},
            "outputs": ["trigger_data"]
        },
        {
            "id": "collect_instagram_analytics",
            "type": "DatabaseAction",
            "config": {
                "operation": "select",
                "table": "publications",
                "filter": {"platform": "instagram", "date": "today"}
            },
            "inputs": {},
            "outputs": ["instagram_data"]
        },
        {
            "id": "collect_youtube_analytics",
            "type": "DatabaseAction",
            "config": {
                "operation": "select",
                "table": "publications",
                "filter": {"platform": "youtube", "date": "today"}
            },
            "inputs": {},
            "outputs": ["youtube_data"]
        },
        {
            "id": "generate_report",
            "type": "ContentGeneratorNode",
            "config": {
                "prompt": "Generate a daily analytics report based on the following data"
            },
            "inputs": {
                "instagram_data": "$collect_instagram_analytics.instagram_data",
                "youtube_data": "$collect_youtube_analytics.youtube_data"
            },
            "outputs": ["report"]
        },
        {
            "id": "send_report",
            "type": "SendEmailAction",
            "config": {
                "recipient": "admin@example.com",
                "subject": "Daily Analytics Report",
                "template": "analytics_report"
            },
            "inputs": {
                "report_data": "$generate_report.report"
            },
            "outputs": ["email_sent"]
        }
    ]
}

CONTENT_MODERATION_WORKFLOW = {
    "id": "content-moderation-template",
    "name": "Content Moderation Pipeline",
    "description": "Review and moderate content before publishing",
    "nodes": [
        {
            "id": "content_upload",
            "type": "ContentUploadTrigger",
            "config": {},
            "inputs": {},
            "outputs": ["file_path", "file_type"]
        },
        {
            "id": "content_length_check",
            "type": "ContentLengthCondition",
            "config": {
                "content_field": "caption",
                "min_length": 10,
                "max_length": 2200
            },
            "inputs": {
                "caption": "$content_upload.caption"
            },
            "outputs": ["length_valid"]
        },
        {
            "id": "ai_content_analysis",
            "type": "ContentGeneratorNode",
            "config": {
                "prompt": "Analyze this content for appropriateness and compliance"
            },
            "inputs": {
                "content": "$content_upload.caption"
            },
            "outputs": ["analysis"]
        },
        {
            "id": "approval_condition",
            "type": "ComparisonCondition",
            "config": {
                "left_field": "analysis.score",
                "operator": "greater_than",
                "right_value": 0.8
            },
            "inputs": {
                "analysis": "$ai_content_analysis.analysis"
            },
            "outputs": ["approved"]
        },
        {
            "id": "auto_publish",
            "type": "SocialMediaPostNode",
            "config": {
                "platform": "instagram"
            },
            "inputs": {
                "file_path": "$content_upload.file_path",
                "caption": "$content_upload.caption"
            },
            "outputs": ["post_id"]
        },
        {
            "id": "flag_for_review",
            "type": "SlackNotificationAction",
            "config": {
                "channel": "#content-review",
                "message": "Content flagged for manual review: {file_path}"
            },
            "inputs": {
                "file_path": "$content_upload.file_path"
            },
            "outputs": ["notification_sent"]
        }
    ]
}

# Export all templates
WORKFLOW_TEMPLATES = {
    "instagram_reel": INSTAGRAM_REEL_WORKFLOW,
    "multi_platform": MULTI_PLATFORM_WORKFLOW,
    "content_repurpose": CONTENT_REPURPOSE_WORKFLOW,
    "scheduled_content": SCHEDULED_CONTENT_WORKFLOW,
    "analytics": ANALYTICS_WORKFLOW,
    "content_moderation": CONTENT_MODERATION_WORKFLOW
}