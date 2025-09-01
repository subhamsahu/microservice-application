"""
Health check router for monitoring service and connection status.
"""
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.core.logger import logger
from app.services.elasticsearch import elasticsearch_service
from app.services.rabbitmq.connection import rabbitmq_manager
from app.core.database import db
from app.core.config import config
from app.core.exceptions import AppException
from app.core.constants import SERVICE_NAME

router = APIRouter()


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    response_description="Comprehensive Health Check API",
    tags=["Health"],
    operation_id="health_v1"
)
async def auth_check_health_handler():
    """
    Comprehensive health check endpoint.
    Returns the status of all critical services.
    """
    logger.info(f"{SERVICE_NAME}: check_health() method called")
    
    health_status = {
        "service": SERVICE_NAME,
        "status": "healthy",
        "version": "0.0.1",
        "connections": {
            "database": "unknown",
            "elasticsearch": "disabled",
            "rabbitmq": "unknown"
        },
        "config": {
            "elasticsearch_enabled": config.ENABLE_ES,
            "apm_enabled": config.ENABLE_APM
        }
    }
    
    overall_healthy = True
    
    try:
        # Check Database Connection
        if db:
            check_health = await db.health_check_async()
            if not check_health:
                overall_healthy = False
                health_status["connections"]["database"] = "unhealthy"
            else:
                health_status["connections"]["database"] = "healthy"
        else:
            health_status["connections"]["database"] = "disconnected"
            overall_healthy = False
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["connections"]["database"] = "unhealthy"
        overall_healthy = False
    
    try:
        # Check ElasticSearch Connection
        if config.ENABLE_ES:
            if elasticsearch_service.client and elasticsearch_service._connected:
                try:
                    await elasticsearch_service.client.cluster.health()
                    health_status["connections"]["elasticsearch"] = "healthy"
                except Exception:
                    health_status["connections"]["elasticsearch"] = "unhealthy"
                    overall_healthy = False
            else:
                health_status["connections"]["elasticsearch"] = "disconnected"
                overall_healthy = False
        else:
            health_status["connections"]["elasticsearch"] = "disabled"
    except Exception as e:
        logger.error(f"Elasticsearch health check failed: {e}")
        health_status["connections"]["elasticsearch"] = "unhealthy"
        overall_healthy = False
    
    try:
        # Check RabbitMQ Connection
        if rabbitmq_manager.is_connected():
            health_status["connections"]["rabbitmq"] = "healthy"
        else:
            health_status["connections"]["rabbitmq"] = "disconnected"
            overall_healthy = False
    except Exception as e:
        logger.error(f"RabbitMQ health check failed: {e}")
        health_status["connections"]["rabbitmq"] = "unhealthy"
        overall_healthy = False
    
    # Set overall status
    if not overall_healthy:
        health_status["status"] = "degraded"
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=health_status
        )
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=health_status
    )


@router.get(
    "/health/ready",
    status_code=status.HTTP_200_OK,
    response_description="Readiness Check",
    tags=["Health"],
    operation_id="readiness_v1"
)
async def readiness_check():
    """
    Readiness probe for Kubernetes deployments.
    Returns 200 if the service is ready to serve traffic.
    """
    try:
        # Check if essential services are available
        ready = True
        
        if not (db and hasattr(db, '_initialized') and db._initialized):
            ready = False
        
        # RabbitMQ should be connected for messaging
        if not rabbitmq_manager.is_connected():
            ready = False
        
        if ready:
            return {"status": "ready"}
        else:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"status": "not ready"}
            )
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not ready", "error": str(e)}
        )


@router.get(
    "/health/live",
    status_code=status.HTTP_200_OK,
    response_description="Liveness Check",
    tags=["Health"],
    operation_id="liveness_v1"
)
async def liveness_check():
    """
    Liveness probe for Kubernetes deployments.
    Returns 200 if the service is alive.
    """
    return {"status": "alive"}
