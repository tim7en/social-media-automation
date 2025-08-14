from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from cryptography.fernet import Fernet
import os
import base64

from ...core.database import get_db
from ...models.models import ApiKey, User
from ...schemas.schemas import (
    ApiKeyCreate, 
    ApiKeyUpdate, 
    ApiKey as ApiKeySchema,
    ApiKeyList,
    ServiceType
)
from .auth import get_current_user
from ...core.logger import logger

router = APIRouter()

# Encryption key for API keys (should be stored securely in production)
def get_encryption_key():
    """Get or generate encryption key for API keys"""
    key = os.getenv("API_KEY_ENCRYPTION_KEY")
    if not key:
        # Generate a new key (in production, this should be stored securely)
        key = Fernet.generate_key()
        logger.warning("No API_KEY_ENCRYPTION_KEY found, using temporary key")
    else:
        key = key.encode()
    return key

def encrypt_api_key(api_key: str) -> str:
    """Encrypt API key for storage"""
    f = Fernet(get_encryption_key())
    encrypted_key = f.encrypt(api_key.encode())
    return base64.b64encode(encrypted_key).decode()

def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt API key from storage"""
    f = Fernet(get_encryption_key())
    decoded_key = base64.b64decode(encrypted_key.encode())
    decrypted_key = f.decrypt(decoded_key)
    return decrypted_key.decode()


@router.get("/api-keys", response_model=List[ApiKeyList])
async def get_user_api_keys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all API keys for the current user (without exposing the actual keys)"""
    try:
        result = await db.execute(
            select(ApiKey).where(ApiKey.user_id == current_user.id)
        )
        api_keys = result.scalars().all()
        
        return [
            ApiKeyList(
                service_name=key.service_name,
                is_active=key.is_active,
                last_used=key.last_used,
                created_at=key.created_at
            )
            for key in api_keys
        ]
    except Exception as e:
        logger.error(f"Error fetching API keys for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch API keys"
        )


@router.post("/api-keys", response_model=ApiKeySchema)
async def create_or_update_api_key(
    api_key_data: ApiKeyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create or update an API key for a service"""
    try:
        # Check if API key already exists for this service
        result = await db.execute(
            select(ApiKey).where(
                and_(
                    ApiKey.user_id == current_user.id,
                    ApiKey.service_name == api_key_data.service_name
                )
            )
        )
        existing_key = result.scalar_one_or_none()
        
        encrypted_key = encrypt_api_key(api_key_data.api_key)
        
        if existing_key:
            # Update existing key
            existing_key.api_key = encrypted_key
            existing_key.is_active = True
            db.add(existing_key)
            await db.commit()
            await db.refresh(existing_key)
            
            logger.info(f"Updated API key for service {api_key_data.service_name} for user {current_user.id}")
            return existing_key
        else:
            # Create new key
            new_api_key = ApiKey(
                user_id=current_user.id,
                service_name=api_key_data.service_name,
                api_key=encrypted_key,
                is_active=True
            )
            
            db.add(new_api_key)
            await db.commit()
            await db.refresh(new_api_key)
            
            logger.info(f"Created new API key for service {api_key_data.service_name} for user {current_user.id}")
            return new_api_key
            
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating/updating API key for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save API key"
        )


@router.put("/api-keys/{service_name}", response_model=ApiKeySchema)
async def update_api_key(
    service_name: ServiceType,
    api_key_update: ApiKeyUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an existing API key"""
    try:
        result = await db.execute(
            select(ApiKey).where(
                and_(
                    ApiKey.user_id == current_user.id,
                    ApiKey.service_name == service_name
                )
            )
        )
        api_key = result.scalar_one_or_none()
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"API key for service {service_name} not found"
            )
        
        if api_key_update.api_key:
            api_key.api_key = encrypt_api_key(api_key_update.api_key)
        
        if api_key_update.is_active is not None:
            api_key.is_active = api_key_update.is_active
        
        db.add(api_key)
        await db.commit()
        await db.refresh(api_key)
        
        logger.info(f"Updated API key for service {service_name} for user {current_user.id}")
        return api_key
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating API key for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update API key"
        )


@router.delete("/api-keys/{service_name}")
async def delete_api_key(
    service_name: ServiceType,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an API key for a service"""
    try:
        result = await db.execute(
            select(ApiKey).where(
                and_(
                    ApiKey.user_id == current_user.id,
                    ApiKey.service_name == service_name
                )
            )
        )
        api_key = result.scalar_one_or_none()
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"API key for service {service_name} not found"
            )
        
        await db.delete(api_key)
        await db.commit()
        
        logger.info(f"Deleted API key for service {service_name} for user {current_user.id}")
        return {"message": f"API key for {service_name} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting API key for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete API key"
        )


@router.get("/api-keys/{service_name}/test")
async def test_api_key(
    service_name: ServiceType,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Test if an API key is valid for a service"""
    try:
        result = await db.execute(
            select(ApiKey).where(
                and_(
                    ApiKey.user_id == current_user.id,
                    ApiKey.service_name == service_name,
                    ApiKey.is_active == True
                )
            )
        )
        api_key = result.scalar_one_or_none()
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Active API key for service {service_name} not found"
            )
        
        # For now, just return that the key exists
        # In a real implementation, you would make a test call to the service
        return {
            "service": service_name,
            "status": "configured",
            "message": f"API key for {service_name} is configured"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing API key for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to test API key"
        )


async def get_user_api_key(user_id: int, service_name: str, db: AsyncSession) -> str:
    """Helper function to get decrypted API key for a user and service"""
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
            return None
        
        # Update last_used timestamp
        from datetime import datetime
        api_key.last_used = datetime.utcnow()
        db.add(api_key)
        await db.commit()
        
        return decrypt_api_key(api_key.api_key)
        
    except Exception as e:
        logger.error(f"Error retrieving API key for user {user_id}, service {service_name}: {str(e)}")
        return None
