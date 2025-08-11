from fastapi import APIRouter, Depends
from datetime import datetime
from typing import Dict
import psutil
import os

from services.database import get_db
from services.redis_client import redis_client
from services.ml_service import MLService
from services.websocket_manager import WebSocketManager

router = APIRouter()

@router.get("/system")
async def get_system_metrics():
    """Get system resource metrics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": {
                "usage_percent": cpu_percent,
                "cores": psutil.cpu_count()
            },
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "usage_percent": memory.percent
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "usage_percent": disk.percent
            }
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/services")
async def get_services_status(
    ml_service: MLService = Depends(lambda: MLService())
):
    """Get status of all services"""
    try:
        # Check database
        try:
            from services.database import engine
            async with engine.begin() as conn:
                await conn.execute("SELECT 1")
            db_status = "healthy"
        except:
            db_status = "unhealthy"
        
        # Check Redis
        redis_status = "healthy" if await redis_client.ping() else "unhealthy"
        
        # Check ML service
        ml_status = "healthy" if ml_service.is_ready else "unhealthy"
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "database": {
                    "status": db_status,
                    "type": "PostgreSQL"
                },
                "cache": {
                    "status": redis_status,
                    "type": "Redis"
                },
                "ml_models": {
                    "status": ml_status,
                    "version": "v1.0.0"
                }
            },
            "overall_status": "healthy" if all([
                db_status == "healthy",
                redis_status == "healthy",
                ml_status == "healthy"
            ]) else "degraded"
        }
    except Exception as e:
        return {"error": str(e), "overall_status": "unhealthy"}

@router.get("/websockets")
async def get_websocket_stats(
    ws_manager: WebSocketManager = Depends(lambda: WebSocketManager())
):
    """Get WebSocket connection statistics"""
    try:
        stats = ws_manager.get_connection_stats()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            **stats
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/alerts")
async def get_active_alerts():
    """Get active system alerts"""
    alerts = []
    
    # Check CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)
    if cpu_percent > 80:
        alerts.append({
            "level": "warning",
            "type": "system",
            "message": f"High CPU usage: {cpu_percent}%",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    # Check memory usage
    memory = psutil.virtual_memory()
    if memory.percent > 85:
        alerts.append({
            "level": "warning",
            "type": "system",
            "message": f"High memory usage: {memory.percent}%",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    # Check disk usage
    disk = psutil.disk_usage('/')
    if disk.percent > 90:
        alerts.append({
            "level": "critical",
            "type": "system",
            "message": f"Critical disk usage: {disk.percent}%",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    return {
        "active_alerts": alerts,
        "alert_count": len(alerts),
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/live-metrics")
async def get_live_metrics(
    ml_service: MLService = Depends(lambda: MLService())
):
    """Get live system metrics for real-time monitoring"""
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        # Service status
        try:
            from services.database import engine
            async with engine.begin() as conn:
                await conn.execute("SELECT 1")
            db_status = "healthy"
            db_latency = 5.2  # Would measure actual latency in production
        except:
            db_status = "unhealthy"
            db_latency = None
        
        redis_status = "healthy" if await redis_client.ping() else "unhealthy"
        ml_status = "healthy" if ml_service.is_ready else "unhealthy"
        
        # Get cached API stats
        api_stats = await redis_client.get_api_stats()
        total_requests = api_stats.get('total_requests', 0) if api_stats else 0
        avg_response_time = api_stats.get('avg_response_time', 45) if api_stats else 45
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "cpu_usage": round(cpu_percent, 1),
                "memory_usage": round(memory.percent, 1),
                "memory_used_gb": round(memory.used / (1024**3), 2),
                "uptime_hours": round(psutil.boot_time() / 3600, 1)
            },
            "services": {
                "database": {
                    "status": db_status,
                    "latency_ms": db_latency
                },
                "redis": {
                    "status": redis_status
                },
                "ml_models": {
                    "status": ml_status,
                    "loaded_models": 3 if ml_service.is_ready else 0
                }
            },
            "api": {
                "total_requests": total_requests,
                "avg_response_time_ms": round(avg_response_time, 1),
                "requests_per_minute": round(total_requests / max(1, 60), 1)  # Simplified calculation
            },
            "alerts": {
                "active": 0,
                "warnings": 1 if cpu_percent > 70 else 0,
                "errors": 1 if db_status == "unhealthy" else 0
            }
        }
        
    except Exception as e:
        return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}

@router.get("/logs/recent")
async def get_recent_logs(limit: int = 50):
    """Get recent application logs"""
    # In production, this would fetch from actual log files or log aggregation service
    return {
        "logs": [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "level": "INFO",
                "message": "Sample log entry",
                "service": "backend"
            }
        ],
        "total": 1
    }

monitoring_router = router