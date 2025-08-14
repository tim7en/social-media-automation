"""
Comprehensive error handling middleware for the social media automation platform.
"""
import traceback
from typing import Any, Dict
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Custom application error with structured error information"""
    
    def __init__(self, message: str, status_code: int = 500, error_code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "INTERNAL_ERROR"
        self.details = details or {}


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware to handle all application errors and provide structured error responses"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Log successful requests
            process_time = time.time() - start_time
            logger.info(
                f"Request completed",
                extra={
                    "method": request.method,
                    "url": str(request.url),
                    "status_code": response.status_code,
                    "process_time": process_time,
                    "client_ip": request.client.host if request.client else None
                }
            )
            
            return response
            
        except AppError as app_error:
            # Handle custom application errors
            logger.error(
                f"Application error: {app_error.message}",
                extra={
                    "error_code": app_error.error_code,
                    "status_code": app_error.status_code,
                    "details": app_error.details,
                    "method": request.method,
                    "url": str(request.url),
                    "client_ip": request.client.host if request.client else None
                }
            )
            
            return JSONResponse(
                status_code=app_error.status_code,
                content={
                    "success": False,
                    "error": {
                        "code": app_error.error_code,
                        "message": app_error.message,
                        "details": app_error.details
                    },
                    "timestamp": time.time()
                }
            )
            
        except HTTPException as http_error:
            # Handle FastAPI HTTP exceptions
            logger.warning(
                f"HTTP error: {http_error.detail}",
                extra={
                    "status_code": http_error.status_code,
                    "method": request.method,
                    "url": str(request.url),
                    "client_ip": request.client.host if request.client else None
                }
            )
            
            return JSONResponse(
                status_code=http_error.status_code,
                content={
                    "success": False,
                    "error": {
                        "code": f"HTTP_{http_error.status_code}",
                        "message": http_error.detail,
                        "details": {}
                    },
                    "timestamp": time.time()
                }
            )
            
        except Exception as error:
            # Handle unexpected errors
            error_id = f"error_{int(time.time())}"
            
            logger.error(
                f"Unexpected error [{error_id}]: {str(error)}",
                extra={
                    "error_id": error_id,
                    "error_type": type(error).__name__,
                    "traceback": traceback.format_exc(),
                    "method": request.method,
                    "url": str(request.url),
                    "client_ip": request.client.host if request.client else None
                }
            )
            
            # Don't expose internal error details in production
            error_message = "Internal server error occurred"
            if hasattr(request.app.state, "settings") and getattr(request.app.state.settings, "DEBUG", False):
                error_message = str(error)
            
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": error_message,
                        "error_id": error_id,
                        "details": {}
                    },
                    "timestamp": time.time()
                }
            )


def create_error_response(
    message: str, 
    status_code: int = 400, 
    error_code: str = None, 
    details: Dict[str, Any] = None
) -> JSONResponse:
    """Create a standardized error response"""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": error_code or f"HTTP_{status_code}",
                "message": message,
                "details": details or {}
            },
            "timestamp": time.time()
        }
    )