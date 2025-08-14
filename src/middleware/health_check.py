"""
Enhanced health check system with comprehensive component monitoring.
"""
import asyncio
import time
import psutil
import os
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as redis
import logging

from ..core.database import get_db
from ..core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


class HealthChecker:
    """Comprehensive health check for all application components"""
    
    def __init__(self):
        self.checks = {
            "database": self._check_database,
            "redis": self._check_redis,
            "storage": self._check_storage,
            "memory": self._check_memory,
            "disk": self._check_disk,
            "external_apis": self._check_external_apis
        }
    
    async def check_all(self, db: AsyncSession) -> Dict[str, Any]:
        """Run all health checks and return comprehensive status"""
        start_time = time.time()
        results = {}
        overall_status = "healthy"
        
        for check_name, check_func in self.checks.items():
            try:
                if check_name == "database":
                    result = await check_func(db)
                else:
                    result = await check_func()
                
                results[check_name] = result
                
                if result["status"] != "healthy":
                    overall_status = "degraded"
                    
            except Exception as e:
                logger.error(f"Health check failed for {check_name}: {str(e)}")
                results[check_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": time.time()
                }
                overall_status = "unhealthy"
        
        # Calculate response time
        response_time = time.time() - start_time
        
        return {
            "status": overall_status,
            "timestamp": time.time(),
            "response_time_ms": round(response_time * 1000, 2),
            "version": "1.0.0",
            "environment": "development" if settings.DEBUG else "production",
            "components": results
        }
    
    async def _check_database(self, db: AsyncSession) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            start_time = time.time()
            
            # Test basic connectivity
            result = await db.execute(text("SELECT 1"))
            result.fetchone()
            
            # Test a more complex query to check performance
            await db.execute(text("SELECT COUNT(*) FROM information_schema.tables"))
            
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time * 1000, 2),
                "timestamp": time.time(),
                "details": {
                    "connection_pool_size": db.bind.pool.size(),
                    "checked_out_connections": db.bind.pool.checkedout()
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def _check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity and performance"""
        try:
            start_time = time.time()
            
            # Connect to Redis
            redis_client = redis.from_url(settings.REDIS_URL)
            
            # Test basic operations
            await redis_client.ping()
            test_key = f"health_check_{int(time.time())}"
            await redis_client.set(test_key, "test", ex=60)
            value = await redis_client.get(test_key)
            await redis_client.delete(test_key)
            
            # Get Redis info
            info = await redis_client.info()
            
            await redis_client.close()
            
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time * 1000, 2),
                "timestamp": time.time(),
                "details": {
                    "version": info.get("redis_version", "unknown"),
                    "used_memory_mb": round(info.get("used_memory", 0) / 1024 / 1024, 2),
                    "connected_clients": info.get("connected_clients", 0)
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def _check_storage(self) -> Dict[str, Any]:
        """Check storage availability and disk space"""
        try:
            # Check if content output directory exists and is writable
            content_dir = settings.CONTENT_OUTPUT_DIR
            
            if not os.path.exists(content_dir):
                os.makedirs(content_dir, exist_ok=True)
            
            # Test write operation
            test_file = os.path.join(content_dir, "health_check.tmp")
            with open(test_file, "w") as f:
                f.write("health check")
            
            # Test read operation
            with open(test_file, "r") as f:
                content = f.read()
            
            # Cleanup
            os.remove(test_file)
            
            # Get disk usage
            disk_usage = psutil.disk_usage(content_dir)
            
            return {
                "status": "healthy",
                "timestamp": time.time(),
                "details": {
                    "content_directory": content_dir,
                    "total_space_gb": round(disk_usage.total / 1024 / 1024 / 1024, 2),
                    "free_space_gb": round(disk_usage.free / 1024 / 1024 / 1024, 2),
                    "used_space_percent": round((disk_usage.used / disk_usage.total) * 100, 2)
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def _check_memory(self) -> Dict[str, Any]:
        """Check system memory usage"""
        try:
            memory = psutil.virtual_memory()
            
            # Determine status based on memory usage
            status = "healthy"
            if memory.percent > 90:
                status = "unhealthy"
            elif memory.percent > 80:
                status = "degraded"
            
            return {
                "status": status,
                "timestamp": time.time(),
                "details": {
                    "total_mb": round(memory.total / 1024 / 1024, 2),
                    "available_mb": round(memory.available / 1024 / 1024, 2),
                    "used_percent": memory.percent,
                    "warning_threshold": 80,
                    "critical_threshold": 90
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def _check_disk(self) -> Dict[str, Any]:
        """Check disk usage for critical paths"""
        try:
            # Check root filesystem
            root_usage = psutil.disk_usage("/")
            
            # Determine status based on disk usage
            status = "healthy"
            usage_percent = (root_usage.used / root_usage.total) * 100
            
            if usage_percent > 95:
                status = "unhealthy"
            elif usage_percent > 85:
                status = "degraded"
            
            return {
                "status": status,
                "timestamp": time.time(),
                "details": {
                    "root_total_gb": round(root_usage.total / 1024 / 1024 / 1024, 2),
                    "root_free_gb": round(root_usage.free / 1024 / 1024 / 1024, 2),
                    "root_used_percent": round(usage_percent, 2),
                    "warning_threshold": 85,
                    "critical_threshold": 95
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def _check_external_apis(self) -> Dict[str, Any]:
        """Check external API availability (non-blocking)"""
        try:
            import httpx
            
            apis_to_check = []
            
            # Only check APIs that have keys configured
            if settings.OPENAI_API_KEY:
                apis_to_check.append(("OpenAI", "https://api.openai.com/v1/models"))
            
            if settings.ELEVENLABS_API_KEY:
                apis_to_check.append(("ElevenLabs", "https://api.elevenlabs.io/v1/voices"))
            
            if not apis_to_check:
                return {
                    "status": "skipped",
                    "timestamp": time.time(),
                    "details": {"message": "No external APIs configured"}
                }
            
            results = {}
            overall_status = "healthy"
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                for api_name, url in apis_to_check:
                    try:
                        response = await client.get(url)
                        if response.status_code < 500:  # Accept 4xx errors (auth issues are expected)
                            results[api_name] = "healthy"
                        else:
                            results[api_name] = "unhealthy"
                            overall_status = "degraded"
                    except Exception:
                        results[api_name] = "unhealthy"
                        overall_status = "degraded"
            
            return {
                "status": overall_status,
                "timestamp": time.time(),
                "details": results
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }


# Initialize health checker
health_checker = HealthChecker()


@router.get("/health")
async def health_check_basic():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "message": "Social Media Automation Platform is running"
    }


@router.get("/health/detailed")
async def health_check_detailed(db: AsyncSession = Depends(get_db)):
    """Detailed health check with all components"""
    try:
        result = await health_checker.check_all(db)
        
        # Set appropriate HTTP status code
        status_code = 200
        if result["status"] == "degraded":
            status_code = 200  # Still operational but with issues
        elif result["status"] == "unhealthy":
            status_code = 503  # Service unavailable
        
        return result
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "error": "Health check system failure",
                "timestamp": time.time()
            }
        )


@router.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Readiness check for Kubernetes/container orchestration"""
    try:
        # Quick checks for essential components
        essential_checks = ["database", "redis"]
        
        for check_name in essential_checks:
            check_func = health_checker.checks[check_name]
            if check_name == "database":
                result = await check_func(db)
            else:
                result = await check_func()
            
            if result["status"] == "unhealthy":
                raise HTTPException(
                    status_code=503,
                    detail={
                        "ready": False,
                        "failed_component": check_name,
                        "timestamp": time.time()
                    }
                )
        
        return {
            "ready": True,
            "timestamp": time.time()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "ready": False,
                "error": str(e),
                "timestamp": time.time()
            }
        )


@router.get("/health/live")
async def liveness_check():
    """Liveness check for Kubernetes/container orchestration"""
    return {
        "alive": True,
        "timestamp": time.time()
    }