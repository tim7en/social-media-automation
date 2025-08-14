"""
Security middleware for rate limiting, authentication, and request validation.
"""
import time
import hashlib
from typing import Dict, Optional
from collections import defaultdict, deque
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware to prevent abuse"""
    
    def __init__(self, app, calls: int = 100, period: int = 900):  # 100 calls per 15 minutes
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = defaultdict(lambda: deque())
    
    async def dispatch(self, request: Request, call_next):
        # Get client identifier
        client_ip = self._get_client_ip(request)
        
        # Check rate limit
        if not self._check_rate_limit(client_ip):
            logger.warning(
                f"Rate limit exceeded for client: {client_ip}",
                extra={
                    "client_ip": client_ip,
                    "method": request.method,
                    "url": str(request.url)
                }
            )
            
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": f"Rate limit exceeded. Maximum {self.calls} requests per {self.period} seconds.",
                        "details": {
                            "limit": self.calls,
                            "period": self.period,
                            "retry_after": self._get_retry_after(client_ip)
                        }
                    },
                    "timestamp": time.time()
                },
                headers={"Retry-After": str(self._get_retry_after(client_ip))}
            )
        
        response = await call_next(request)
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address, considering proxy headers"""
        # Check for forwarded headers (common in load balancers/proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _check_rate_limit(self, client_ip: str) -> bool:
        """Check if client has exceeded rate limit"""
        now = time.time()
        client_requests = self.clients[client_ip]
        
        # Remove old requests outside the time window
        while client_requests and client_requests[0] <= now - self.period:
            client_requests.popleft()
        
        # Check if within limit
        if len(client_requests) >= self.calls:
            return False
        
        # Add current request
        client_requests.append(now)
        return True
    
    def _get_retry_after(self, client_ip: str) -> int:
        """Calculate retry-after time in seconds"""
        client_requests = self.clients[client_ip]
        if not client_requests:
            return 0
        
        oldest_request = client_requests[0]
        return max(0, int(self.period - (time.time() - oldest_request)))


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'"
        )
        
        return response


class InputValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for basic input validation and sanitization"""
    
    SUSPICIOUS_PATTERNS = [
        r'<script',
        r'javascript:',
        r'on\w+\s*=',
        r'eval\s*\(',
        r'expression\s*\(',
        r'vbscript:',
        r'data:text/html',
        r'<iframe',
        r'<object',
        r'<embed'
    ]
    
    MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
    
    async def dispatch(self, request: Request, call_next):
        # Check request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.MAX_REQUEST_SIZE:
            logger.warning(
                f"Request size too large: {content_length} bytes",
                extra={
                    "client_ip": request.client.host if request.client else None,
                    "method": request.method,
                    "url": str(request.url)
                }
            )
            
            return JSONResponse(
                status_code=413,
                content={
                    "success": False,
                    "error": {
                        "code": "REQUEST_TOO_LARGE",
                        "message": f"Request size exceeds maximum allowed size of {self.MAX_REQUEST_SIZE} bytes",
                        "details": {"max_size": self.MAX_REQUEST_SIZE}
                    },
                    "timestamp": time.time()
                }
            )
        
        # Validate request headers and query parameters
        if not self._validate_request(request):
            logger.warning(
                "Suspicious request detected",
                extra={
                    "client_ip": request.client.host if request.client else None,
                    "method": request.method,
                    "url": str(request.url),
                    "headers": dict(request.headers),
                    "query_params": dict(request.query_params)
                }
            )
            
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": {
                        "code": "INVALID_REQUEST",
                        "message": "Request contains invalid or suspicious content",
                        "details": {}
                    },
                    "timestamp": time.time()
                }
            )
        
        response = await call_next(request)
        return response
    
    def _validate_request(self, request: Request) -> bool:
        """Validate request for suspicious patterns"""
        import re
        
        # Skip validation for dashboard and static file requests
        path = str(request.url.path)
        if path.startswith('/dashboard') or path.startswith('/static') or path.startswith('/api-keys'):
            return True
        
        # Check query parameters
        for key, value in request.query_params.items():
            # Skip VS Code browser request IDs and common parameters
            if key.lower() in ['id', 'vscodebrowerreqid', 'vscodebrowserreqid', '_t', 'timestamp']:
                continue
            if self._contains_suspicious_content(value):
                return False
        
        # Check headers (exclude common ones that might contain these patterns legitimately)
        safe_headers = {'user-agent', 'accept', 'accept-encoding', 'accept-language', 'referer', 'host', 'connection'}
        for name, value in request.headers.items():
            if name.lower() not in safe_headers and self._contains_suspicious_content(value):
                return False
        
        return True
    
    def _contains_suspicious_content(self, text: str) -> bool:
        """Check if text contains suspicious patterns"""
        import re
        
        text_lower = text.lower()
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False