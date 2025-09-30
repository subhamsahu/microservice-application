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
async def chat_check_health_handler():
    """
    Comprehensive health check endpoint.
    Returns the status of all critical services.
    """
    logger.info(f"{SERVICE_NAME}: check_health() method called")
    
    health_status = {
        "service": SERVICE_NAME,
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "services": {
            "database": "unknown",
            "elasticsearch": "unknown",
            "redis": "unknown", 
            "rabbitmq": "unknown"
        }
    }
    
    try:
        # Check database connection
        if db and await db.health_check_async():
            health_status["services"]["database"] = "healthy"
        else:
            health_status["services"]["database"] = "unhealthy"
            
        # Check Elasticsearch connection
        if config.ENABLE_ES and await elasticsearch_service.health_check():
            health_status["services"]["elasticsearch"] = "healthy"
        else:
            health_status["services"]["elasticsearch"] = "disabled" if not config.ENABLE_ES else "unhealthy"
            
        # Check RabbitMQ connection
        if rabbitmq_manager.is_connected():
            health_status["services"]["rabbitmq"] = "healthy"
        else:
            health_status["services"]["rabbitmq"] = "unhealthy"
            
        # Check Redis connection
        from app.services.redis import redis_service
        if await redis_service.health_check():
            health_status["services"]["redis"] = "healthy"
        else:
            health_status["services"]["redis"] = "unhealthy"
            
        # Determine overall status
        unhealthy_services = [name for name, status in health_status["services"].items() 
                            if status == "unhealthy"]
        
        if unhealthy_services:
            health_status["status"] = "degraded"
            
        logger.info(f"{SERVICE_NAME}: Health check completed - {health_status['status']}")
        
        return JSONResponse(
            status_code=status.HTTP_200_OK if health_status["status"] != "unhealthy" else status.HTTP_503_SERVICE_UNAVAILABLE,
            content=health_status
        )
        
    except Exception as error:
        logger.error(f"{SERVICE_NAME}: Health check failed - {error}")
        health_status["status"] = "unhealthy"
        health_status["error"] = str(error)
        
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=health_status
        )