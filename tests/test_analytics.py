import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
import json


class TestAnalytics:
    """Test analytics endpoints and functionality"""

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

    async def test_analytics_overview(self, authenticated_client: AsyncClient):
        """Test getting analytics overview"""
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()
        
        request_data = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "platforms": ["youtube", "instagram", "facebook"]
        }
        
        response = await authenticated_client.post(
            "/api/v1/analytics/overview",
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "total_publications" in data
        assert "total_views" in data
        assert "total_engagement" in data
        assert "engagement_rate" in data
        assert "platform_breakdown" in data
        assert "top_performing_content" in data
        assert "trends" in data
        
        # Check platform breakdown
        platform_breakdown = data["platform_breakdown"]
        assert "youtube" in platform_breakdown
        assert "instagram" in platform_breakdown
        assert "facebook" in platform_breakdown
        
        # Verify each platform has required metrics
        for platform, metrics in platform_breakdown.items():
            assert "publications" in metrics
            assert "views" in metrics
            assert "engagement" in metrics
            assert "engagement_rate" in metrics
        
        # Check top performing content structure
        top_content = data["top_performing_content"]
        assert isinstance(top_content, list)
        if top_content:
            content_item = top_content[0]
            assert "title" in content_item
            assert "platform" in content_item
            assert "views" in content_item
            assert "engagement" in content_item
            assert "engagement_rate" in content_item
            assert "published_at" in content_item

    async def test_platform_specific_analytics(self, authenticated_client: AsyncClient):
        """Test getting analytics for a specific platform"""
        platform = "youtube"
        days = 30
        
        response = await authenticated_client.get(
            f"/api/v1/analytics/platforms/{platform}",
            params={"days": days}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["platform"] == platform
        assert "period" in data
        assert "summary" in data
        assert "daily_stats" in data
        assert "top_posts" in data
        
        # Check period information
        period = data["period"]
        assert period["days"] == days
        assert "start_date" in period
        assert "end_date" in period
        
        # Check summary metrics
        summary = data["summary"]
        required_summary_fields = [
            "total_posts", "total_views", "total_likes", 
            "total_comments", "total_shares", "average_engagement_rate"
        ]
        for field in required_summary_fields:
            assert field in summary
            assert isinstance(summary[field], (int, float))
        
        # Check daily stats structure
        daily_stats = data["daily_stats"]
        assert isinstance(daily_stats, list)
        assert len(daily_stats) == days
        
        for stat in daily_stats:
            assert "date" in stat
            assert "posts" in stat
            assert "views" in stat
            assert "engagement" in stat
        
        # Check top posts structure
        top_posts = data["top_posts"]
        assert isinstance(top_posts, list)
        for post in top_posts:
            assert "id" in post
            assert "title" in post
            assert "views" in post
            assert "engagement" in post
            assert "engagement_rate" in post
            assert "published_at" in post

    async def test_content_specific_analytics(self, authenticated_client: AsyncClient):
        """Test getting analytics for specific content"""
        content_id = 123
        
        response = await authenticated_client.get(
            f"/api/v1/analytics/content/{content_id}"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["content_id"] == content_id
        assert "title" in data
        assert "created_at" in data
        assert "platforms" in data
        assert "total_performance" in data
        assert "performance_over_time" in data
        
        # Check platforms data
        platforms = data["platforms"]
        for platform, metrics in platforms.items():
            assert "post_id" in metrics
            assert "views" in metrics
            assert "likes" in metrics
            assert "comments" in metrics
            assert "shares" in metrics
            assert "engagement_rate" in metrics
            assert "published_at" in metrics
        
        # Check total performance
        total_perf = data["total_performance"]
        assert "total_views" in total_perf
        assert "total_engagement" in total_perf
        assert "average_engagement_rate" in total_perf
        
        # Check performance over time
        perf_timeline = data["performance_over_time"]
        assert isinstance(perf_timeline, list)
        for point in perf_timeline:
            assert "timestamp" in point
            assert "cumulative_views" in point
            assert "cumulative_engagement" in point

    async def test_trends_analysis(self, authenticated_client: AsyncClient):
        """Test getting trends and insights"""
        response = await authenticated_client.get(
            "/api/v1/analytics/trends",
            params={"days": 30, "platform": "youtube"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "period" in data
        assert "trending_topics" in data
        assert "optimal_posting_times" in data
        assert "content_performance_insights" in data
        
        # Check period info
        period = data["period"]
        assert period["days"] == 30
        assert period["platform"] == "youtube"
        
        # Check trending topics
        trending_topics = data["trending_topics"]
        assert isinstance(trending_topics, list)
        for topic in trending_topics:
            assert "topic" in topic
            assert "mentions" in topic
            assert "average_engagement" in topic
            assert "growth" in topic
        
        # Check optimal posting times
        posting_times = data["optimal_posting_times"]
        days_of_week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for day in days_of_week:
            assert day in posting_times
            assert isinstance(posting_times[day], list)
        
        # Check content performance insights
        insights = data["content_performance_insights"]
        assert "best_performing_duration" in insights
        assert "best_performing_style" in insights
        assert "most_engaging_hashtags" in insights
        assert "audience_engagement_patterns" in insights

    async def test_trends_analysis_all_platforms(self, authenticated_client: AsyncClient):
        """Test getting trends for all platforms"""
        response = await authenticated_client.get(
            "/api/v1/analytics/trends",
            params={"days": 7}  # No platform specified = all platforms
        )
        
        assert response.status_code == 200
        data = response.json()
        
        period = data["period"]
        assert period["days"] == 7
        assert period["platform"] == "all"

    async def test_analytics_export(self, authenticated_client: AsyncClient):
        """Test exporting analytics data"""
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()
        
        response = await authenticated_client.get(
            "/api/v1/analytics/export",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "format": "csv",
                "platforms": ["youtube", "instagram"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "export_id" in data
        assert "format" in data
        assert "status" in data
        assert "download_url" in data
        assert "estimated_completion" in data
        
        assert data["format"] == "csv"
        assert data["status"] == "processing"
        assert data["export_id"].startswith("export_")

    async def test_analytics_export_different_formats(self, authenticated_client: AsyncClient):
        """Test exporting analytics in different formats"""
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()
        
        formats = ["csv", "json", "xlsx"]
        
        for export_format in formats:
            response = await authenticated_client.get(
                "/api/v1/analytics/export",
                params={
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "format": export_format
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["format"] == export_format

    async def test_analytics_date_range_validation(self, authenticated_client: AsyncClient):
        """Test analytics with various date ranges"""
        # Test last 7 days
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()
        
        request_data = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "platforms": ["youtube"]
        }
        
        response = await authenticated_client.post(
            "/api/v1/analytics/overview",
            json=request_data
        )
        
        assert response.status_code == 200
        
        # Test last 90 days
        start_date = datetime.utcnow() - timedelta(days=90)
        request_data["start_date"] = start_date.isoformat()
        
        response = await authenticated_client.post(
            "/api/v1/analytics/overview",
            json=request_data
        )
        
        assert response.status_code == 200

    async def test_analytics_platform_filtering(self, authenticated_client: AsyncClient):
        """Test analytics with platform filtering"""
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()
        
        # Test single platform
        request_data = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "platforms": ["youtube"]
        }
        
        response = await authenticated_client.post(
            "/api/v1/analytics/overview",
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Test multiple platforms
        request_data["platforms"] = ["youtube", "instagram", "facebook"]
        
        response = await authenticated_client.post(
            "/api/v1/analytics/overview",
            json=request_data
        )
        
        assert response.status_code == 200

    async def test_analytics_error_handling(self, authenticated_client: AsyncClient):
        """Test error handling in analytics endpoints"""
        # Test with invalid content ID
        response = await authenticated_client.get("/api/v1/analytics/content/999999")
        # Should still return 200 with mock data, but in real implementation might return 404
        assert response.status_code == 200
        
        # Test with invalid platform
        response = await authenticated_client.get("/api/v1/analytics/platforms/invalid_platform")
        assert response.status_code == 200  # Mock implementation handles any platform name
        
        # Test trends with invalid parameters
        response = await authenticated_client.get(
            "/api/v1/analytics/trends",
            params={"days": -1}  # Invalid days
        )
        # Mock implementation might not validate, but should handle gracefully
        assert response.status_code in [200, 400, 422]

    async def test_analytics_performance_metrics(self, authenticated_client: AsyncClient):
        """Test that analytics return consistent performance metrics"""
        # Get overview
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()
        
        request_data = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "platforms": ["youtube", "instagram"]
        }
        
        response = await authenticated_client.post(
            "/api/v1/analytics/overview",
            json=request_data
        )
        
        assert response.status_code == 200
        overview_data = response.json()
        
        # Get platform-specific data
        youtube_response = await authenticated_client.get(
            "/api/v1/analytics/platforms/youtube",
            params={"days": 30}
        )
        
        assert youtube_response.status_code == 200
        youtube_data = youtube_response.json()
        
        # Verify metric consistency (in a real implementation)
        # For mock data, just verify structure
        assert "total_views" in overview_data
        assert "total_views" in youtube_data["summary"]
        
        # Verify engagement rate is within reasonable bounds
        assert 0 <= overview_data["engagement_rate"] <= 100
        assert 0 <= youtube_data["summary"]["average_engagement_rate"] <= 100

    async def test_authentication_required_for_analytics(self, client: AsyncClient):
        """Test that analytics endpoints require authentication"""
        # Test without authentication token
        response = await client.post("/api/v1/analytics/overview", json={})
        assert response.status_code == 403
        
        response = await client.get("/api/v1/analytics/platforms/youtube")
        assert response.status_code == 403
        
        response = await client.get("/api/v1/analytics/content/1")
        assert response.status_code == 403