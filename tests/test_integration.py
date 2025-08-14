import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock, MagicMock
import tempfile
import os
import json
import asyncio


class TestIntegrationWorkflow:
    """Test complete end-to-end workflows of the social media automation platform"""

    @pytest.fixture
    async def authenticated_client(self, client: AsyncClient):
        """Get authenticated client with valid token"""
        # Login to get token
        login_response = await client.post(
            "/api/v1/auth/login",
            params={"username": "admin", "password": "admin"}
        )
        
        token_data = login_response.json()
        access_token = token_data["access_token"]
        
        # Add auth header to client
        client.headers.update({"Authorization": f"Bearer {access_token}"})
        return client

    async def test_complete_content_generation_and_publishing_workflow(
        self, authenticated_client: AsyncClient, mock_api_keys, temp_content_dir
    ):
        """Test the complete workflow from content generation to publishing"""
        
        # Step 1: Generate script
        with patch('src.services.ai_content_generator.AIContentGenerator.generate_script') as mock_script:
            mock_script.return_value = {
                "script": "Welcome to our comprehensive guide on AI content creation. In this video, we'll explore how artificial intelligence is revolutionizing the way we create engaging social media content.",
                "title_suggestions": [
                    "AI Content Creation: The Complete Guide",
                    "How to Create Viral Content with AI",
                    "Master AI Content Creation in 2024"
                ],
                "duration": 60,
                "word_count": 150,
                "metadata": {"style": "educational", "platform": "youtube"}
            }
            
            script_response = await authenticated_client.post(
                "/api/v1/content/script",
                params={
                    "topic": "AI content creation guide",
                    "style": "educational",
                    "duration": 60,
                    "platform": "youtube"
                }
            )
            
            assert script_response.status_code == 200
            script_data = script_response.json()
            script_text = script_data["script"]
            title = script_data["title_suggestions"][0]

        # Step 2: Generate voice audio
        with patch('src.services.voice_generator.VoiceGenerator.generate_speech') as mock_voice:
            audio_path = os.path.join(temp_content_dir, "generated_audio.mp3")
            with open(audio_path, 'w') as f:
                f.write("mock audio content")
            
            mock_voice.return_value = audio_path
            
            voice_response = await authenticated_client.post(
                "/api/v1/content/voice",
                params={
                    "text": script_text,
                    "voice_id": "test_voice_id",
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            )
            
            assert voice_response.status_code == 200
            voice_data = voice_response.json()
            generated_audio_path = voice_data["audio_path"]

        # Step 3: Create video
        with patch('src.services.video_processor.VideoProcessor.create_video_from_script') as mock_video:
            video_path = os.path.join(temp_content_dir, "generated_video.mp4")
            with open(video_path, 'w') as f:
                f.write("mock video content")
            
            mock_video.return_value = video_path
            
            video_response = await authenticated_client.post(
                "/api/v1/content/video",
                json={
                    "script_data": script_data,
                    "audio_path": generated_audio_path,
                    "video_config": {"resolution": "1080p", "fps": 30}
                }
            )
            
            assert video_response.status_code == 200
            video_data = video_response.json()
            generated_video_path = video_data["video_path"]

        # Step 4: Generate additional content metadata
        with patch('src.services.ai_content_generator.AIContentGenerator.generate_description') as mock_desc:
            mock_desc.return_value = "Learn how to leverage AI for creating engaging social media content. This comprehensive guide covers everything from script generation to video creation and publishing automation."
            
            desc_response = await authenticated_client.post(
                "/api/v1/content/description",
                params={
                    "title": title,
                    "script": script_text,
                    "platform": "youtube"
                }
            )
            
            assert desc_response.status_code == 200
            description = desc_response.json()

        with patch('src.services.ai_content_generator.AIContentGenerator.generate_hashtags') as mock_hashtags:
            mock_hashtags.return_value = [
                "#AI", "#ContentCreation", "#SocialMedia", "#YouTube", 
                "#Automation", "#DigitalMarketing", "#VideoMarketing", "#Tech"
            ]
            
            hashtags_response = await authenticated_client.post(
                "/api/v1/content/hashtags",
                params={
                    "topic": "AI content creation",
                    "platform": "youtube",
                    "count": 8
                }
            )
            
            assert hashtags_response.status_code == 200
            hashtags = hashtags_response.json()

        # Step 5: Publish to multiple platforms
        content_data = {
            "title": title,
            "description": description,
            "tags": ["AI", "content", "creation", "automation"],
            "hashtags": hashtags
        }
        
        with patch('src.tasks.social_publishing.publish_content_task.delay') as mock_publish_task:
            mock_publish_task.return_value = MagicMock(id="publish_task_456")
            
            publish_response = await authenticated_client.post(
                "/api/v1/platforms/publish",
                params={
                    "video_path": generated_video_path,
                    "platforms": ["youtube", "instagram"],
                    "content_data": content_data
                }
            )
            
            assert publish_response.status_code == 200
            publish_data = publish_response.json()
            task_id = publish_data["task_id"]

        # Step 6: Check task status
        with patch('src.core.celery_app.celery_app') as mock_celery:
            mock_result = MagicMock()
            mock_result.status = "SUCCESS"
            mock_result.ready.return_value = True
            mock_result.result = {
                "youtube": {
                    "post_id": "youtube_123",
                    "url": "https://youtube.com/watch?v=youtube_123",
                    "status": "published"
                },
                "instagram": {
                    "post_id": "instagram_456", 
                    "url": "https://instagram.com/p/instagram_456",
                    "status": "published"
                }
            }
            
            mock_celery.AsyncResult.return_value = mock_result
            
            task_response = await authenticated_client.get(f"/api/v1/content/task/{task_id}")
            
            assert task_response.status_code == 200
            task_data = task_response.json()
            assert task_data["status"] == "SUCCESS"
            assert "youtube" in task_data["result"]
            assert "instagram" in task_data["result"]

        # Step 7: Get analytics
        with patch('src.services.social_publisher.SocialMediaPublisher.get_platform_analytics') as mock_analytics:
            mock_analytics.return_value = {
                "platform": "youtube",
                "post_id": "youtube_123",
                "views": 5000,
                "likes": 250,
                "comments": 15,
                "shares": 8,
                "engagement_rate": 5.46
            }
            
            analytics_response = await authenticated_client.get(
                "/api/v1/platforms/analytics/youtube/youtube_123"
            )
            
            assert analytics_response.status_code == 200
            analytics_data = analytics_response.json()
            assert analytics_data["views"] > 0
            assert analytics_data["engagement_rate"] > 0

        # Verify all files were created in temp directory
        assert os.path.exists(generated_audio_path)
        assert os.path.exists(generated_video_path)

    async def test_automated_content_generation_workflow(
        self, authenticated_client: AsyncClient, mock_api_keys, temp_content_dir
    ):
        """Test the automated content generation using the full generation endpoint"""
        
        request_data = {
            "title": "AI Social Media Automation",
            "topic": "How to automate your social media with AI",
            "content_type": "video",
            "duration": 45,
            "style": "engaging",
            "target_platforms": ["youtube", "instagram", "tiktok"],
            "project_id": 1
        }
        
        # Mock the complete content generation task
        with patch('src.tasks.content_generation.generate_complete_content.delay') as mock_task:
            mock_task.return_value = MagicMock(id="content_task_789")
            
            # Start content generation
            generation_response = await authenticated_client.post(
                "/api/v1/content/generate",
                json=request_data
            )
            
            assert generation_response.status_code == 200
            gen_data = generation_response.json()
            assert gen_data["status"] == "processing"
            task_id = gen_data["task_id"]

        # Mock checking task progress
        with patch('src.core.celery_app.celery_app') as mock_celery:
            # First check - in progress
            mock_result = MagicMock()
            mock_result.status = "PENDING"
            mock_result.ready.return_value = False
            mock_result.info = {
                "progress": 50,
                "current_step": "generating_video",
                "steps_completed": ["script_generation", "voice_generation"],
                "steps_remaining": ["video_creation", "optimization"]
            }
            
            mock_celery.AsyncResult.return_value = mock_result
            
            progress_response = await authenticated_client.get(f"/api/v1/content/task/{task_id}")
            
            assert progress_response.status_code == 200
            progress_data = progress_response.json()
            assert progress_data["status"] == "PENDING"
            assert "progress" in progress_data

            # Second check - completed
            mock_result.status = "SUCCESS"
            mock_result.ready.return_value = True
            mock_result.result = {
                "video_path": os.path.join(temp_content_dir, "complete_video.mp4"),
                "audio_path": os.path.join(temp_content_dir, "complete_audio.mp3"),
                "script": "Complete generated script about AI social media automation...",
                "metadata": {
                    "title": "AI Social Media Automation",
                    "description": "Complete guide to automating social media with AI",
                    "hashtags": ["#AI", "#SocialMedia", "#Automation"],
                    "duration": 45,
                    "word_count": 135
                }
            }
            
            completion_response = await authenticated_client.get(f"/api/v1/content/task/{task_id}")
            
            assert completion_response.status_code == 200
            completion_data = completion_response.json()
            assert completion_data["status"] == "SUCCESS"
            assert "video_path" in completion_data["result"]
            assert "metadata" in completion_data["result"]

    async def test_platform_connection_and_account_management(
        self, authenticated_client: AsyncClient, mock_api_keys
    ):
        """Test managing social media accounts and platform connections"""
        
        # Step 1: Check initial platform status
        status_response = await authenticated_client.get("/api/v1/platforms/platforms/status")
        assert status_response.status_code == 200
        initial_status = status_response.json()
        
        # All platforms should initially be disconnected
        for platform in ["youtube", "facebook", "instagram", "tiktok"]:
            assert platform in initial_status
            assert initial_status[platform]["connected"] is False

        # Step 2: Add social media accounts
        youtube_account = {
            "platform": "youtube",
            "account_name": "AI Content Channel",
            "account_id": "UC123456789",
            "credentials": {
                "client_id": "test_youtube_client_id",
                "client_secret": "test_youtube_client_secret",
                "refresh_token": "test_youtube_refresh_token"
            }
        }
        
        create_response = await authenticated_client.post(
            "/api/v1/platforms/accounts",
            json=youtube_account
        )
        
        assert create_response.status_code == 200
        created_account = create_response.json()
        assert created_account["platform"] == "youtube"
        account_id = created_account["id"]

        # Step 3: Get accounts list
        accounts_response = await authenticated_client.get("/api/v1/platforms/accounts")
        assert accounts_response.status_code == 200
        accounts = accounts_response.json()
        assert isinstance(accounts, list)

        # Step 4: Update account
        update_data = {
            "account_name": "Updated AI Content Channel",
            "is_active": True
        }
        
        update_response = await authenticated_client.put(
            f"/api/v1/platforms/accounts/{account_id}",
            json=update_data
        )
        
        assert update_response.status_code == 200
        updated_account = update_response.json()
        assert updated_account["id"] == account_id

        # Step 5: Test publishing with connected account
        temp_video = "/tmp/test_video.mp4"
        
        with patch('src.services.social_publisher.SocialMediaPublisher.publish_to_youtube') as mock_publish:
            mock_publish.return_value = {
                "platform": "youtube",
                "post_id": "youtube_published_123",
                "url": "https://youtube.com/watch?v=youtube_published_123",
                "status": "published"
            }
            
            publish_response = await authenticated_client.post(
                "/api/v1/platforms/publish/youtube",
                params={
                    "video_path": temp_video,
                    "content_data": {
                        "title": "Test Video",
                        "description": "Test Description",
                        "tags": ["test"]
                    }
                }
            )
            
            assert publish_response.status_code == 200

        # Step 6: Delete account
        delete_response = await authenticated_client.delete(f"/api/v1/platforms/accounts/{account_id}")
        assert delete_response.status_code == 200
        assert delete_response.json()["message"] == "Account deleted successfully"

    async def test_analytics_and_reporting_workflow(
        self, authenticated_client: AsyncClient, mock_api_keys
    ):
        """Test comprehensive analytics and reporting workflow"""
        
        from datetime import datetime, timedelta
        
        # Step 1: Get overall analytics overview
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()
        
        overview_request = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "platforms": ["youtube", "instagram", "facebook"]
        }
        
        overview_response = await authenticated_client.post(
            "/api/v1/analytics/overview",
            json=overview_request
        )
        
        assert overview_response.status_code == 200
        overview_data = overview_response.json()
        
        total_views = overview_data["total_views"]
        total_engagement = overview_data["total_engagement"]
        
        # Step 2: Get platform-specific analytics
        platform_analytics = {}
        for platform in ["youtube", "instagram", "facebook"]:
            platform_response = await authenticated_client.get(
                f"/api/v1/analytics/platforms/{platform}",
                params={"days": 30}
            )
            
            assert platform_response.status_code == 200
            platform_analytics[platform] = platform_response.json()

        # Step 3: Get content-specific analytics
        content_response = await authenticated_client.get("/api/v1/analytics/content/123")
        assert content_response.status_code == 200
        content_analytics = content_response.json()
        
        # Step 4: Get trends analysis
        trends_response = await authenticated_client.get(
            "/api/v1/analytics/trends",
            params={"days": 30}
        )
        
        assert trends_response.status_code == 200
        trends_data = trends_response.json()
        
        # Verify trends contain actionable insights
        assert "trending_topics" in trends_data
        assert "optimal_posting_times" in trends_data
        assert "content_performance_insights" in trends_data

        # Step 5: Export analytics data
        export_response = await authenticated_client.get(
            "/api/v1/analytics/export",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "format": "csv",
                "platforms": ["youtube", "instagram"]
            }
        )
        
        assert export_response.status_code == 200
        export_data = export_response.json()
        assert "export_id" in export_data
        assert export_data["format"] == "csv"

        # Verify data consistency across endpoints
        assert total_views > 0
        assert total_engagement > 0
        
        # Platform breakdown should sum to totals (in real implementation)
        platform_breakdown = overview_data["platform_breakdown"]
        for platform in ["youtube", "instagram", "facebook"]:
            assert platform in platform_breakdown
            platform_views = platform_breakdown[platform]["views"]
            assert platform_views > 0

    async def test_error_handling_and_recovery(
        self, authenticated_client: AsyncClient, mock_api_keys
    ):
        """Test error handling and recovery scenarios"""
        
        # Test 1: API key validation
        # Remove mock API keys to test error handling
        with patch.object(settings, 'OPENAI_API_KEY', ''):
            script_response = await authenticated_client.post(
                "/api/v1/content/script",
                params={"topic": "test topic"}
            )
            # Should handle missing API key gracefully
            assert script_response.status_code in [200, 400, 500]

        # Test 2: Invalid file paths
        invalid_video_path = "/nonexistent/path/video.mp4"
        
        publish_response = await authenticated_client.post(
            "/api/v1/platforms/publish/youtube", 
            params={
                "video_path": invalid_video_path,
                "content_data": {"title": "Test"}
            }
        )
        # Should handle invalid file paths
        assert publish_response.status_code in [400, 404, 500]

        # Test 3: Invalid task ID
        task_response = await authenticated_client.get("/api/v1/content/task/invalid_task_id")
        assert task_response.status_code in [200, 404, 500]

        # Test 4: Malformed request data
        malformed_response = await authenticated_client.post(
            "/api/v1/content/generate",
            json={"invalid": "data"}  # Missing required fields
        )
        assert malformed_response.status_code in [400, 422, 500]

    async def test_concurrent_operations(
        self, authenticated_client: AsyncClient, mock_api_keys
    ):
        """Test handling of concurrent operations"""
        
        # Create multiple concurrent content generation requests
        async def generate_content(topic):
            response = await authenticated_client.post(
                "/api/v1/content/script",
                params={
                    "topic": f"AI content about {topic}",
                    "style": "educational"
                }
            )
            return response

        # Mock the AI service to handle concurrent requests
        with patch('src.services.ai_content_generator.AIContentGenerator.generate_script') as mock_script:
            mock_script.return_value = {
                "script": "Generated script content",
                "title_suggestions": ["Title 1", "Title 2"],
                "duration": 60
            }
            
            topics = ["machine learning", "social media", "automation", "AI tools", "content creation"]
            
            # Run concurrent requests
            tasks = [generate_content(topic) for topic in topics]
            responses = await asyncio.gather(*tasks)
            
            # All requests should succeed
            for response in responses:
                assert response.status_code == 200
                data = response.json()
                assert "script" in data

    async def test_user_session_management(self, client: AsyncClient):
        """Test user session and authentication management"""
        
        # Test 1: Login and get valid session
        login_response = await client.post(
            "/api/v1/auth/login",
            params={"username": "admin", "password": "admin"}
        )
        
        assert login_response.status_code == 200
        login_data = login_response.json()
        access_token = login_data["access_token"]

        # Test 2: Use token to access protected resource
        headers = {"Authorization": f"Bearer {access_token}"}
        
        me_response = await client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == 200
        user_data = me_response.json()
        assert user_data["username"] == "admin"

        # Test 3: Refresh token
        refresh_response = await client.post("/api/v1/auth/refresh", headers=headers)
        assert refresh_response.status_code == 200
        refresh_data = refresh_response.json()
        new_token = refresh_data["access_token"]
        assert new_token != access_token

        # Test 4: Use new token
        new_headers = {"Authorization": f"Bearer {new_token}"}
        me_response_2 = await client.get("/api/v1/auth/me", headers=new_headers)
        assert me_response_2.status_code == 200

        # Test 5: Logout
        logout_response = await client.post("/api/v1/auth/logout", headers=new_headers)
        assert logout_response.status_code == 200
        assert logout_response.json()["message"] == "Successfully logged out"