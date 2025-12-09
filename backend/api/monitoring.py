"""
Production Monitoring and Metrics Module
Provides health checks, metrics collection, and monitoring utilities
"""

import time
import psutil
import asyncio
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Response
from pydantic import BaseModel

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


class SystemMetrics(BaseModel):
    """System metrics model"""
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_usage_percent: float
    timestamp: str


class ServiceMetrics(BaseModel):
    """Service-level metrics"""
    uptime_seconds: float
    total_requests: int
    failed_requests: int
    avg_response_time_ms: float
    timestamp: str


# Global metrics storage (use Redis in production)
METRICS = {
    "start_time": time.time(),
    "total_requests": 0,
    "failed_requests": 0,
    "response_times": [],
}


def get_system_metrics() -> SystemMetrics:
    """Get current system metrics"""
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return SystemMetrics(
        cpu_percent=psutil.cpu_percent(interval=0.1),
        memory_percent=memory.percent,
        memory_available_mb=memory.available / (1024 * 1024),
        disk_usage_percent=disk.percent,
        timestamp=datetime.utcnow().isoformat()
    )


def get_service_metrics() -> ServiceMetrics:
    """Get service-level metrics"""
    uptime = time.time() - METRICS["start_time"]
    avg_response_time = (
        sum(METRICS["response_times"][-100:]) / len(METRICS["response_times"][-100:])
        if METRICS["response_times"]
        else 0
    )
    
    return ServiceMetrics(
        uptime_seconds=uptime,
        total_requests=METRICS["total_requests"],
        failed_requests=METRICS["failed_requests"],
        avg_response_time_ms=avg_response_time * 1000,
        timestamp=datetime.utcnow().isoformat()
    )


@router.get("/metrics/system", response_model=SystemMetrics)
async def system_metrics():
    """Get system resource metrics"""
    return get_system_metrics()


@router.get("/metrics/service", response_model=ServiceMetrics)
async def service_metrics():
    """Get service-level metrics"""
    return get_service_metrics()


@router.get("/metrics/prometheus")
async def prometheus_metrics():
    """Prometheus-compatible metrics endpoint"""
    sys_metrics = get_system_metrics()
    svc_metrics = get_service_metrics()
    
    metrics_text = f"""# HELP cpu_usage_percent CPU usage percentage
# TYPE cpu_usage_percent gauge
cpu_usage_percent {sys_metrics.cpu_percent}

# HELP memory_usage_percent Memory usage percentage
# TYPE memory_usage_percent gauge
memory_usage_percent {sys_metrics.memory_percent}

# HELP disk_usage_percent Disk usage percentage
# TYPE disk_usage_percent gauge
disk_usage_percent {sys_metrics.disk_usage_percent}

# HELP service_uptime_seconds Service uptime in seconds
# TYPE service_uptime_seconds counter
service_uptime_seconds {svc_metrics.uptime_seconds}

# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total {svc_metrics.total_requests}

# HELP http_requests_failed Total failed HTTP requests
# TYPE http_requests_failed counter
http_requests_failed {svc_metrics.failed_requests}

# HELP http_response_time_ms Average response time in milliseconds
# TYPE http_response_time_ms gauge
http_response_time_ms {svc_metrics.avg_response_time_ms}
"""
    
    return Response(content=metrics_text, media_type="text/plain")


@router.get("/status")
async def service_status():
    """Comprehensive service status"""
    sys_metrics = get_system_metrics()
    svc_metrics = get_service_metrics()
    
    # Determine overall health
    health_status = "healthy"
    if sys_metrics.cpu_percent > 90 or sys_metrics.memory_percent > 90:
        health_status = "degraded"
    if sys_metrics.disk_usage_percent > 95:
        health_status = "critical"
    
    return {
        "status": health_status,
        "version": "1.0.0",
        "environment": "production",
        "system": sys_metrics.dict(),
        "service": svc_metrics.dict(),
        "timestamp": datetime.utcnow().isoformat()
    }


def track_request(response_time: float, failed: bool = False):
    """Track request metrics"""
    METRICS["total_requests"] += 1
    if failed:
        METRICS["failed_requests"] += 1
    METRICS["response_times"].append(response_time)
    
    # Keep only last 1000 response times
    if len(METRICS["response_times"]) > 1000:
        METRICS["response_times"] = METRICS["response_times"][-1000:]
