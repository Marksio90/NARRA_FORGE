"""
API Gateway API - NarraForge 3.0 Phase 5
Endpoints for API gateway management and monitoring
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.services.api_gateway import (
    api_gateway,
    RateLimitConfig,
    RateLimitStrategy,
    CachePolicy,
    AuthType
)

router = APIRouter(prefix="/gateway")


# Request/Response Models
class ClientRegistrationRequest(BaseModel):
    """Request to register API client"""
    name: str
    tier: str = "standard"
    rate_limit_override: Optional[Dict[str, Any]] = None
    allowed_endpoints: Optional[List[str]] = None
    ip_whitelist: Optional[List[str]] = None


class ClientResponse(BaseModel):
    """Client response"""
    success: bool
    client: Optional[Dict[str, Any]] = None
    api_key: Optional[str] = None
    message: str = ""


class EndpointRegistrationRequest(BaseModel):
    """Request to register endpoint"""
    path: str
    method: str
    service: str
    auth_required: bool = True
    auth_type: str = "jwt"
    cache_policy: str = "no_cache"
    timeout_seconds: int = 30
    description: str = ""


class EndpointResponse(BaseModel):
    """Endpoint response"""
    success: bool
    endpoint: Optional[Dict[str, Any]] = None
    message: str = ""


class RequestProcessRequest(BaseModel):
    """Simulated request processing"""
    endpoint_path: str
    method: str
    headers: Dict[str, str] = {}
    query_params: Dict[str, Any] = {}
    body: Optional[Dict[str, Any]] = None
    ip_address: str = "127.0.0.1"


# Endpoints

@router.get("/health")
async def gateway_health():
    """Get gateway health status"""
    metrics = api_gateway.get_metrics()
    return {
        "success": True,
        "status": "healthy",
        "metrics": metrics
    }


@router.post("/clients/register", response_model=ClientResponse)
async def register_client(request: ClientRegistrationRequest):
    """
    Register a new API client

    Creates API key and configures rate limiting based on tier.
    """
    try:
        rate_limit = None
        if request.rate_limit_override:
            rate_limit = RateLimitConfig(
                requests_per_minute=request.rate_limit_override.get("requests_per_minute", 60),
                requests_per_hour=request.rate_limit_override.get("requests_per_hour", 1000),
                requests_per_day=request.rate_limit_override.get("requests_per_day", 10000),
                burst_limit=request.rate_limit_override.get("burst_limit", 100)
            )

        client = api_gateway.register_client(
            name=request.name,
            tier=request.tier,
            rate_limit_override=rate_limit,
            allowed_endpoints=request.allowed_endpoints,
            ip_whitelist=request.ip_whitelist
        )

        return ClientResponse(
            success=True,
            client=client.to_dict(),
            api_key=client.api_key,
            message="Client registered successfully"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clients/{client_id}", response_model=ClientResponse)
async def get_client(client_id: str):
    """Get client details"""
    try:
        client = api_gateway.get_client(client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        return ClientResponse(
            success=True,
            client=client.to_dict(),
            message="Client retrieved"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clients/{client_id}/usage")
async def get_client_usage(client_id: str):
    """Get client usage statistics"""
    try:
        usage = api_gateway.get_client_usage(client_id)
        if not usage:
            raise HTTPException(status_code=404, detail="Client not found")

        return {
            "success": True,
            "usage": usage
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clients/{client_id}/rate-limit")
async def check_rate_limit(client_id: str):
    """Check current rate limit status"""
    try:
        status = api_gateway.check_rate_limit(client_id)
        return {
            "success": True,
            "rate_limit": status
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/endpoints/register", response_model=EndpointResponse)
async def register_endpoint(request: EndpointRegistrationRequest):
    """Register a new API endpoint"""
    try:
        auth_type = AuthType(request.auth_type)
        cache_policy = CachePolicy(request.cache_policy)

        endpoint = api_gateway.register_endpoint(
            path=request.path,
            method=request.method,
            service=request.service,
            auth_required=request.auth_required,
            auth_type=auth_type,
            cache_policy=cache_policy,
            timeout_seconds=request.timeout_seconds,
            description=request.description
        )

        return EndpointResponse(
            success=True,
            endpoint=endpoint.to_dict(),
            message="Endpoint registered"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/endpoints")
async def get_endpoints(
    service: Optional[str] = None,
    include_deprecated: bool = False
):
    """Get all registered endpoints"""
    try:
        endpoints = api_gateway.get_endpoints(
            service=service,
            include_deprecated=include_deprecated
        )

        return {
            "success": True,
            "endpoints": [e.to_dict() for e in endpoints],
            "count": len(endpoints)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/endpoints/{endpoint_id}/deprecate")
async def deprecate_endpoint(
    endpoint_id: str,
    deprecation_date: str,
    replacement: Optional[str] = None
):
    """Mark endpoint as deprecated"""
    try:
        dep_date = datetime.fromisoformat(deprecation_date)
        api_gateway.deprecate_endpoint(endpoint_id, dep_date, replacement)

        return {
            "success": True,
            "message": f"Endpoint {endpoint_id} marked as deprecated"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/circuit-breakers")
async def get_circuit_breakers():
    """Get circuit breaker states"""
    try:
        metrics = api_gateway.get_metrics()
        return {
            "success": True,
            "circuit_breakers": metrics.get("circuit_breakers", {})
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/circuit-breakers/{service}")
async def check_circuit_breaker(service: str):
    """Check circuit breaker for specific service"""
    try:
        status = api_gateway.check_circuit_breaker(service)
        return {
            "success": True,
            "service": service,
            "circuit_breaker": status
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/clear")
async def clear_cache(pattern: Optional[str] = None):
    """Clear response cache"""
    try:
        api_gateway.clear_cache(pattern)
        return {
            "success": True,
            "message": f"Cache cleared" + (f" for pattern: {pattern}" if pattern else "")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs")
async def get_request_logs(
    client_id: Optional[str] = None,
    endpoint: Optional[str] = None,
    status_code: Optional[int] = None,
    limit: int = 100
):
    """Get request logs"""
    try:
        logs = api_gateway.get_request_logs(
            client_id=client_id,
            endpoint=endpoint,
            status_code=status_code,
            limit=limit
        )

        return {
            "success": True,
            "logs": [log.to_dict() for log in logs],
            "count": len(logs)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_gateway_metrics():
    """Get gateway metrics"""
    try:
        metrics = api_gateway.get_metrics()
        return {
            "success": True,
            "metrics": metrics
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tiers")
async def get_rate_limit_tiers():
    """Get available rate limit tiers"""
    from app.services.api_gateway import TIER_RATE_LIMITS
    return {
        "success": True,
        "tiers": {
            name: config.to_dict()
            for name, config in TIER_RATE_LIMITS.items()
        }
    }
