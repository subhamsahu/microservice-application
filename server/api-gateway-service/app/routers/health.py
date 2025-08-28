"""
Health check router for monitoring service and connection status.
"""
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.core.logger import logger
from app.services.elasticsearch import ElasticSearchService
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
async def api_gateway_check_health_handler():
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
            "elasticsearch": "disabled"
        },
        "config": {
            "elasticsearch_enabled": config.ENABLE_ES,
            "apm_enabled": config.ENABLE_APM
        }
    }
    
    overall_healthy = True
    
    try:
        # Check ElasticSearch Connection
        if config.ENABLE_ES:
            elastic_service = ElasticSearchService(config.ELASTICSEARCH_URL)
            if elastic_service and hasattr(elastic_service, 'client') and elastic_service.client:
                try:
                    elastic_service.check_connection()
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
        # API Gateway service is ready if it's running
        # No critical dependencies to check
        return {"status": "ready"}
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
