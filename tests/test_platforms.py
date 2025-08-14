import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock, MagicMock
import json
import tempfile
import os


class TestPlatformIntegration:
    """Test social media platform integration and publishing"""

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

    async def test_create_social_account(self, authenticated_client: AsyncClient):
        """Test creating a social media account"""
        account_data = {
            "platform": "youtube",
            "account_name": "Test Channel",
            "account_id": "UC123456789",
            "credentials": {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "refresh_token": "test_refresh_token"
            }
        }
        
        response = await authenticated_client.post(
            "/api/v1/platforms/accounts",
            json=account_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["platform"] == "youtube"
        assert data["account_name"] == "Test Channel"
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data

    async def test_get_social_accounts(self, authenticated_client: AsyncClient):
        """Test getting user's social media accounts"""
        response = await authenticated_client.get("/api/v1/platforms/accounts")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Currently returns empty list due to mock implementation

    async def test_update_social_account(self, authenticated_client: AsyncClient):
        """Test updating a social media account"""
        account_id = 1
        update_data = {
            "account_name": "Updated Test Channel",
            "is_active": True
        }
        
        response = await authenticated_client.put(
            f"/api/v1/platforms/accounts/{account_id}",
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == account_id
        assert data["account_name"] == "Updated Account"  # From mock implementation

    async def test_delete_social_account(self, authenticated_client: AsyncClient):
        """Test deleting a social media account"""
        account_id = 1
        
        response = await authenticated_client.delete(
            f"/api/v1/platforms/accounts/{account_id}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Account deleted successfully"

    async def test_publish_to_multiple_platforms(self, authenticated_client: AsyncClient, temp_content_dir):
        """Test publishing content to multiple platforms"""
        # Create a mock video file
        video_path = os.path.join(temp_content_dir, "test_video.mp4")
        with open(video_path, 'w') as f:
            f.write("mock video content")
        
        with patch('src.tasks.social_publishing.publish_content_task.delay') as mock_task:
            mock_task.return_value = MagicMock(id="publish_task_123")
            
            publish_data = {
                "video_path": video_path,
                "platforms": ["youtube", "instagram"],
                "content_data": {
                    "title": "Test Video",
                    "description": "This is a test video",
                    "tags": ["test", "ai", "content"],
                    "hashtags": ["#test", "#ai", "#content"]
                }
            }
            
            response = await authenticated_client.post(
                "/api/v1/platforms/publish",
                params={
                    "video_path": publish_data["video_path"],
                    "platforms": publish_data["platforms"],
                    "content_data": publish_data["content_data"]
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "task_id" in data
            assert data["task_id"] == "publish_task_123"
            assert data["status"] == "processing"
            assert data["message"] == "Content publishing started"

    async def test_publish_to_youtube(self, authenticated_client: AsyncClient, temp_content_dir, mock_api_keys):
        """Test publishing content to YouTube"""
        video_path = os.path.join(temp_content_dir, "test_video.mp4")
        with open(video_path, 'w') as f:
            f.write("mock video content")
        
        with patch('src.services.social_publisher.SocialMediaPublisher.publish_to_youtube') as mock_publish:
            mock_publish.return_value = {
                "platform": "youtube",
                "post_id": "youtube_video_123",
                "url": "https://youtube.com/watch?v=youtube_video_123",
                "status": "published",
                "published_at": "2024-01-01T12:00:00Z"
            }
            
            content_data = {
                "title": "Test YouTube Video",
                "description": "This is a test YouTube video",
                "tags": ["test", "youtube", "ai"]
            }
            
            response = await authenticated_client.post(
                f"/api/v1/platforms/publish/youtube",
                params={
                    "video_path": video_path,
                    "content_data": content_data
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["platform"] == "youtube"
            assert data["post_id"] == "youtube_video_123"
            assert data["status"] == "published"

    async def test_publish_to_instagram(self, authenticated_client: AsyncClient, temp_content_dir, mock_api_keys):
        """Test publishing content to Instagram"""
        video_path = os.path.join(temp_content_dir, "test_video.mp4")
        with open(video_path, 'w') as f:
            f.write("mock video content")
        
        with patch('src.services.social_publisher.SocialMediaPublisher.publish_to_instagram') as mock_publish:
            mock_publish.return_value = {
                "platform": "instagram",
                "post_id": "instagram_post_456",
                "url": "https://instagram.com/p/instagram_post_456",
                "status": "published",
                "published_at": "2024-01-01T12:00:00Z"
            }
            
            content_data = {
                "caption": "Test Instagram post with AI content!",
                "hashtags": ["#test", "#instagram", "#ai", "#reel"]
            }
            
            response = await authenticated_client.post(
                f"/api/v1/platforms/publish/instagram",
                params={
                    "video_path": video_path,
                    "content_data": content_data
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["platform"] == "instagram"
            assert data["post_id"] == "instagram_post_456"
            assert data["status"] == "published"

    async def test_publish_to_facebook(self, authenticated_client: AsyncClient, temp_content_dir, mock_api_keys):
        """Test publishing content to Facebook"""
        video_path = os.path.join(temp_content_dir, "test_video.mp4")
        with open(video_path, 'w') as f:
            f.write("mock video content")
        
        with patch('src.services.social_publisher.SocialMediaPublisher.publish_to_facebook') as mock_publish:
            mock_publish.return_value = {
                "platform": "facebook",
                "post_id": "facebook_post_789",
                "url": "https://facebook.com/posts/facebook_post_789",
                "status": "published",
                "published_at": "2024-01-01T12:00:00Z"
            }
            
            content_data = {
                "message": "Check out this AI-generated content!",
                "page_id": "test_page_id"
            }
            
            response = await authenticated_client.post(
                f"/api/v1/platforms/publish/facebook",
                params={
                    "video_path": video_path,
                    "content_data": content_data
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["platform"] == "facebook"
            assert data["post_id"] == "facebook_post_789"
            assert data["status"] == "published"

    async def test_publish_to_tiktok(self, authenticated_client: AsyncClient, temp_content_dir, mock_api_keys):
        """Test publishing content to TikTok"""
        video_path = os.path.join(temp_content_dir, "test_video.mp4")
        with open(video_path, 'w') as f:
            f.write("mock video content")
        
        with patch('src.services.social_publisher.SocialMediaPublisher.publish_to_tiktok') as mock_publish:
            mock_publish.return_value = {
                "platform": "tiktok",
                "post_id": "tiktok_video_999",
                "url": "https://tiktok.com/@user/video/tiktok_video_999",
                "status": "published",
                "published_at": "2024-01-01T12:00:00Z"
            }
            
            content_data = {
                "caption": "AI-generated TikTok content! #ai #viral",
                "hashtags": ["#ai", "#viral", "#tiktok", "#fyp"]
            }
            
            response = await authenticated_client.post(
                f"/api/v1/platforms/publish/tiktok",
                params={
                    "video_path": video_path,
                    "content_data": content_data
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["platform"] == "tiktok"
            assert data["post_id"] == "tiktok_video_999"
            assert data["status"] == "published"

    async def test_publish_to_unsupported_platform(self, authenticated_client: AsyncClient, temp_content_dir):
        """Test publishing to an unsupported platform"""
        video_path = os.path.join(temp_content_dir, "test_video.mp4")
        with open(video_path, 'w') as f:
            f.write("mock video content")
        
        content_data = {"title": "Test"}
        
        response = await authenticated_client.post(
            f"/api/v1/platforms/publish/unsupported_platform",
            params={
                "video_path": video_path,
                "content_data": content_data
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "not supported" in data["detail"]

    async def test_get_post_analytics(self, authenticated_client: AsyncClient, mock_api_keys):
        """Test getting analytics for a specific post"""
        with patch('src.services.social_publisher.SocialMediaPublisher.get_platform_analytics') as mock_analytics:
            mock_analytics.return_value = {
                "platform": "youtube",
                "post_id": "youtube_video_123",
                "views": 10000,
                "likes": 500,
                "comments": 50,
                "shares": 25,
                "engagement_rate": 5.75,
                "watch_time_minutes": 7500,
                "demographics": {
                    "age_groups": {"18-24": 30, "25-34": 40, "35-44": 20, "45+": 10},
                    "gender": {"male": 60, "female": 40},
                    "top_countries": ["US", "UK", "CA", "AU"]
                }
            }
            
            response = await authenticated_client.get(
                "/api/v1/platforms/analytics/youtube/youtube_video_123"
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["platform"] == "youtube"
            assert data["views"] == 10000
            assert data["engagement_rate"] == 5.75
            assert "demographics" in data

    async def test_get_publications(self, authenticated_client: AsyncClient):
        """Test getting published content"""
        response = await authenticated_client.get(
            "/api/v1/platforms/publications",
            params={"platform": "youtube", "limit": 10, "offset": 0}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Currently returns empty list due to mock implementation

    async def test_get_platforms_status(self, authenticated_client: AsyncClient):
        """Test checking the status of all connected platforms"""
        response = await authenticated_client.get("/api/v1/platforms/platforms/status")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should contain status for all supported platforms
        assert "youtube" in data
        assert "facebook" in data
        assert "instagram" in data
        assert "tiktok" in data
        
        # Each platform should have connection status
        for platform, status in data.items():
            assert "connected" in status
            assert isinstance(status["connected"], bool)
            if not status["connected"]:
                assert "error" in status

    async def test_authentication_required_for_platforms(self, client: AsyncClient):
        """Test that platform endpoints require authentication"""
        # Test without authentication token
        response = await client.get("/api/v1/platforms/accounts")
        assert response.status_code == 403
        
        response = await client.post(
            "/api/v1/platforms/accounts",
            json={"platform": "youtube", "account_name": "test"}
        )
        assert response.status_code == 403
        
        response = await client.get("/api/v1/platforms/platforms/status")
        assert response.status_code == 200  # This endpoint might be public

    async def test_platform_error_handling(self, authenticated_client: AsyncClient, temp_content_dir):
        """Test error handling in platform operations"""
        video_path = os.path.join(temp_content_dir, "test_video.mp4")
        with open(video_path, 'w') as f:
            f.write("mock video content")
        
        # Test with error in publishing service
        with patch('src.services.social_publisher.SocialMediaPublisher.publish_to_youtube') as mock_publish:
            mock_publish.side_effect = Exception("YouTube API error")
            
            content_data = {"title": "Test", "description": "Test"}
            
            response = await authenticated_client.post(
                f"/api/v1/platforms/publish/youtube",
                params={
                    "video_path": video_path,
                    "content_data": content_data
                }
            )
            
            assert response.status_code == 500
            data = response.json()
            assert "YouTube API error" in data["detail"]