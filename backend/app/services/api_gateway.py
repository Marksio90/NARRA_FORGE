"""
Unified API Gateway - NarraForge 3.0 Phase 5
Centralized API management, routing, rate limiting, and request orchestration
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
from datetime import datetime, timedelta
import uuid
import hashlib
import time
import asyncio
from collections import defaultdict


class RateLimitStrategy(Enum):
    """Rate limiting strategies"""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"


class RequestPriority(Enum):
    """Request priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class AuthType(Enum):
    """Authentication types"""
    NONE = "none"
    API_KEY = "api_key"
    JWT = "jwt"
    OAUTH2 = "oauth2"
    BASIC = "basic"


class CachePolicy(Enum):
    """Cache policies for responses"""
    NO_CACHE = "no_cache"
    SHORT = "short"  # 1 minute
    MEDIUM = "medium"  # 5 minutes
    LONG = "long"  # 30 minutes
    EXTENDED = "extended"  # 2 hours


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class RateLimitConfig:
    """Rate limit configuration"""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_limit: int = 100
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW

    def to_dict(self) -> Dict[str, Any]:
        return {
            "requests_per_minute": self.requests_per_minute,
            "requests_per_hour": self.requests_per_hour,
            "requests_per_day": self.requests_per_day,
            "burst_limit": self.burst_limit,
            "strategy": self.strategy.value
        }


@dataclass
class RateLimitState:
    """Current rate limit state for a client"""
    client_id: str
    minute_count: int = 0
    hour_count: int = 0
    day_count: int = 0
    minute_reset: datetime = field(default_factory=datetime.now)
    hour_reset: datetime = field(default_factory=datetime.now)
    day_reset: datetime = field(default_factory=datetime.now)
    tokens: float = 0.0  # For token bucket
    last_request: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "client_id": self.client_id,
            "minute_count": self.minute_count,
            "hour_count": self.hour_count,
            "day_count": self.day_count,
            "minute_reset": self.minute_reset.isoformat(),
            "hour_reset": self.hour_reset.isoformat(),
            "day_reset": self.day_reset.isoformat()
        }


@dataclass
class APIEndpoint:
    """API endpoint configuration"""
    endpoint_id: str
    path: str
    method: str
    service: str
    version: str = "v1"
    auth_required: bool = True
    auth_type: AuthType = AuthType.JWT
    rate_limit: Optional[RateLimitConfig] = None
    cache_policy: CachePolicy = CachePolicy.NO_CACHE
    timeout_seconds: int = 30
    retry_count: int = 3
    priority: RequestPriority = RequestPriority.NORMAL
    deprecated: bool = False
    deprecation_date: Optional[datetime] = None
    replacement_endpoint: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "endpoint_id": self.endpoint_id,
            "path": self.path,
            "method": self.method,
            "service": self.service,
            "version": self.version,
            "auth_required": self.auth_required,
            "auth_type": self.auth_type.value,
            "rate_limit": self.rate_limit.to_dict() if self.rate_limit else None,
            "cache_policy": self.cache_policy.value,
            "timeout_seconds": self.timeout_seconds,
            "retry_count": self.retry_count,
            "priority": self.priority.value,
            "deprecated": self.deprecated,
            "tags": self.tags,
            "description": self.description
        }


@dataclass
class APIClient:
    """API client/consumer configuration"""
    client_id: str
    name: str
    api_key: str
    secret_hash: str
    tier: str = "standard"  # free, standard, premium, enterprise
    rate_limit_override: Optional[RateLimitConfig] = None
    allowed_endpoints: List[str] = field(default_factory=list)  # Empty = all
    blocked_endpoints: List[str] = field(default_factory=list)
    ip_whitelist: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "client_id": self.client_id,
            "name": self.name,
            "tier": self.tier,
            "rate_limit_override": self.rate_limit_override.to_dict() if self.rate_limit_override else None,
            "allowed_endpoints": self.allowed_endpoints,
            "blocked_endpoints": self.blocked_endpoints,
            "ip_whitelist": self.ip_whitelist,
            "created_at": self.created_at.isoformat(),
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "is_active": self.is_active,
            "metadata": self.metadata
        }


