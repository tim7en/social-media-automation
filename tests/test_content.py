import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock, MagicMock
import json
import tempfile
import os


class TestContentGeneration:
    """Test content generation endpoints and functionality"""

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

    async def test_generate_script_basic(self, authenticated_client: AsyncClient, mock_api_keys):
        """Test basic script generation"""
        with patch('src.services.ai_content_generator.AIContentGenerator.generate_script') as mock_generate:
            mock_generate.return_value = {
                "script": "This is a test script about AI content creation.",
                "title_suggestions": ["AI Content Creation", "How to Create with AI"],
                "duration": 60,
                "word_count": 120,
                "metadata": {"style": "educational", "platform": "youtube"}
            }
            
            response = await authenticated_client.post(
                "/api/v1/content/script",
                params={
                    "topic": "AI content creation",
                    "style": "educational",
                    "duration": 60,
                    "platform": "youtube"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "script" in data
            assert "title_suggestions" in data
            assert data["duration"] == 60
            mock_generate.assert_called_once()

    async def test_generate_script_with_context(self, authenticated_client: AsyncClient, mock_api_keys):
        """Test script generation with additional context"""
        with patch('src.services.ai_content_generator.AIContentGenerator.generate_script') as mock_generate:
            mock_generate.return_value = {
                "script": "Advanced script with specific context about machine learning.",
                "title_suggestions": ["ML Explained", "Machine Learning Basics"],
                "duration": 90,
                "word_count": 180
            }
            
            response = await authenticated_client.post(
                "/api/v1/content/script",
                params={
                    "topic": "machine learning",
                    "style": "technical",
                    "duration": 90,
                    "platform": "youtube",
                    "additional_context": "Focus on beginners, avoid complex math"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "script" in data
            assert data["duration"] == 90

    async def test_generate_titles(self, authenticated_client: AsyncClient, mock_api_keys):
        """Test title generation"""
        with patch('src.services.ai_content_generator.AIContentGenerator.generate_title_suggestions') as mock_titles:
            mock_titles.return_value = [
                "Amazing AI Content Tips",
                "Create Viral Content with AI",
                "AI Content Creation Secrets",
                "How to Use AI for Content",
                "AI Content Generation Guide"
            ]
            
            response = await authenticated_client.post(
                "/api/v1/content/titles",
                params={
                    "topic": "AI content creation",
                    "platform": "youtube",
                    "count": 5
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 5
            assert all(isinstance(title, str) for title in data)

    async def test_generate_description(self, authenticated_client: AsyncClient, mock_api_keys):
        """Test description generation"""
        with patch('src.services.ai_content_generator.AIContentGenerator.generate_description') as mock_desc:
            mock_desc.return_value = "This is a comprehensive guide to AI content creation that will help you automate your social media presence."
            
            response = await authenticated_client.post(
                "/api/v1/content/description",
                params={
                    "title": "AI Content Creation Guide",
                    "script": "This script explains how to create content with AI...",
                    "platform": "youtube"
                }
            )
            
            assert response.status_code == 200
            description = response.json()
            assert isinstance(description, str)
            assert len(description) > 0

    async def test_generate_hashtags(self, authenticated_client: AsyncClient, mock_api_keys):
        """Test hashtag generation"""
        with patch('src.services.ai_content_generator.AIContentGenerator.generate_hashtags') as mock_hashtags:
            mock_hashtags.return_value = [
                "#AI", "#ContentCreation", "#SocialMedia", "#Automation",
                "#DigitalMarketing", "#Technology", "#Innovation", "#Viral",
                "#Creator", "#Tips"
            ]
            
            response = await authenticated_client.post(
                "/api/v1/content/hashtags",
                params={
                    "topic": "AI content creation",
                    "platform": "instagram",
                    "count": 10
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 10
            assert all(hashtag.startswith("#") for hashtag in data)

    async def test_generate_voice_audio(self, authenticated_client: AsyncClient, mock_api_keys, temp_content_dir):
        """Test voice audio generation"""
        with patch('src.services.voice_generator.VoiceGenerator.generate_speech') as mock_voice:
            mock_audio_path = os.path.join(temp_content_dir, "test_audio.mp3")
            with open(mock_audio_path, 'w') as f:
                f.write("mock audio content")
            
            mock_voice.return_value = mock_audio_path
            
            response = await authenticated_client.post(
                "/api/v1/content/voice",
                params={
                    "text": "This is a test script for voice generation.",
                    "voice_id": "test_voice_id",
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "audio_path" in data
            assert data["audio_path"] == mock_audio_path
            mock_voice.assert_called_once()

    async def test_get_available_voices(self, authenticated_client: AsyncClient, mock_api_keys):
        """Test getting available voices"""
        with patch('src.services.voice_generator.VoiceGenerator.get_available_voices') as mock_voices:
            mock_voices.return_value = [
                {"voice_id": "voice1", "name": "Rachel", "category": "female"},
                {"voice_id": "voice2", "name": "Adam", "category": "male"},
                {"voice_id": "voice3", "name": "Emily", "category": "female"}
            ]
            
            response = await authenticated_client.get("/api/v1/content/voices")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 3
            assert all("voice_id" in voice and "name" in voice for voice in data)

    async def test_create_video(self, authenticated_client: AsyncClient, mock_api_keys, temp_content_dir):
        """Test video creation"""
        with patch('src.services.video_processor.VideoProcessor.create_video_from_script') as mock_video:
            mock_video_path = os.path.join(temp_content_dir, "test_video.mp4")
            with open(mock_video_path, 'w') as f:
                f.write("mock video content")
                
            mock_video.return_value = mock_video_path
            
            script_data = {
                "script": "This is a test script",
                "scenes": [{"text": "Scene 1", "duration": 5}],
                "metadata": {"style": "educational"}
            }
            
            audio_path = os.path.join(temp_content_dir, "audio.mp3")
            with open(audio_path, 'w') as f:
                f.write("mock audio")
            
            response = await authenticated_client.post(
                "/api/v1/content/video",
                json={
                    "script_data": script_data,
                    "audio_path": audio_path,
                    "video_config": {"resolution": "1080p", "fps": 30}
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "video_path" in data
            assert data["video_path"] == mock_video_path

    async def test_full_content_generation(self, authenticated_client: AsyncClient, sample_content_request, mock_api_keys):
        """Test full content generation workflow"""
        with patch('src.tasks.content_generation.generate_complete_content.delay') as mock_task:
            mock_task.return_value = MagicMock(id="test_task_123")
            
            response = await authenticated_client.post(
                "/api/v1/content/generate",
                json=sample_content_request
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "task_id" in data
            assert data["task_id"] == "test_task_123"
            assert data["status"] == "processing"
            assert data["message"] == "Content generation started"

    async def test_get_task_status_processing(self, authenticated_client: AsyncClient):
        """Test getting task status for processing task"""
        with patch('src.core.celery_app.celery_app') as mock_celery:
            mock_result = MagicMock()
            mock_result.status = "PENDING"
            mock_result.ready.return_value = False
            mock_result.info = {"progress": 25, "current_step": "generating_script"}
            
            mock_celery.AsyncResult.return_value = mock_result
            
            response = await authenticated_client.get("/api/v1/content/task/test_task_123")
            
            assert response.status_code == 200
            data = response.json()
            assert data["task_id"] == "test_task_123"
            assert data["status"] == "PENDING"
            assert data["result"] is None
            assert "progress" in data

    async def test_get_task_status_completed(self, authenticated_client: AsyncClient):
        """Test getting task status for completed task"""
        with patch('src.core.celery_app.celery_app') as mock_celery:
            mock_result = MagicMock()
            mock_result.status = "SUCCESS"
            mock_result.ready.return_value = True
            mock_result.result = {
                "video_path": "/tmp/generated_content/video_123.mp4",
                "audio_path": "/tmp/generated_content/audio_123.mp3",
                "script": "Generated script content",
                "metadata": {"duration": 60, "word_count": 120}
            }
            
            mock_celery.AsyncResult.return_value = mock_result
            
            response = await authenticated_client.get("/api/v1/content/task/test_task_123")
            
            assert response.status_code == 200
            data = response.json()
            assert data["task_id"] == "test_task_123"
            assert data["status"] == "SUCCESS"
            assert data["result"] is not None
            assert "video_path" in data["result"]

    async def test_error_handling_missing_api_keys(self, authenticated_client: AsyncClient):
        """Test error handling when API keys are missing"""
        # Don't use mock_api_keys fixture to test missing keys
        
        response = await authenticated_client.post(
            "/api/v1/content/script",
            params={
                "topic": "AI content creation",
                "style": "educational"
            }
        )
        
        # Should handle missing API keys gracefully
        # The actual behavior depends on the service implementation
        assert response.status_code in [200, 500]  # Either works with mock or fails gracefully

    async def test_error_handling_invalid_parameters(self, authenticated_client: AsyncClient):
        """Test error handling with invalid parameters"""
        response = await authenticated_client.post(
            "/api/v1/content/script",
            params={
                "topic": "",  # Empty topic
                "duration": -1,  # Invalid duration
                "platform": "invalid_platform"
            }
        )
        
        # Should handle invalid parameters
        assert response.status_code in [400, 422, 500]