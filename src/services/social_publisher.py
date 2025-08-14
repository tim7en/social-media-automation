from typing import Optional, Dict, Any, List
import httpx
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import facebook
from instagrapi import Client as InstagramClient
import json
from ..core.config import settings
from ..core.logger import logger


class SocialMediaPublisher:
    """Social media publishing service"""
    
    def __init__(self):
        self.youtube_service = None
        self.facebook_api = None
        self.instagram_client = None
    
    async def publish_to_youtube(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: List[str] = None,
        privacy_status: str = "public"
    ) -> Dict[str, Any]:
        """Publish video to YouTube"""
        
        try:
            # Initialize YouTube service
            youtube = await self._get_youtube_service()
            
            # Prepare video metadata
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags or [],
                    'categoryId': '22'  # People & Blogs
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Upload video
            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
            
            request = youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logger.info(f"Upload progress: {int(status.progress() * 100)}%")
            
            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            logger.info(f"Video uploaded to YouTube: {video_url}")
            
            return {
                "success": True,
                "platform": "youtube",
                "post_id": video_id,
                "url": video_url,
                "response": response
            }
            
        except Exception as e:
            logger.error(f"Error publishing to YouTube: {e}")
            return {
                "success": False,
                "platform": "youtube",
                "error": str(e)
            }
    
    async def publish_to_facebook(
        self,
        video_path: str,
        message: str,
        page_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Publish video to Facebook"""
        
        try:
            # Initialize Facebook API
            fb_api = self._get_facebook_api()
            
            # Upload video
            if page_id:
                # Post to page
                response = fb_api.put_video(
                    video=open(video_path, 'rb'),
                    message=message,
                    parent_object=page_id
                )
            else:
                # Post to personal profile
                response = fb_api.put_video(
                    video=open(video_path, 'rb'),
                    message=message
                )
            
            post_id = response.get('id')
            post_url = f"https://www.facebook.com/{post_id}"
            
            logger.info(f"Video posted to Facebook: {post_url}")
            
            return {
                "success": True,
                "platform": "facebook",
                "post_id": post_id,
                "url": post_url,
                "response": response
            }
            
        except Exception as e:
            logger.error(f"Error publishing to Facebook: {e}")
            return {
                "success": False,
                "platform": "facebook",
                "error": str(e)
            }
    
    async def publish_to_instagram(
        self,
        video_path: str,
        caption: str,
        hashtags: List[str] = None
    ) -> Dict[str, Any]:
        """Publish video to Instagram"""
        
        try:
            # Initialize Instagram client
            ig_client = await self._get_instagram_client()
            
            # Prepare caption with hashtags
            full_caption = caption
            if hashtags:
                full_caption += "\n\n" + " ".join([f"#{tag}" for tag in hashtags])
            
            # Upload video
            media = ig_client.video_upload(video_path, full_caption)
            
            post_id = media.pk
            post_url = f"https://www.instagram.com/p/{media.code}/"
            
            logger.info(f"Video posted to Instagram: {post_url}")
            
            return {
                "success": True,
                "platform": "instagram",
                "post_id": post_id,
                "url": post_url,
                "response": media.dict()
            }
            
        except Exception as e:
            logger.error(f"Error publishing to Instagram: {e}")
            return {
                "success": False,
                "platform": "instagram",
                "error": str(e)
            }
    
    async def publish_to_tiktok(
        self,
        video_path: str,
        caption: str,
        hashtags: List[str] = None
    ) -> Dict[str, Any]:
        """Publish video to TikTok"""
        
        try:
            # Note: TikTok API requires special approval and has limited functionality
            # This is a placeholder implementation
            
            # For now, return a message about manual upload
            logger.warning("TikTok API publishing not fully implemented - requires manual upload")
            
            return {
                "success": False,
                "platform": "tiktok",
                "error": "TikTok API publishing requires special approval - please upload manually",
                "manual_upload_info": {
                    "video_path": video_path,
                    "caption": caption,
                    "hashtags": hashtags
                }
            }
            
        except Exception as e:
            logger.error(f"Error publishing to TikTok: {e}")
            return {
                "success": False,
                "platform": "tiktok",
                "error": str(e)
            }
    
    async def publish_to_multiple_platforms(
        self,
        video_path: str,
        content_data: Dict[str, Any],
        platforms: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """Publish to multiple platforms"""
        
        results = {}
        
        for platform in platforms:
            try:
                if platform == "youtube":
                    result = await self.publish_to_youtube(
                        video_path,
                        content_data.get("title", ""),
                        content_data.get("description", ""),
                        content_data.get("tags", []),
                        content_data.get("privacy_status", "public")
                    )
                elif platform == "facebook":
                    result = await self.publish_to_facebook(
                        video_path,
                        content_data.get("message", ""),
                        content_data.get("page_id")
                    )
                elif platform == "instagram":
                    result = await self.publish_to_instagram(
                        video_path,
                        content_data.get("caption", ""),
                        content_data.get("hashtags", [])
                    )
                elif platform == "tiktok":
                    result = await self.publish_to_tiktok(
                        video_path,
                        content_data.get("caption", ""),
                        content_data.get("hashtags", [])
                    )
                else:
                    result = {
                        "success": False,
                        "platform": platform,
                        "error": f"Platform {platform} not supported"
                    }
                
                results[platform] = result
                
            except Exception as e:
                logger.error(f"Error publishing to {platform}: {e}")
                results[platform] = {
                    "success": False,
                    "platform": platform,
                    "error": str(e)
                }
        
        return results
    
    async def _get_youtube_service(self):
        """Get authenticated YouTube service"""
        
        if not self.youtube_service:
            try:
                # Use OAuth2 credentials
                credentials = Credentials(
                    token=None,
                    refresh_token=settings.GOOGLE_REFRESH_TOKEN,
                    client_id=settings.GOOGLE_CLIENT_ID,
                    client_secret=settings.GOOGLE_CLIENT_SECRET,
                    token_uri="https://oauth2.googleapis.com/token"
                )
                
                # Refresh the token
                credentials.refresh(Request())
                
                self.youtube_service = build('youtube', 'v3', credentials=credentials)
                
            except Exception as e:
                logger.error(f"Error authenticating with YouTube: {e}")
                raise
        
        return self.youtube_service
    
    def _get_facebook_api(self):
        """Get Facebook API instance"""
        
        if not self.facebook_api:
            try:
                self.facebook_api = facebook.GraphAPI(
                    access_token=settings.FACEBOOK_ACCESS_TOKEN,
                    version="3.1"
                )
            except Exception as e:
                logger.error(f"Error initializing Facebook API: {e}")
                raise
        
        return self.facebook_api
    
    async def _get_instagram_client(self):
        """Get Instagram client"""
        
        if not self.instagram_client:
            try:
                self.instagram_client = InstagramClient()
                
                # Login using access token or credentials
                # Note: Instagram Basic Display API has limitations
                # This may require session-based authentication
                
                logger.warning("Instagram client initialized - may require manual authentication")
                
            except Exception as e:
                logger.error(f"Error initializing Instagram client: {e}")
                raise
        
        return self.instagram_client
    
    async def get_platform_analytics(
        self,
        platform: str,
        post_id: str
    ) -> Dict[str, Any]:
        """Get analytics for a specific post"""
        
        try:
            if platform == "youtube":
                return await self._get_youtube_analytics(post_id)
            elif platform == "facebook":
                return await self._get_facebook_analytics(post_id)
            elif platform == "instagram":
                return await self._get_instagram_analytics(post_id)
            else:
                return {"error": f"Analytics not available for {platform}"}
                
        except Exception as e:
            logger.error(f"Error getting analytics for {platform}: {e}")
            return {"error": str(e)}
    
    async def _get_youtube_analytics(self, video_id: str) -> Dict[str, Any]:
        """Get YouTube video analytics"""
        
        try:
            youtube = await self._get_youtube_service()
            
            # Get video statistics
            response = youtube.videos().list(
                part="statistics,snippet",
                id=video_id
            ).execute()
            
            if response['items']:
                video_data = response['items'][0]
                stats = video_data['statistics']
                
                return {
                    "views": int(stats.get('viewCount', 0)),
                    "likes": int(stats.get('likeCount', 0)),
                    "comments": int(stats.get('commentCount', 0)),
                    "title": video_data['snippet']['title'],
                    "published_at": video_data['snippet']['publishedAt']
                }
            else:
                return {"error": "Video not found"}
                
        except Exception as e:
            logger.error(f"Error getting YouTube analytics: {e}")
            return {"error": str(e)}
    
    async def _get_facebook_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get Facebook post analytics"""
        
        try:
            fb_api = self._get_facebook_api()
            
            # Get post insights
            post_data = fb_api.get_object(
                post_id,
                fields="created_time,message,insights.metric(post_reactions_by_type_total,post_impressions,post_video_views)"
            )
            
            insights = post_data.get('insights', {}).get('data', [])
            
            analytics = {
                "created_time": post_data.get('created_time'),
                "message": post_data.get('message', ''),
            }
            
            for insight in insights:
                metric = insight['name']
                value = insight['values'][0]['value'] if insight['values'] else 0
                analytics[metric] = value
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting Facebook analytics: {e}")
            return {"error": str(e)}
    
    async def _get_instagram_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get Instagram post analytics"""
        
        try:
            # Note: Instagram Basic Display API has limited analytics
            # This would require Instagram Business API for full analytics
            
            logger.warning("Instagram analytics limited - requires Business API")
            
            return {
                "error": "Instagram analytics require Business API access"
            }
            
        except Exception as e:
            logger.error(f"Error getting Instagram analytics: {e}")
            return {"error": str(e)}