@dataclass
class CircuitBreaker:
    """Circuit breaker for service protection"""
    service_name: str
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    failure_threshold: int = 5
    success_threshold: int = 3
    timeout_seconds: int = 60
    last_failure: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    half_open_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "service_name": self.service_name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "failure_threshold": self.failure_threshold,
            "success_threshold": self.success_threshold,
            "timeout_seconds": self.timeout_seconds,
            "last_failure": self.last_failure.isoformat() if self.last_failure else None
        }


@dataclass
class APIRequest:
    """Incoming API request"""
    request_id: str
    client_id: str
    endpoint_path: str
    method: str
    headers: Dict[str, str]
    query_params: Dict[str, Any]
    body: Optional[Dict[str, Any]]
    ip_address: str
    timestamp: datetime = field(default_factory=datetime.now)
    priority: RequestPriority = RequestPriority.NORMAL
    trace_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "client_id": self.client_id,
            "endpoint_path": self.endpoint_path,
            "method": self.method,
            "ip_address": self.ip_address,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority.value,
            "trace_id": self.trace_id
        }


@dataclass
class APIResponse:
    """API response"""
    request_id: str
    status_code: int
    headers: Dict[str, str]
    body: Any
    processing_time_ms: float
    cached: bool = False
    trace_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "status_code": self.status_code,
            "processing_time_ms": self.processing_time_ms,
            "cached": self.cached,
            "trace_id": self.trace_id
        }


@dataclass
class RequestLog:
    """Request log entry"""
    log_id: str
    request_id: str
    client_id: str
    endpoint: str
    method: str
    status_code: int
    processing_time_ms: float
    timestamp: datetime
    ip_address: str
    user_agent: Optional[str] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "log_id": self.log_id,
            "request_id": self.request_id,
            "client_id": self.client_id,
            "endpoint": self.endpoint,
            "method": self.method,
            "status_code": self.status_code,
            "processing_time_ms": self.processing_time_ms,
            "timestamp": self.timestamp.isoformat(),
            "ip_address": self.ip_address,
            "error_message": self.error_message
        }


# Tier-based rate limits
TIER_RATE_LIMITS: Dict[str, RateLimitConfig] = {
    "free": RateLimitConfig(
        requests_per_minute=10,
        requests_per_hour=100,
        requests_per_day=500,
        burst_limit=15
    ),
    "standard": RateLimitConfig(
        requests_per_minute=60,
        requests_per_hour=1000,
        requests_per_day=10000,
        burst_limit=100
    ),
    "premium": RateLimitConfig(
        requests_per_minute=300,
        requests_per_hour=5000,
        requests_per_day=50000,
        burst_limit=500
    ),
    "enterprise": RateLimitConfig(
        requests_per_minute=1000,
        requests_per_hour=20000,
        requests_per_day=200000,
        burst_limit=2000
    )
}


