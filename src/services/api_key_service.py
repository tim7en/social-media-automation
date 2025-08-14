"""
API Key Management Service
Handles user-specific API key retrieval and management
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, Dict
from datetime import datetime

from ..models.models import ApiKey
from ..core.logger import logger
from ..api.routers.api_keys import decrypt_api_key


class ApiKeyService:
    """Service for managing user API keys"""
    
    @staticmethod
    async def get_user_api_key(user_id: int, service_name: str, db: AsyncSession) -> Optional[str]:
        """
        Get decrypted API key for a user and service
        
        Args:
            user_id: The user's ID
            service_name: The service name (openai, elevenlabs, etc.)
            db: Database session
            
        Returns:
            Decrypted API key or None if not found
        """
        try:
            result = await db.execute(
                select(ApiKey).where(
                    and_(
                        ApiKey.user_id == user_id,
                        ApiKey.service_name == service_name,
                        ApiKey.is_active == True
                    )
                )
            )
            api_key = result.scalar_one_or_none()
            
            if not api_key:
                logger.warning(f"No active API key found for user {user_id}, service {service_name}")
                return None
            
            # Update last_used timestamp
            api_key.last_used = datetime.utcnow()
            db.add(api_key)
            await db.commit()
            
            return decrypt_api_key(api_key.api_key)
            
        except Exception as e:
            logger.error(f"Error retrieving API key for user {user_id}, service {service_name}: {str(e)}")
            return None
    
    @staticmethod
    async def get_all_user_api_keys(user_id: int, db: AsyncSession) -> Dict[str, str]:
        """
        Get all active API keys for a user
        
        Args:
            user_id: The user's ID
            db: Database session
            
        Returns:
            Dictionary of service_name -> decrypted_api_key
        """
        try:
            result = await db.execute(
                select(ApiKey).where(
                    and_(
                        ApiKey.user_id == user_id,
                        ApiKey.is_active == True
                    )
                )
            )
            api_keys = result.scalars().all()
            
            keys_dict = {}
            for api_key in api_keys:
                try:
                    decrypted_key = decrypt_api_key(api_key.api_key)
                    keys_dict[api_key.service_name] = decrypted_key
                    
                    # Update last_used timestamp
                    api_key.last_used = datetime.utcnow()
                    db.add(api_key)
                    
                except Exception as e:
                    logger.error(f"Failed to decrypt API key for service {api_key.service_name}: {str(e)}")
                    continue
            
            await db.commit()
            return keys_dict
            
        except Exception as e:
            logger.error(f"Error retrieving all API keys for user {user_id}: {str(e)}")
            return {}
    
    @staticmethod
    async def has_api_key(user_id: int, service_name: str, db: AsyncSession) -> bool:
        """
        Check if user has an active API key for a service
        
        Args:
            user_id: The user's ID
            service_name: The service name
            db: Database session
            
        Returns:
            True if user has active API key, False otherwise
        """
        try:
            result = await db.execute(
                select(ApiKey).where(
                    and_(
                        ApiKey.user_id == user_id,
                        ApiKey.service_name == service_name,
                        ApiKey.is_active == True
                    )
                )
            )
            api_key = result.scalar_one_or_none()
            return api_key is not None
            
        except Exception as e:
            logger.error(f"Error checking API key for user {user_id}, service {service_name}: {str(e)}")
            return False


# Global instance
api_key_service = ApiKeyService()
