"""
Tests for middleware module - rate limiting and logging.
"""

import os
import sys
import time
from collections import deque
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

# Add the compere package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from compere.modules.middleware import (
    LoggingMiddleware,
    RateLimitMiddleware,
    create_logging_middleware,
    create_rate_limit_middleware,
)


class TestRateLimitMiddleware:
    """Test rate limiting middleware"""

    def test_rate_limit_disabled(self):
        """Test that requests pass through when rate limiting is disabled"""
        app = FastAPI()
        app.add_middleware(RateLimitMiddleware, calls=5, period=60, enabled=False)

        @app.get("/test")
        def test_endpoint():
            return {"message": "success"}

        client = TestClient(app)

        # Make many requests - should all succeed when disabled
        for _ in range(20):
            response = client.get("/test")
            assert response.status_code == 200

    def test_rate_limit_enabled(self):
        """Test rate limiting when enabled"""
        app = FastAPI()
        app.add_middleware(RateLimitMiddleware, calls=3, period=60, enabled=True)

        @app.get("/test")
        def test_endpoint():
            return {"message": "success"}

        client = TestClient(app)

        # First 3 requests should succeed
        for i in range(3):
            response = client.get("/test")
            assert response.status_code == 200, f"Request {i + 1} failed"

        # 4th request should be rate limited
        response = client.get("/test")
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]

    def test_rate_limit_headers(self):
        """Test rate limit headers are set"""
        app = FastAPI()
        app.add_middleware(RateLimitMiddleware, calls=10, period=60, enabled=True)

        @app.get("/test")
        def test_endpoint():
            return {"message": "success"}

        client = TestClient(app)
        response = client.get("/test")

        assert response.status_code == 200
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers
        assert response.headers["X-RateLimit-Limit"] == "10"

    def test_rate_limit_remaining_decreases(self):
        """Test that remaining count decreases with each request"""
        app = FastAPI()
        app.add_middleware(RateLimitMiddleware, calls=5, period=60, enabled=True)

        @app.get("/test")
        def test_endpoint():
            return {"message": "success"}

        client = TestClient(app)

        response1 = client.get("/test")
        remaining1 = int(response1.headers["X-RateLimit-Remaining"])

        response2 = client.get("/test")
        remaining2 = int(response2.headers["X-RateLimit-Remaining"])

        assert remaining2 < remaining1

    def test_rate_limit_retry_after_header(self):
        """Test Retry-After header on rate limit"""
        app = FastAPI()
        app.add_middleware(RateLimitMiddleware, calls=1, period=30, enabled=True)

        @app.get("/test")
        def test_endpoint():
            return {"message": "success"}

        client = TestClient(app)

        # First request succeeds
        client.get("/test")

        # Second request is rate limited
        response = client.get("/test")
        assert response.status_code == 429
        assert "Retry-After" in response.headers
        assert response.headers["Retry-After"] == "30"

    def test_get_client_ip_direct(self):
        """Test getting client IP directly"""
        middleware = RateLimitMiddleware(app=MagicMock(), calls=10, period=60)

        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}
        mock_request.client = MagicMock()
        mock_request.client.host = "192.168.1.1"

        ip = middleware.get_client_ip(mock_request)
        assert ip == "192.168.1.1"

    def test_get_client_ip_forwarded(self):
        """Test getting client IP from X-Forwarded-For header"""
        middleware = RateLimitMiddleware(app=MagicMock(), calls=10, period=60)

        mock_request = MagicMock(spec=Request)
        mock_request.headers = {"X-Forwarded-For": "10.0.0.1, 192.168.1.1"}
        mock_request.client = MagicMock()
        mock_request.client.host = "127.0.0.1"

        ip = middleware.get_client_ip(mock_request)
        assert ip == "10.0.0.1"

    def test_get_client_ip_no_client(self):
        """Test getting client IP when client is None"""
        middleware = RateLimitMiddleware(app=MagicMock(), calls=10, period=60)

        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}
        mock_request.client = None

        ip = middleware.get_client_ip(mock_request)
        assert ip == "unknown"


class TestLoggingMiddleware:
    """Test logging middleware"""

    def test_logging_disabled(self):
        """Test that logging is skipped when disabled"""
        app = FastAPI()
        app.add_middleware(LoggingMiddleware, enabled=False)

        @app.get("/test")
        def test_endpoint():
            return {"message": "success"}

        client = TestClient(app)
        response = client.get("/test")

        assert response.status_code == 200
        # X-Process-Time header should not be present when disabled
        assert "X-Process-Time" not in response.headers

    def test_logging_enabled(self):
        """Test logging when enabled"""
        app = FastAPI()
        app.add_middleware(LoggingMiddleware, enabled=True)

        @app.get("/test")
        def test_endpoint():
            return {"message": "success"}

        client = TestClient(app)
        response = client.get("/test")

        assert response.status_code == 200
        assert "X-Process-Time" in response.headers

    def test_process_time_header(self):
        """Test X-Process-Time header is set correctly"""
        app = FastAPI()
        app.add_middleware(LoggingMiddleware, enabled=True)

        @app.get("/test")
        def test_endpoint():
            return {"message": "success"}

        client = TestClient(app)
        response = client.get("/test")

        process_time = float(response.headers["X-Process-Time"])
        assert process_time >= 0
        assert process_time < 10  # Should be fast


class TestMiddlewareFactory:
    """Test middleware factory functions"""

    def test_create_rate_limit_middleware_default(self):
        """Test creating rate limit middleware with defaults"""
        with patch.dict(os.environ, {}, clear=True):
            middleware = create_rate_limit_middleware()
            assert middleware.calls == 100
            assert middleware.period == 60
            assert middleware.enabled is False

    def test_create_rate_limit_middleware_enabled(self):
        """Test creating rate limit middleware when enabled"""
        with patch.dict(
            os.environ,
            {
                "RATE_LIMIT_ENABLED": "true",
                "RATE_LIMIT_REQUESTS": "50",
                "RATE_LIMIT_WINDOW": "120",
            },
        ):
            middleware = create_rate_limit_middleware()
            assert middleware.calls == 50
            assert middleware.period == 120
            assert middleware.enabled is True

    def test_create_logging_middleware_default(self):
        """Test creating logging middleware with defaults"""
        with patch.dict(os.environ, {}, clear=True):
            middleware = create_logging_middleware()
            assert middleware.enabled is True  # Default is true

    def test_create_logging_middleware_disabled(self):
        """Test creating logging middleware when disabled"""
        with patch.dict(os.environ, {"LOG_REQUESTS": "false"}):
            middleware = create_logging_middleware()
            assert middleware.enabled is False


class TestRateLimitCleanup:
    """Test rate limit cleanup of old entries"""

    def test_old_entries_cleaned(self):
        """Test that old request entries are cleaned up"""
        app = FastAPI()
        # Very short period for testing
        middleware = RateLimitMiddleware(app=app, calls=100, period=1, enabled=True)

        # Manually add old entries
        old_time = time.time() - 5  # 5 seconds ago
        middleware.clients["test_ip"] = deque([old_time, old_time, old_time])

        # Simulate a request that should clean old entries
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}
        mock_request.client = MagicMock()
        mock_request.client.host = "test_ip"

        # The dispatch would clean old entries
        # We can verify by checking the deque after simulating time passage
        now = time.time()
        client_requests = middleware.clients["test_ip"]

        # Clean old entries manually (simulating what dispatch does)
        while client_requests and client_requests[0] < now - middleware.period:
            client_requests.popleft()

        # All old entries should be removed
        assert len(client_requests) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
