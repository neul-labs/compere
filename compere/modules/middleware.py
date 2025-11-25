"""
Middleware for rate limiting and other cross-cutting concerns
"""
import logging
import os
import time
from collections import defaultdict, deque
from typing import Dict

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware"""

    def __init__(
        self,
        app,
        calls: int = 100,
        period: int = 60,
        enabled: bool = True
    ):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.enabled = enabled
        self.clients: Dict[str, deque] = defaultdict(deque)

    def get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""
        if not self.enabled:
            return await call_next(request)

        client_ip = self.get_client_ip(request)
        now = time.time()

        # Clean old entries
        client_requests = self.clients[client_ip]
        while client_requests and client_requests[0] < now - self.period:
            client_requests.popleft()

        # Check rate limit
        if len(client_requests) >= self.calls:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Rate limit exceeded. Max {self.calls} requests per {self.period} seconds.",
                    "retry_after": self.period
                },
                headers={"Retry-After": str(self.period)}
            )

        # Add current request
        client_requests.append(now)

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(max(0, self.calls - len(client_requests)))
        response.headers["X-RateLimit-Reset"] = str(int(now + self.period))

        return response

class LoggingMiddleware(BaseHTTPMiddleware):
    """Request/response logging middleware"""

    def __init__(self, app, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled

    async def dispatch(self, request: Request, call_next):
        """Log requests and responses"""
        if not self.enabled:
            return await call_next(request)

        start_time = time.time()
        client_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else "unknown")

        # Process request
        response = await call_next(request)

        # Log request
        process_time = time.time() - start_time
        logger.info(
            f"{client_ip} - \"{request.method} {request.url.path}\" "
            f"{response.status_code} - {process_time:.3f}s"
        )

        # Add timing header
        response.headers["X-Process-Time"] = str(process_time)

        return response

def create_rate_limit_middleware():
    """Create rate limiting middleware with configuration"""
    enabled = os.getenv("RATE_LIMIT_ENABLED", "false").lower() == "true"
    calls = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    period = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

    return RateLimitMiddleware(
        app=None,  # Will be set by FastAPI
        calls=calls,
        period=period,
        enabled=enabled
    )

def create_logging_middleware():
    """Create logging middleware with configuration"""
    enabled = os.getenv("LOG_REQUESTS", "true").lower() == "true"

    return LoggingMiddleware(
        app=None,  # Will be set by FastAPI
        enabled=enabled
    )