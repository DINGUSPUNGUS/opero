"""
Monitoring and health check endpoints for Opero platform
"""
import time
import psutil
import asyncio
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from app.core.database import get_db
from app.core.performance import redis_client
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


@router.get("/health")
async def health_check():
    """Comprehensive health check"""
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "checks": {}
    }
    
    # Check API
    health_status["checks"]["api"] = {
        "status": "healthy",
        "response_time": 0.001
    }
    
    # Check database
    try:
        start_time = time.time()
        async with get_db() as db:
            await db.execute(text("SELECT 1"))
        db_response_time = time.time() - start_time
        
        health_status["checks"]["database"] = {
            "status": "healthy",
            "response_time": db_response_time
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Check Redis
    try:
        start_time = time.time()
        redis_client.ping()
        redis_response_time = time.time() - start_time
        
        health_status["checks"]["redis"] = {
            "status": "healthy",
            "response_time": redis_response_time
        }
    except Exception as e:
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    return health_status


@router.get("/metrics/system")
async def system_metrics():
    """System performance metrics"""
    try:
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory metrics
        memory = psutil.virtual_memory()
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        
        # Network metrics
        network = psutil.net_io_counters()
        
        return {
            "cpu": {
                "usage_percent": cpu_percent,
                "count": cpu_count,
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percent": memory.percent
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            },
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            },
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system metrics: {str(e)}")


@router.get("/metrics/application")
async def application_metrics():
    """Application-specific metrics"""
    try:
        # Database metrics
        db_metrics = await _get_database_metrics()
        
        # Redis metrics
        redis_metrics = await _get_redis_metrics()
        
        # API metrics (would integrate with your request tracking)
        api_metrics = {
            "total_requests": 0,  # Implement request counter
            "error_rate": 0,      # Implement error tracking
            "avg_response_time": 0 # Implement response time tracking
        }
        
        return {
            "database": db_metrics,
            "cache": redis_metrics,
            "api": api_metrics,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get application metrics: {str(e)}")


async def _get_database_metrics() -> Dict[str, Any]:
    """Get database performance metrics"""
    try:
        async with get_db() as db:
            # Connection count
            result = await db.execute(text("""
                SELECT count(*) as connection_count 
                FROM pg_stat_activity 
                WHERE state = 'active'
            """))
            connection_count = result.scalar()
            
            # Database size
            result = await db.execute(text("""
                SELECT pg_size_pretty(pg_database_size(current_database())) as size
            """))
            db_size = result.scalar()
            
            return {
                "active_connections": connection_count,
                "database_size": db_size,
                "status": "healthy"
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


async def _get_redis_metrics() -> Dict[str, Any]:
    """Get Redis performance metrics"""
    try:
        info = redis_client.info()
        return {
            "connected_clients": info.get("connected_clients", 0),
            "used_memory": info.get("used_memory", 0),
            "used_memory_human": info.get("used_memory_human", "0B"),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
            "status": "healthy"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@router.get("/logs/recent")
async def recent_logs(lines: int = 100):
    """Get recent application logs"""
    try:
        # Read recent logs from file
        log_file = "logs/opero.log"
        try:
            with open(log_file, "r") as f:
                log_lines = f.readlines()
                recent_lines = log_lines[-lines:] if len(log_lines) > lines else log_lines
                return {
                    "logs": [line.strip() for line in recent_lines],
                    "total_lines": len(recent_lines),
                    "timestamp": time.time()
                }
        except FileNotFoundError:
            return {
                "logs": [],
                "total_lines": 0,
                "message": "Log file not found",
                "timestamp": time.time()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read logs: {str(e)}")


@router.get("/alerts")
async def active_alerts():
    """Get active system alerts"""
    alerts = []
    
    # Check system metrics for alerts
    try:
        # Memory alert
        memory = psutil.virtual_memory()
        if memory.percent > 85:
            alerts.append({
                "type": "memory",
                "severity": "warning",
                "message": f"High memory usage: {memory.percent:.1f}%",
                "timestamp": time.time()
            })
        
        # CPU alert
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 80:
            alerts.append({
                "type": "cpu",
                "severity": "warning",
                "message": f"High CPU usage: {cpu_percent:.1f}%",
                "timestamp": time.time()
            })
        
        # Disk alert
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        if disk_percent > 90:
            alerts.append({
                "type": "disk",
                "severity": "critical",
                "message": f"Low disk space: {disk_percent:.1f}% used",
                "timestamp": time.time()
            })
        
    except Exception as e:
        alerts.append({
            "type": "monitoring",
            "severity": "error",
            "message": f"Failed to check system metrics: {str(e)}",
            "timestamp": time.time()
        })
    
    return {
        "alerts": alerts,
        "count": len(alerts),
        "timestamp": time.time()
    }
