"""
Performance optimization middleware and caching for Opero platform
"""
import time
import redis
import json
import hashlib
from typing import Any, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import get_settings

settings = get_settings()

# Redis client for caching
redis_client = redis.from_url(settings.redis_url, decode_responses=True)


class CacheMiddleware(BaseHTTPMiddleware):
    """Redis-based caching middleware"""
    
    def __init__(self, app, cache_ttl: int = 300):
        super().__init__(app)
        self.cache_ttl = cache_ttl
        self.cacheable_methods = {"GET"}
        self.cacheable_paths = {
            "/contacts/stats",
            "/agent/analytics",
            "/health",
            "/info"
        }
    
    async def dispatch(self, request: Request, call_next):
        # Only cache GET requests to specific paths
        if (request.method not in self.cacheable_methods or 
            not any(request.url.path.startswith(path) for path in self.cacheable_paths)):
            return await call_next(request)
        
        # Generate cache key
        cache_key = self._generate_cache_key(request)
        
        # Try to get from cache
        try:
            cached_response = redis_client.get(cache_key)
            if cached_response:
                data = json.loads(cached_response)
                return JSONResponse(
                    content=data,
                    headers={"X-Cache": "HIT"}
                )
        except Exception:
            pass  # Cache miss or error, continue to origin
        
        # Get response from origin
        response = await call_next(request)
        
        # Cache successful responses
        if response.status_code == 200 and hasattr(response, 'body'):
            try:
                # Read response body
                body = b""
                async for chunk in response.body_iterator:
                    body += chunk
                
                # Parse and cache
                data = json.loads(body.decode())
                redis_client.setex(
                    cache_key, 
                    self.cache_ttl, 
                    json.dumps(data)
                )
                
                # Return response with cache headers
                return JSONResponse(
                    content=data,
                    status_code=response.status_code,
                    headers={"X-Cache": "MISS"}
                )
            except Exception:
                pass  # Don't cache on error
        
        return response
    
    def _generate_cache_key(self, request: Request) -> str:
        """Generate cache key from request"""
        key_data = f"{request.method}:{request.url.path}:{request.url.query}"
        return f"cache:{hashlib.md5(key_data.encode()).hexdigest()}"


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Performance monitoring middleware"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Add request ID for tracing
        request_id = hashlib.md5(f"{time.time()}:{id(request)}".encode()).hexdigest()[:8]
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Add performance headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id
        
        # Log slow requests
        if process_time > 1.0:
            print(f"⚠️ Slow request: {request.method} {request.url.path} took {process_time:.2f}s")
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Redis-based rate limiting middleware"""
    
    def __init__(self, app, requests_per_minute: int = 60, burst: int = 10):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst = burst
        self.window_size = 60  # 1 minute
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check rate limit
        if not await self._check_rate_limit(client_ip):
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {self.requests_per_minute} requests per minute allowed"
                },
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0"
                }
            )
        
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP from request"""
        # Check for forwarded IP first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    async def _check_rate_limit(self, client_ip: str) -> bool:
        """Check if client is within rate limit"""
        try:
            current_time = int(time.time())
            key = f"rate_limit:{client_ip}:{current_time // self.window_size}"
            
            # Get current count
            current_count = redis_client.get(key)
            if current_count is None:
                current_count = 0
            else:
                current_count = int(current_count)
            
            # Check limit
            if current_count >= self.requests_per_minute:
                return False
            
            # Increment counter
            pipe = redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, self.window_size)
            pipe.execute()
            
            return True
        except Exception:
            # If Redis fails, allow request (fail open)
            return True


# Connection pooling for database
from sqlalchemy.pool import QueuePool
from app.core.database import engine

# Configure connection pool
engine.pool_class = QueuePool
engine.pool_size = 20
engine.max_overflow = 30
engine.pool_pre_ping = True
engine.pool_recycle = 3600


# Background task processor using Celery
from celery import Celery

celery_app = Celery(
    "opero",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)


@celery_app.task
def process_background_task(task_type: str, data: dict):
    """Generic background task processor"""
    print(f"Processing background task: {task_type}")
    # Add your background processing logic here
    return {"status": "completed", "task_type": task_type}


# Metrics collection
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter(
    "http_requests_total", 
    "Total HTTP requests", 
    ["method", "endpoint", "status"]
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration",
    ["method", "endpoint"]
)


def record_metrics(request: Request, response: Response, process_time: float):
    """Record metrics for monitoring"""
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(process_time)


async def get_metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type="text/plain")
