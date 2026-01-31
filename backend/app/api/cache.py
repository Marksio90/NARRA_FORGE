"""
Cache Layer API - NarraForge 3.0 Phase 5
Endpoints for cache management and monitoring
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from app.services.cache_layer import (
    cache_layer,
    CacheConfig,
    CacheLevel,
    EvictionPolicy,
    CACHE_PATTERNS
)

router = APIRouter(prefix="/cache")


# Request/Response Models
class NamespaceCreateRequest(BaseModel):
    """Request to create namespace"""
    name: str
    max_size: int = 1000
    max_memory_mb: int = 100
    default_ttl_seconds: int = 300
    eviction_policy: str = "lru"


class NamespaceResponse(BaseModel):
    """Namespace response"""
    success: bool
    namespace: Optional[Dict[str, Any]] = None
    message: str = ""


class CacheSetRequest(BaseModel):
    """Request to set cache value"""
    key: str
    value: Any
    ttl_seconds: Optional[int] = None
    tags: Optional[List[str]] = None
    level: str = "l2_local"


class CacheResponse(BaseModel):
    """Cache response"""
    success: bool
    value: Any = None
    cached: bool = False
    message: str = ""


class WarmCacheRequest(BaseModel):
    """Request to warm cache"""
    items: List[Dict[str, Any]]


class InvalidateRequest(BaseModel):
    """Request to invalidate cache"""
    tags: Optional[List[str]] = None
    pattern: Optional[str] = None


# Endpoints

@router.get("/health")
async def cache_health():
    """Get cache health status"""
    stats = cache_layer.get_stats()
    return {
        "success": True,
        "status": "healthy",
        "stats": stats
    }


@router.post("/namespaces/create", response_model=NamespaceResponse)
async def create_namespace(request: NamespaceCreateRequest):
    """Create a new cache namespace"""
    try:
        eviction = EvictionPolicy(request.eviction_policy)

        config = CacheConfig(
            max_size=request.max_size,
            max_memory_mb=request.max_memory_mb,
            default_ttl_seconds=request.default_ttl_seconds,
            eviction_policy=eviction
        )

        namespace = cache_layer.create_namespace(request.name, config)

        return NamespaceResponse(
            success=True,
            namespace=namespace.to_dict(),
            message="Namespace created"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/namespaces")
async def get_namespaces():
    """Get all cache namespaces"""
    try:
        namespaces = cache_layer.get_namespaces()
        return {
            "success": True,
            "namespaces": namespaces,
            "count": len(namespaces)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/namespaces/{namespace}")
async def get_namespace(namespace: str):
    """Get namespace details"""
    try:
        ns = cache_layer.get_namespace(namespace)
        if not ns:
            raise HTTPException(status_code=404, detail="Namespace not found")

        return {
            "success": True,
            "namespace": ns.to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get/{key}")
async def get_cached_value(
    key: str,
    namespace: str = "default"
):
    """Get value from cache"""
    try:
        value = cache_layer.get(key, namespace)

        return CacheResponse(
            success=True,
            value=value,
            cached=value is not None,
            message="Cache hit" if value is not None else "Cache miss"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/set", response_model=CacheResponse)
async def set_cached_value(request: CacheSetRequest, namespace: str = "default"):
    """Set value in cache"""
    try:
        level = CacheLevel(request.level)

        cache_layer.set(
            key=request.key,
            value=request.value,
            namespace=namespace,
            ttl_seconds=request.ttl_seconds,
            tags=request.tags,
            level=level
        )

        return CacheResponse(
            success=True,
            cached=True,
            message=f"Value cached with key: {request.key}"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{key}")
async def delete_cached_value(key: str, namespace: str = "default"):
    """Delete value from cache"""
    try:
        deleted = cache_layer.delete(key, namespace)

        return {
            "success": True,
            "deleted": deleted,
            "message": "Value deleted" if deleted else "Key not found"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/invalidate")
async def invalidate_cache(request: InvalidateRequest, namespace: Optional[str] = None):
    """Invalidate cache entries by tags or pattern"""
    try:
        count = 0

        if request.tags:
            count += cache_layer.invalidate_by_tags(request.tags, namespace)

        if request.pattern:
            count += cache_layer.invalidate_by_pattern(request.pattern, namespace)

        return {
            "success": True,
            "invalidated_count": count,
            "message": f"Invalidated {count} entries"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear")
async def clear_cache(namespace: Optional[str] = None):
    """Clear cache"""
    try:
        cache_layer.clear(namespace)

        return {
            "success": True,
            "message": f"Cache cleared" + (f" for namespace: {namespace}" if namespace else " (all namespaces)")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/warm", response_model=CacheResponse)
async def warm_cache(request: WarmCacheRequest, namespace: str = "default"):
    """Warm cache with items"""
    try:
        cache_layer.warm(request.items, namespace)

        return CacheResponse(
            success=True,
            message=f"Warmed {len(request.items)} items"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/keys")
async def get_keys(
    namespace: str = "default",
    pattern: Optional[str] = None
):
    """Get all keys in namespace"""
    try:
        keys = cache_layer.get_keys(namespace, pattern)

        return {
            "success": True,
            "keys": keys,
            "count": len(keys)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entries")
async def get_entries(namespace: str = "default", limit: int = 100):
    """Get cache entries for inspection"""
    try:
        entries = cache_layer.get_entries(namespace, limit)

        return {
            "success": True,
            "entries": entries,
            "count": len(entries)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_cache_stats(namespace: Optional[str] = None):
    """Get cache statistics"""
    try:
        stats = cache_layer.get_stats(namespace)
        return {
            "success": True,
            "stats": stats
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patterns")
async def get_cache_patterns():
    """Get predefined cache key patterns"""
    return {
        "success": True,
        "patterns": CACHE_PATTERNS
    }


@router.post("/cleanup")
async def cleanup_expired():
    """Clean up expired entries"""
    try:
        count = await cache_layer.cleanup()
        return {
            "success": True,
            "cleaned_count": count,
            "message": f"Cleaned up {count} expired entries"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/eviction-policies")
async def get_eviction_policies():
    """Get available eviction policies"""
    return {
        "success": True,
        "policies": [
            {
                "name": policy.value,
                "description": {
                    "lru": "Least Recently Used - evicts entries not accessed recently",
                    "lfu": "Least Frequently Used - evicts entries with lowest access count",
                    "fifo": "First In First Out - evicts oldest entries first",
                    "ttl": "Time To Live - evicts based on expiration only",
                    "random": "Random - randomly selects entries to evict"
                }.get(policy.value, "")
            }
            for policy in EvictionPolicy
        ]
    }


@router.get("/levels")
async def get_cache_levels():
    """Get cache hierarchy levels"""
    return {
        "success": True,
        "levels": [
            {
                "level": level.value,
                "description": {
                    "l1_memory": "Fastest, smallest - in-memory LRU cache",
                    "l2_local": "Fast, larger - local namespace cache",
                    "l3_distributed": "Slower, largest - distributed cache (Redis)"
                }.get(level.value, "")
            }
            for level in CacheLevel
        ]
    }