class UnifiedAPIGateway:
    """
    Unified API Gateway for NarraForge

    Features:
    - Centralized routing and endpoint management
    - Rate limiting with multiple strategies
    - Authentication and authorization
    - Circuit breaker pattern
    - Request/response caching
    - Request logging and analytics
    - API versioning
    - Load balancing
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Endpoint registry
        self.endpoints: Dict[str, APIEndpoint] = {}

        # Client registry
        self.clients: Dict[str, APIClient] = {}

        # Rate limit states
        self.rate_limit_states: Dict[str, RateLimitState] = {}

        # Circuit breakers per service
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}

        # Response cache
        self.response_cache: Dict[str, Dict[str, Any]] = {}

        # Request logs
        self.request_logs: List[RequestLog] = []

        # Request queue for priority handling
        self.request_queue: Dict[RequestPriority, List[APIRequest]] = {
            priority: [] for priority in RequestPriority
        }

        # Service health status
        self.service_health: Dict[str, Dict[str, Any]] = {}

        # Metrics
        self.metrics: Dict[str, Any] = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "cached_responses": 0,
            "rate_limited": 0,
            "circuit_broken": 0
        }

        self._register_default_endpoints()
        self._initialized = True

    def _register_default_endpoints(self):
        """Register default NarraForge endpoints"""
        default_endpoints = [
            # Phase 1 - Foundation
            ("mirix", "/mirix", ["GET", "POST"]),
            ("emotional", "/emotional", ["GET", "POST"]),
            ("dialogue", "/dialogue", ["GET", "POST"]),
            ("consciousness", "/consciousness", ["GET", "POST"]),
            ("style", "/style", ["GET", "POST"]),
            ("pacing", "/pacing", ["GET", "POST"]),
            # Phase 2 - Multimodal
            ("illustrations", "/illustrations", ["GET", "POST"]),
            ("audiobook", "/audiobook", ["GET", "POST"]),
            ("covers", "/covers", ["GET", "POST"]),
            ("trailer", "/trailer", ["GET", "POST"]),
            ("interactive", "/interactive", ["GET", "POST"]),
            ("soundtrack", "/soundtrack", ["GET", "POST"]),
            # Phase 3 - Intelligence
            ("coherence", "/coherence", ["GET", "POST"]),
            ("psychology", "/psychology", ["GET", "POST"]),
            ("cultural", "/cultural", ["GET", "POST"]),
            ("complexity", "/complexity", ["GET", "POST"]),
            ("trends", "/trends", ["GET", "POST"]),
            # Phase 4 - Expansion
            ("multilanguage", "/multilanguage", ["GET", "POST"]),
            ("collaborative", "/collaborative", ["GET", "POST"]),
            ("coach", "/coach", ["GET", "POST"]),
            ("platforms", "/platforms", ["GET", "POST"]),
            ("analytics", "/analytics", ["GET", "POST"]),
        ]

        for service, path, methods in default_endpoints:
            for method in methods:
                endpoint_id = f"{service}_{method.lower()}"
                self.endpoints[endpoint_id] = APIEndpoint(
                    endpoint_id=endpoint_id,
                    path=f"/api/v1{path}",
                    method=method,
                    service=service,
                    tags=[service]
                )

    def register_endpoint(
        self,
        path: str,
        method: str,
        service: str,
        auth_required: bool = True,
        auth_type: AuthType = AuthType.JWT,
        rate_limit: Optional[RateLimitConfig] = None,
        cache_policy: CachePolicy = CachePolicy.NO_CACHE,
        timeout_seconds: int = 30,
        description: str = ""
    ) -> APIEndpoint:
        """Register a new API endpoint"""
        endpoint_id = str(uuid.uuid4())[:8]

        endpoint = APIEndpoint(
            endpoint_id=endpoint_id,
            path=path,
            method=method.upper(),
            service=service,
            auth_required=auth_required,
            auth_type=auth_type,
            rate_limit=rate_limit,
            cache_policy=cache_policy,
            timeout_seconds=timeout_seconds,
            description=description
        )

        self.endpoints[endpoint_id] = endpoint
        return endpoint

    def register_client(
        self,
        name: str,
        tier: str = "standard",
        rate_limit_override: Optional[RateLimitConfig] = None,
        allowed_endpoints: Optional[List[str]] = None,
        ip_whitelist: Optional[List[str]] = None
    ) -> APIClient:
        """Register a new API client"""
        client_id = str(uuid.uuid4())
        api_key = f"nf_{uuid.uuid4().hex}"
        secret = str(uuid.uuid4())
        secret_hash = hashlib.sha256(secret.encode()).hexdigest()

        client = APIClient(
            client_id=client_id,
            name=name,
            api_key=api_key,
            secret_hash=secret_hash,
            tier=tier,
            rate_limit_override=rate_limit_override,
            allowed_endpoints=allowed_endpoints or [],
            ip_whitelist=ip_whitelist or []
        )

        self.clients[client_id] = client

        # Initialize rate limit state
        self.rate_limit_states[client_id] = RateLimitState(client_id=client_id)

        return client

    def get_client(self, client_id: str) -> Optional[APIClient]:
        """Get client by ID"""
        return self.clients.get(client_id)

    def get_client_by_api_key(self, api_key: str) -> Optional[APIClient]:
        """Get client by API key"""
        for client in self.clients.values():
            if client.api_key == api_key:
                return client
        return None

    def check_rate_limit(self, client_id: str) -> Dict[str, Any]:
        """Check if client is within rate limits"""
        client = self.clients.get(client_id)
        if not client:
            return {"allowed": False, "reason": "Unknown client"}

        state = self.rate_limit_states.get(client_id)
        if not state:
            state = RateLimitState(client_id=client_id)
            self.rate_limit_states[client_id] = state

        # Get applicable rate limit
        rate_limit = client.rate_limit_override or TIER_RATE_LIMITS.get(
            client.tier,
            TIER_RATE_LIMITS["standard"]
        )

        now = datetime.now()

        # Reset counters if needed
        if now >= state.minute_reset:
            state.minute_count = 0
            state.minute_reset = now + timedelta(minutes=1)

        if now >= state.hour_reset:
            state.hour_count = 0
            state.hour_reset = now + timedelta(hours=1)

        if now >= state.day_reset:
            state.day_count = 0
            state.day_reset = now + timedelta(days=1)

        # Check limits
        if state.minute_count >= rate_limit.requests_per_minute:
            self.metrics["rate_limited"] += 1
            return {
                "allowed": False,
                "reason": "Minute limit exceeded",
                "retry_after": (state.minute_reset - now).seconds
            }

        if state.hour_count >= rate_limit.requests_per_hour:
            self.metrics["rate_limited"] += 1
            return {
                "allowed": False,
                "reason": "Hour limit exceeded",
                "retry_after": (state.hour_reset - now).seconds
            }

        if state.day_count >= rate_limit.requests_per_day:
            self.metrics["rate_limited"] += 1
            return {
                "allowed": False,
                "reason": "Day limit exceeded",
                "retry_after": (state.day_reset - now).seconds
            }

        # Increment counters
        state.minute_count += 1
        state.hour_count += 1
        state.day_count += 1
        state.last_request = now

        return {
            "allowed": True,
            "remaining_minute": rate_limit.requests_per_minute - state.minute_count,
            "remaining_hour": rate_limit.requests_per_hour - state.hour_count,
            "remaining_day": rate_limit.requests_per_day - state.day_count
        }

    def check_circuit_breaker(self, service_name: str) -> Dict[str, Any]:
        """Check circuit breaker state for a service"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker(
                service_name=service_name
            )

        breaker = self.circuit_breakers[service_name]
        now = datetime.now()

        if breaker.state == CircuitState.OPEN:
            # Check if timeout has passed
            if breaker.opened_at and (now - breaker.opened_at).seconds >= breaker.timeout_seconds:
                breaker.state = CircuitState.HALF_OPEN
                breaker.half_open_at = now
                breaker.success_count = 0
                return {"allowed": True, "state": "half_open"}
            else:
                self.metrics["circuit_broken"] += 1
                return {
                    "allowed": False,
                    "state": "open",
                    "retry_after": breaker.timeout_seconds - (now - breaker.opened_at).seconds
                }

        return {"allowed": True, "state": breaker.state.value}

    def record_success(self, service_name: str):
        """Record successful request for circuit breaker"""
        if service_name not in self.circuit_breakers:
            return

        breaker = self.circuit_breakers[service_name]

        if breaker.state == CircuitState.HALF_OPEN:
            breaker.success_count += 1
            if breaker.success_count >= breaker.success_threshold:
                breaker.state = CircuitState.CLOSED
                breaker.failure_count = 0
        elif breaker.state == CircuitState.CLOSED:
            breaker.failure_count = 0

    def record_failure(self, service_name: str):
        """Record failed request for circuit breaker"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker(
                service_name=service_name
            )

        breaker = self.circuit_breakers[service_name]
        breaker.failure_count += 1
        breaker.last_failure = datetime.now()

        if breaker.state == CircuitState.HALF_OPEN:
            breaker.state = CircuitState.OPEN
            breaker.opened_at = datetime.now()
        elif breaker.state == CircuitState.CLOSED:
            if breaker.failure_count >= breaker.failure_threshold:
                breaker.state = CircuitState.OPEN
                breaker.opened_at = datetime.now()

    def get_cached_response(
        self,
        endpoint_path: str,
        method: str,
        cache_key: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached response if available"""
        full_key = f"{method}:{endpoint_path}:{cache_key}"

        if full_key in self.response_cache:
            cached = self.response_cache[full_key]
            if datetime.now() < cached["expires_at"]:
                self.metrics["cached_responses"] += 1
                return cached["response"]
            else:
                del self.response_cache[full_key]

        return None

    def cache_response(
        self,
        endpoint_path: str,
        method: str,
        cache_key: str,
        response: Dict[str, Any],
        cache_policy: CachePolicy
    ):
        """Cache a response"""
        if cache_policy == CachePolicy.NO_CACHE:
            return

        ttl_map = {
            CachePolicy.SHORT: 60,
            CachePolicy.MEDIUM: 300,
            CachePolicy.LONG: 1800,
            CachePolicy.EXTENDED: 7200
        }

        ttl = ttl_map.get(cache_policy, 0)
        if ttl == 0:
            return

        full_key = f"{method}:{endpoint_path}:{cache_key}"
        self.response_cache[full_key] = {
            "response": response,
            "expires_at": datetime.now() + timedelta(seconds=ttl),
            "cached_at": datetime.now()
        }

    def process_request(
        self,
        client_id: str,
        endpoint_path: str,
        method: str,
        headers: Dict[str, str],
        query_params: Dict[str, Any],
        body: Optional[Dict[str, Any]],
        ip_address: str
    ) -> APIResponse:
        """Process an incoming API request"""
        request_id = str(uuid.uuid4())
        trace_id = headers.get("X-Trace-ID", str(uuid.uuid4()))
        start_time = time.time()

        self.metrics["total_requests"] += 1

        # Create request object
        request = APIRequest(
            request_id=request_id,
            client_id=client_id,
            endpoint_path=endpoint_path,
            method=method,
            headers=headers,
            query_params=query_params,
            body=body,
            ip_address=ip_address,
            trace_id=trace_id
        )

        # Find endpoint
        endpoint = self._find_endpoint(endpoint_path, method)
        if not endpoint:
            return self._error_response(
                request_id, 404, "Endpoint not found", trace_id, start_time
            )

        # Check rate limit
        rate_check = self.check_rate_limit(client_id)
        if not rate_check["allowed"]:
            return self._error_response(
                request_id, 429, rate_check["reason"], trace_id, start_time,
                headers={"Retry-After": str(rate_check.get("retry_after", 60))}
            )

        # Check circuit breaker
        circuit_check = self.check_circuit_breaker(endpoint.service)
        if not circuit_check["allowed"]:
            return self._error_response(
                request_id, 503, "Service temporarily unavailable",
                trace_id, start_time
            )

        # Check cache
        if method == "GET":
            cache_key = hashlib.md5(
                f"{query_params}".encode()
            ).hexdigest()
            cached = self.get_cached_response(endpoint_path, method, cache_key)
            if cached:
                processing_time = (time.time() - start_time) * 1000
                return APIResponse(
                    request_id=request_id,
                    status_code=200,
                    headers={"X-Cache": "HIT"},
                    body=cached,
                    processing_time_ms=processing_time,
                    cached=True,
                    trace_id=trace_id
                )

        # Process request (simulated - actual routing handled by FastAPI)
        try:
            # In real implementation, this would route to the actual service
            response_body = {
                "success": True,
                "endpoint": endpoint_path,
                "service": endpoint.service,
                "request_id": request_id
            }

            processing_time = (time.time() - start_time) * 1000

            # Record success
            self.record_success(endpoint.service)
            self.metrics["successful_requests"] += 1

            # Cache if applicable
            if method == "GET" and endpoint.cache_policy != CachePolicy.NO_CACHE:
                self.cache_response(
                    endpoint_path, method, cache_key,
                    response_body, endpoint.cache_policy
                )

            # Log request
            self._log_request(request, 200, processing_time)

            return APIResponse(
                request_id=request_id,
                status_code=200,
                headers={
                    "X-Request-ID": request_id,
                    "X-Trace-ID": trace_id
                },
                body=response_body,
                processing_time_ms=processing_time,
                trace_id=trace_id
            )

        except Exception as e:
            self.record_failure(endpoint.service)
            self.metrics["failed_requests"] += 1
            return self._error_response(
                request_id, 500, str(e), trace_id, start_time
            )

    def _find_endpoint(
        self,
        path: str,
        method: str
    ) -> Optional[APIEndpoint]:
        """Find matching endpoint"""
        for endpoint in self.endpoints.values():
            if endpoint.path == path and endpoint.method == method:
                return endpoint
        return None

    def _error_response(
        self,
        request_id: str,
        status_code: int,
        message: str,
        trace_id: str,
        start_time: float,
        headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """Create error response"""
        processing_time = (time.time() - start_time) * 1000

        response_headers = {
            "X-Request-ID": request_id,
            "X-Trace-ID": trace_id
        }
        if headers:
            response_headers.update(headers)

        return APIResponse(
            request_id=request_id,
            status_code=status_code,
            headers=response_headers,
            body={"success": False, "error": message},
            processing_time_ms=processing_time,
            trace_id=trace_id
        )

    def _log_request(
        self,
        request: APIRequest,
        status_code: int,
        processing_time: float,
        error_message: Optional[str] = None
    ):
        """Log request"""
        log = RequestLog(
            log_id=str(uuid.uuid4()),
            request_id=request.request_id,
            client_id=request.client_id,
            endpoint=request.endpoint_path,
            method=request.method,
            status_code=status_code,
            processing_time_ms=processing_time,
            timestamp=request.timestamp,
            ip_address=request.ip_address,
            user_agent=request.headers.get("User-Agent"),
            error_message=error_message
        )

        self.request_logs.append(log)

        # Keep only last 10000 logs
        if len(self.request_logs) > 10000:
            self.request_logs = self.request_logs[-10000:]

    def get_endpoints(
        self,
        service: Optional[str] = None,
        include_deprecated: bool = False
    ) -> List[APIEndpoint]:
        """Get all registered endpoints"""
        endpoints = list(self.endpoints.values())

        if service:
            endpoints = [e for e in endpoints if e.service == service]

        if not include_deprecated:
            endpoints = [e for e in endpoints if not e.deprecated]

        return endpoints

    def get_metrics(self) -> Dict[str, Any]:
        """Get gateway metrics"""
        return {
            **self.metrics,
            "endpoints_count": len(self.endpoints),
            "clients_count": len(self.clients),
            "cache_size": len(self.response_cache),
            "circuit_breakers": {
                name: breaker.to_dict()
                for name, breaker in self.circuit_breakers.items()
            }
        }

    def get_request_logs(
        self,
        client_id: Optional[str] = None,
        endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
        limit: int = 100
    ) -> List[RequestLog]:
        """Get request logs with filters"""
        logs = self.request_logs

        if client_id:
            logs = [l for l in logs if l.client_id == client_id]

        if endpoint:
            logs = [l for l in logs if l.endpoint == endpoint]

        if status_code:
            logs = [l for l in logs if l.status_code == status_code]

        return logs[-limit:]

    def get_client_usage(self, client_id: str) -> Dict[str, Any]:
        """Get usage statistics for a client"""
        client = self.clients.get(client_id)
        if not client:
            return {}

        state = self.rate_limit_states.get(client_id)
        logs = [l for l in self.request_logs if l.client_id == client_id]

        return {
            "client": client.to_dict(),
            "rate_limit_state": state.to_dict() if state else None,
            "total_requests": len(logs),
            "successful_requests": len([l for l in logs if l.status_code < 400]),
            "failed_requests": len([l for l in logs if l.status_code >= 400]),
            "avg_response_time": sum(l.processing_time_ms for l in logs) / len(logs) if logs else 0
        }

    def deprecate_endpoint(
        self,
        endpoint_id: str,
        deprecation_date: datetime,
        replacement: Optional[str] = None
    ):
        """Mark an endpoint as deprecated"""
        if endpoint_id in self.endpoints:
            self.endpoints[endpoint_id].deprecated = True
            self.endpoints[endpoint_id].deprecation_date = deprecation_date
            self.endpoints[endpoint_id].replacement_endpoint = replacement

    def clear_cache(self, pattern: Optional[str] = None):
        """Clear response cache"""
        if pattern:
            keys_to_delete = [
                k for k in self.response_cache.keys()
                if pattern in k
            ]
            for key in keys_to_delete:
                del self.response_cache[key]
        else:
            self.response_cache.clear()


# Singleton instance
api_gateway = UnifiedAPIGateway()
