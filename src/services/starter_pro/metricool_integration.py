"""
Metricool Integration for Social Media Analytics and Scheduling
Comprehensive social media management and performance tracking
"""

from typing import Dict, Any, Optional, List
import httpx
import asyncio
from datetime import datetime, timedelta
from ...core.config import settings
from ...core.logger import logger


class MetricoolIntegration:
    """Metricool API integration for social media management"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'METRICOOL_API_KEY', '')
        self.base_url = "https://api.metricool.com/v1"
        
    async def schedule_content(
        self,
        platforms: List[str],
        content: Dict[str, Any],
        schedule_time: datetime,
        optimize_timing: bool = True
    ) -> Dict[str, Any]:
        """Schedule content across multiple social media platforms"""
        
        try:
            # Optimize posting time if requested
            if optimize_timing:
                optimal_time = await self._get_optimal_posting_time(platforms)
                if optimal_time:
                    schedule_time = optimal_time
            
            scheduling_data = {
                "platforms": platforms,
                "content": content,
                "schedule_time": schedule_time.isoformat(),
                "auto_publish": True,
                "track_performance": True
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/schedule",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=scheduling_data
                )
                
                if response.status_code == 201:
                    result = response.json()
                    schedule_id = result.get("schedule_id")
                    
                    return {
                        "success": True,
                        "schedule_id": schedule_id,
                        "scheduled_time": schedule_time.isoformat(),
                        "platforms": platforms,
                        "content_type": content.get("type", "unknown"),
                        "optimized": optimize_timing
                    }
                else:
                    logger.error(f"Metricool scheduling error: {response.status_code}")
                    return {
                        "success": False,
                        "error": f"Scheduling failed: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error scheduling content: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_posting_calendar(
        self,
        content_plan: List[Dict[str, Any]],
        start_date: datetime,
        frequency: str = "daily"
    ) -> Dict[str, Any]:
        """Create automated posting calendar"""
        
        try:
            frequency_hours = {
                "hourly": 1,
                "daily": 24,
                "twice_daily": 12,
                "weekly": 168,
                "bi_weekly": 336
            }
            
            interval_hours = frequency_hours.get(frequency, 24)
            scheduled_posts = []
            
            current_time = start_date
            
            for i, content_item in enumerate(content_plan):
                # Schedule each piece of content
                schedule_result = await self.schedule_content(
                    platforms=content_item.get("platforms", ["instagram", "tiktok"]),
                    content=content_item,
                    schedule_time=current_time,
                    optimize_timing=True
                )
                
                if schedule_result.get("success"):
                    scheduled_posts.append({
                        "index": i,
                        "schedule_id": schedule_result.get("schedule_id"),
                        "scheduled_time": current_time.isoformat(),
                        "content_title": content_item.get("title", f"Post {i+1}"),
                        "platforms": content_item.get("platforms", [])
                    })
                
                # Calculate next posting time
                current_time += timedelta(hours=interval_hours)
            
            return {
                "success": True,
                "calendar_created": True,
                "scheduled_posts": scheduled_posts,
                "total_posts": len(scheduled_posts),
                "frequency": frequency,
                "start_date": start_date.isoformat(),
                "end_date": current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating posting calendar: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_analytics_report(
        self,
        platforms: List[str],
        start_date: datetime,
        end_date: datetime,
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get comprehensive analytics report"""
        
        try:
            if not metrics:
                metrics = [
                    "reach", "impressions", "engagement", "clicks", 
                    "followers_growth", "engagement_rate", "best_posting_times"
                ]
            
            analytics_data = {
                "platforms": platforms,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "metrics": metrics,
                "include_comparisons": True,
                "include_recommendations": True
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/analytics/report",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=analytics_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Process and enhance the analytics data
                    processed_analytics = await self._process_analytics_data(result)
                    
                    return {
                        "success": True,
                        "analytics": processed_analytics,
                        "platforms": platforms,
                        "date_range": {
                            "start": start_date.isoformat(),
                            "end": end_date.isoformat()
                        },
                        "metrics_included": metrics
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Analytics request failed: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_competitor_analysis(
        self,
        competitor_accounts: List[str],
        platforms: List[str] = ["instagram", "tiktok", "youtube"]
    ) -> Dict[str, Any]:
        """Analyze competitor performance and strategies"""
        
        try:
            analysis_data = {
                "competitors": competitor_accounts,
                "platforms": platforms,
                "metrics": [
                    "posting_frequency", "engagement_rate", "content_types",
                    "hashtag_strategies", "posting_times", "growth_trends"
                ],
                "analysis_depth": "comprehensive"
            }
            
            async with httpx.AsyncClient(timeout=180) as client:
                response = await client.post(
                    f"{self.base_url}/analytics/competitors",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=analysis_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    return {
                        "success": True,
                        "competitor_analysis": result,
                        "insights": await self._extract_competitor_insights(result),
                        "recommendations": await self._generate_strategy_recommendations(result),
                        "analyzed_accounts": competitor_accounts,
                        "platforms": platforms
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Competitor analysis failed: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error analyzing competitors: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def optimize_hashtag_strategy(
        self,
        content_topic: str,
        target_audience: str,
        platforms: List[str]
    ) -> Dict[str, Any]:
        """Generate optimized hashtag strategy"""
        
        try:
            hashtag_data = {
                "content_topic": content_topic,
                "target_audience": target_audience,
                "platforms": platforms,
                "strategy_type": "growth_focused",
                "include_trending": True,
                "include_niche": True,
                "max_hashtags_per_platform": {
                    "instagram": 30,
                    "tiktok": 5,
                    "twitter": 3,
                    "linkedin": 5
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/hashtags/optimize",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=hashtag_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    return {
                        "success": True,
                        "hashtag_strategy": result,
                        "platforms": platforms,
                        "content_topic": content_topic,
                        "target_audience": target_audience
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Hashtag optimization failed: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error optimizing hashtags: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def track_campaign_performance(
        self,
        campaign_id: str,
        tracking_metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Track performance of specific campaigns"""
        
        try:
            if not tracking_metrics:
                tracking_metrics = [
                    "reach", "impressions", "engagement", "conversion_rate",
                    "click_through_rate", "cost_per_engagement", "roi"
                ]
            
            tracking_data = {
                "campaign_id": campaign_id,
                "metrics": tracking_metrics,
                "real_time": True,
                "include_breakdown": True
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/campaigns/{campaign_id}/performance",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    params=tracking_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    return {
                        "success": True,
                        "campaign_performance": result,
                        "campaign_id": campaign_id,
                        "metrics_tracked": tracking_metrics,
                        "performance_summary": await self._summarize_campaign_performance(result)
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Campaign tracking failed: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error tracking campaign: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_optimal_posting_time(self, platforms: List[str]) -> Optional[datetime]:
        """Get optimal posting time based on audience analytics"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/analytics/optimal-times",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    params={"platforms": ",".join(platforms)}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    optimal_time_str = data.get("next_optimal_time")
                    if optimal_time_str:
                        return datetime.fromisoformat(optimal_time_str)
                
        except Exception as e:
            logger.error(f"Error getting optimal posting time: {e}")
        
        return None
    
    async def _process_analytics_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and enhance analytics data"""
        
        processed = {
            "summary": {
                "total_reach": raw_data.get("total_reach", 0),
                "total_impressions": raw_data.get("total_impressions", 0),
                "average_engagement_rate": raw_data.get("avg_engagement_rate", 0),
                "follower_growth": raw_data.get("follower_growth", 0)
            },
            "platform_breakdown": raw_data.get("platform_data", {}),
            "trending_content": raw_data.get("top_performing_posts", []),
            "recommendations": raw_data.get("recommendations", [])
        }
        
        # Calculate additional insights
        if processed["summary"]["total_impressions"] > 0:
            processed["summary"]["reach_rate"] = (
                processed["summary"]["total_reach"] / 
                processed["summary"]["total_impressions"] * 100
            )
        
        return processed
    
    async def _extract_competitor_insights(self, analysis_data: Dict[str, Any]) -> List[str]:
        """Extract actionable insights from competitor analysis"""
        
        insights = []
        
        # Analyze posting patterns
        posting_data = analysis_data.get("posting_patterns", {})
        if posting_data:
            insights.append(f"Competitors post most frequently on {posting_data.get('peak_days', 'weekdays')}")
            insights.append(f"Average posting frequency: {posting_data.get('avg_posts_per_week', 'unknown')} posts/week")
        
        # Analyze engagement strategies
        engagement_data = analysis_data.get("engagement_strategies", {})
        if engagement_data:
            top_strategy = engagement_data.get("most_effective_strategy")
            if top_strategy:
                insights.append(f"Most effective strategy: {top_strategy}")
        
        # Content type analysis
        content_data = analysis_data.get("content_types", {})
        if content_data:
            top_content_type = max(content_data, key=content_data.get)
            insights.append(f"Most used content type: {top_content_type}")
        
        return insights
    
    async def _generate_strategy_recommendations(self, analysis_data: Dict[str, Any]) -> List[str]:
        """Generate strategy recommendations based on competitor analysis"""
        
        recommendations = []
        
        # Posting frequency recommendations
        posting_freq = analysis_data.get("avg_posting_frequency", 0)
        if posting_freq > 0:
            recommendations.append(f"Consider posting {posting_freq + 1} times per week to stay competitive")
        
        # Content type recommendations
        trending_content = analysis_data.get("trending_content_types", [])
        if trending_content:
            recommendations.append(f"Focus on {trending_content[0]} content for better engagement")
        
        # Hashtag recommendations
        hashtag_data = analysis_data.get("hashtag_analysis", {})
        if hashtag_data:
            avg_hashtags = hashtag_data.get("avg_hashtag_count", 0)
            if avg_hashtags > 0:
                recommendations.append(f"Use approximately {avg_hashtags} hashtags per post")
        
        return recommendations
    
    async def _summarize_campaign_performance(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize campaign performance data"""
        
        summary = {
            "status": "unknown",
            "key_metrics": {},
            "performance_grade": "N/A",
            "areas_for_improvement": []
        }
        
        # Determine campaign status
        engagement_rate = performance_data.get("engagement_rate", 0)
        if engagement_rate > 5:
            summary["status"] = "excellent"
            summary["performance_grade"] = "A"
        elif engagement_rate > 3:
            summary["status"] = "good"
            summary["performance_grade"] = "B"
        elif engagement_rate > 1:
            summary["status"] = "average"
            summary["performance_grade"] = "C"
        else:
            summary["status"] = "needs_improvement"
            summary["performance_grade"] = "D"
        
        # Extract key metrics
        summary["key_metrics"] = {
            "total_reach": performance_data.get("reach", 0),
            "engagement_rate": performance_data.get("engagement_rate", 0),
            "conversion_rate": performance_data.get("conversion_rate", 0),
            "roi": performance_data.get("roi", 0)
        }
        
        # Identify improvement areas
        if summary["key_metrics"]["engagement_rate"] < 3:
            summary["areas_for_improvement"].append("engagement_strategy")
        if summary["key_metrics"]["conversion_rate"] < 2:
            summary["areas_for_improvement"].append("call_to_action")
        if summary["key_metrics"]["roi"] < 100:
            summary["areas_for_improvement"].append("targeting_optimization")
        
        return summary


class MetricoolWorkflowManager:
    """High-level workflow manager for Metricool operations"""
    
    def __init__(self):
        self.metricool = MetricoolIntegration()
    
    async def setup_automated_publishing(
        self,
        content_calendar: List[Dict[str, Any]],
        start_date: datetime,
        publishing_strategy: str = "optimal_timing"
    ) -> Dict[str, Any]:
        """Set up complete automated publishing workflow"""
        
        # Create posting calendar
        calendar_result = await self.metricool.create_posting_calendar(
            content_plan=content_calendar,
            start_date=start_date,
            frequency="daily"
        )
        
        if not calendar_result.get("success"):
            return calendar_result
        
        # Set up analytics tracking
        analytics_setup = {
            "calendar_id": calendar_result.get("schedule_id"),
            "tracking_enabled": True,
            "automated_reports": True,
            "optimization_enabled": True
        }
        
        return {
            "success": True,
            "calendar": calendar_result,
            "analytics_setup": analytics_setup,
            "automation_active": True,
            "next_post": calendar_result.get("scheduled_posts", [{}])[0].get("scheduled_time")
        }
