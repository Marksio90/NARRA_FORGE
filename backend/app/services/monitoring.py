"""
Monitoring & Health Service - NarraForge 3.0 Phase 5
Comprehensive system monitoring, health checks, and observability
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from datetime import datetime, timedelta
import uuid
import asyncio
import time
import psutil
import logging

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Service health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SILENCED = "silenced"


@dataclass
class HealthCheck:
    """Health check definition"""
    check_id: str
    name: str
    service: str
    check_function: Optional[Callable[[], bool]] = None
    interval_seconds: int = 30
    timeout_seconds: int = 10
    failure_threshold: int = 3
    success_threshold: int = 1
    last_check: Optional[datetime] = None
    last_status: HealthStatus = HealthStatus.UNKNOWN
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    is_critical: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "check_id": self.check_id,
            "name": self.name,
            "service": self.service,
            "interval_seconds": self.interval_seconds,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "last_status": self.last_status.value,
            "consecutive_failures": self.consecutive_failures,
            "is_critical": self.is_critical
        }


@dataclass
class HealthCheckResult:
    """Result of health check execution"""
    check_id: str
    status: HealthStatus
    response_time_ms: float
    timestamp: datetime = field(default_factory=datetime.now)
    message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "check_id": self.check_id,
            "status": self.status.value,
            "response_time_ms": self.response_time_ms,
            "timestamp": self.timestamp.isoformat(),
            "message": self.message,
            "details": self.details
        }


@dataclass
class Metric:
    """Metric data point"""
    metric_id: str
    name: str
    metric_type: MetricType
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    unit: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "name": self.name,
            "type": self.metric_type.value,
            "value": self.value,
            "labels": self.labels,
            "timestamp": self.timestamp.isoformat(),
            "unit": self.unit
        }


@dataclass
class MetricSeries:
    """Time series of metrics"""
    name: str
    metric_type: MetricType
    data_points: List[Metric] = field(default_factory=list)
    labels: Dict[str, str] = field(default_factory=dict)
    retention_hours: int = 24

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.metric_type.value,
            "labels": self.labels,
            "data_points_count": len(self.data_points),
            "retention_hours": self.retention_hours
        }


@dataclass
class Alert:
    """System alert"""
    alert_id: str
    name: str
    severity: AlertSeverity
    status: AlertStatus
    source: str
    message: str
    triggered_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolution_note: Optional[str] = None
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "name": self.name,
            "severity": self.severity.value,
            "status": self.status.value,
            "source": self.source,
            "message": self.message,
            "triggered_at": self.triggered_at.isoformat(),
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "labels": self.labels
        }


@dataclass
class AlertRule:
    """Alert triggering rule"""
    rule_id: str
    name: str
    condition: str  # Expression to evaluate
    severity: AlertSeverity
    for_duration_seconds: int = 0  # Must be true for this long
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    notification_channels: List[str] = field(default_factory=list)
    is_active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "condition": self.condition,
            "severity": self.severity.value,
            "for_duration_seconds": self.for_duration_seconds,
            "labels": self.labels,
            "is_active": self.is_active
        }


@dataclass
class ServiceInfo:
    """Service information"""
    service_id: str
    name: str
    version: str
    status: HealthStatus
    uptime_seconds: float
    started_at: datetime
    host: str = "localhost"
    port: int = 8000
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "service_id": self.service_id,
            "name": self.name,
            "version": self.version,
            "status": self.status.value,
            "uptime_seconds": self.uptime_seconds,
            "started_at": self.started_at.isoformat(),
            "host": self.host,
            "port": self.port,
            "dependencies": self.dependencies
        }


@dataclass
class TraceSpan:
    """Distributed tracing span"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    service_name: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_ms: float = 0.0
    status: str = "ok"
    tags: Dict[str, str] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "operation_name": self.operation_name,
            "service_name": self.service_name,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration_ms": self.duration_ms,
            "status": self.status,
            "tags": self.tags
        }


# NarraForge services for monitoring
NARRAFORGE_SERVICES = [
    # Phase 1 - Foundation
    "mirix", "emotional", "dialogue", "consciousness", "style", "pacing",
    # Phase 2 - Multimodal
    "illustrations", "audiobook", "covers", "trailer", "interactive", "soundtrack",
    # Phase 3 - Intelligence
    "coherence", "psychology", "cultural", "complexity", "trends",
    # Phase 4 - Expansion
    "multilanguage", "collaborative", "coach", "platforms", "analytics",
    # Phase 5 - Integration
    "gateway", "orchestrator", "eventbus", "cache",
    # Infrastructure
    "database", "redis", "celery",
]


class MonitoringService:
    """
    Monitoring & Health Service for NarraForge

    Features:
    - Health checks for all services
    - Metrics collection and aggregation
    - Alert management
    - Distributed tracing
    - System resource monitoring
    - Uptime tracking
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

        # Service start time
        self.started_at = datetime.now()

        # Health checks
        self.health_checks: Dict[str, HealthCheck] = {}

        # Health check history
        self.health_history: List[HealthCheckResult] = []

        # Metrics
        self.metrics: Dict[str, MetricSeries] = {}

        # Alerts
        self.alerts: Dict[str, Alert] = {}

        # Alert rules
        self.alert_rules: Dict[str, AlertRule] = {}

        # Services
        self.services: Dict[str, ServiceInfo] = {}

        # Traces
        self.traces: Dict[str, List[TraceSpan]] = {}

        # System metrics
        self.system_metrics: Dict[str, float] = {}

        # Background tasks
        self._monitoring_task: Optional[asyncio.Task] = None

        self._register_default_checks()
        self._register_default_rules()
        self._register_services()
        self._initialized = True

    def _register_default_checks(self):
        """Register default health checks"""
        for service in NARRAFORGE_SERVICES:
            self.register_health_check(
                name=f"{service}_health",
                service=service,
                interval_seconds=30,
                is_critical=(service in ["database", "redis"])
            )

    def _register_default_rules(self):
        """Register default alert rules"""
        default_rules = [
            ("high_error_rate", "error_rate > 0.1", AlertSeverity.ERROR),
            ("high_latency", "p99_latency_ms > 1000", AlertSeverity.WARNING),
            ("low_disk_space", "disk_usage_percent > 90", AlertSeverity.CRITICAL),
            ("high_memory", "memory_usage_percent > 85", AlertSeverity.WARNING),
            ("service_down", "service_health == 'unhealthy'", AlertSeverity.CRITICAL),
        ]

        for name, condition, severity in default_rules:
            self.register_alert_rule(name, condition, severity)

    def _register_services(self):
        """Register NarraForge services"""
        for service in NARRAFORGE_SERVICES:
            self.services[service] = ServiceInfo(
                service_id=str(uuid.uuid4()),
                name=service,
                version="3.0.0",
                status=HealthStatus.UNKNOWN,
                uptime_seconds=0,
                started_at=self.started_at
            )

    def register_health_check(
        self,
        name: str,
        service: str,
        check_function: Optional[Callable[[], bool]] = None,
        interval_seconds: int = 30,
        timeout_seconds: int = 10,
        is_critical: bool = False
    ) -> HealthCheck:
        """Register a health check"""
        check_id = str(uuid.uuid4())

        check = HealthCheck(
            check_id=check_id,
            name=name,
            service=service,
            check_function=check_function,
            interval_seconds=interval_seconds,
            timeout_seconds=timeout_seconds,
            is_critical=is_critical
        )

        self.health_checks[check_id] = check
        return check

    async def run_health_check(self, check_id: str) -> HealthCheckResult:
        """Run a specific health check"""
        check = self.health_checks.get(check_id)
        if not check:
            return HealthCheckResult(
                check_id=check_id,
                status=HealthStatus.UNKNOWN,
                response_time_ms=0,
                message="Check not found"
            )

        start_time = time.time()

        try:
            # Run check function if provided
            if check.check_function:
                if asyncio.iscoroutinefunction(check.check_function):
                    success = await asyncio.wait_for(
                        check.check_function(),
                        timeout=check.timeout_seconds
                    )
                else:
                    success = check.check_function()
            else:
                # Default: assume healthy
                success = True

            response_time = (time.time() - start_time) * 1000

            if success:
                check.consecutive_successes += 1
                check.consecutive_failures = 0

                if check.consecutive_successes >= check.success_threshold:
                    check.last_status = HealthStatus.HEALTHY
            else:
                check.consecutive_failures += 1
                check.consecutive_successes = 0

                if check.consecutive_failures >= check.failure_threshold:
                    check.last_status = HealthStatus.UNHEALTHY
                else:
                    check.last_status = HealthStatus.DEGRADED

            check.last_check = datetime.now()

            result = HealthCheckResult(
                check_id=check_id,
                status=check.last_status,
                response_time_ms=response_time,
                message="Check passed" if success else "Check failed"
            )

        except asyncio.TimeoutError:
            check.consecutive_failures += 1
            check.last_status = HealthStatus.UNHEALTHY

            result = HealthCheckResult(
                check_id=check_id,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=check.timeout_seconds * 1000,
                message="Check timed out"
            )

        except Exception as e:
            check.consecutive_failures += 1
            check.last_status = HealthStatus.UNHEALTHY

            result = HealthCheckResult(
                check_id=check_id,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=(time.time() - start_time) * 1000,
                message=str(e)
            )

        # Store history
        self.health_history.append(result)
        if len(self.health_history) > 10000:
            self.health_history = self.health_history[-10000:]

        # Update service status
        if check.service in self.services:
            self.services[check.service].status = check.last_status

        return result

    async def run_all_health_checks(self) -> Dict[str, HealthCheckResult]:
        """Run all registered health checks"""
        results = {}
        tasks = []

        for check_id in self.health_checks:
            task = self.run_health_check(check_id)
            tasks.append((check_id, task))

        for check_id, task in tasks:
            result = await task
            results[check_id] = result

        return results

    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        statuses = [check.last_status for check in self.health_checks.values()]
        critical_checks = [
            check for check in self.health_checks.values()
            if check.is_critical
        ]

        # Determine overall status
        if any(check.last_status == HealthStatus.UNHEALTHY for check in critical_checks):
            overall_status = HealthStatus.UNHEALTHY
        elif any(s == HealthStatus.UNHEALTHY for s in statuses):
            overall_status = HealthStatus.DEGRADED
        elif any(s == HealthStatus.DEGRADED for s in statuses):
            overall_status = HealthStatus.DEGRADED
        elif any(s == HealthStatus.UNKNOWN for s in statuses):
            overall_status = HealthStatus.UNKNOWN
        else:
            overall_status = HealthStatus.HEALTHY

        return {
            "status": overall_status.value,
            "uptime_seconds": (datetime.now() - self.started_at).total_seconds(),
            "checks_total": len(self.health_checks),
            "checks_healthy": len([s for s in statuses if s == HealthStatus.HEALTHY]),
            "checks_unhealthy": len([s for s in statuses if s == HealthStatus.UNHEALTHY]),
            "checks_degraded": len([s for s in statuses if s == HealthStatus.DEGRADED]),
            "timestamp": datetime.now().isoformat()
        }

    def record_metric(
        self,
        name: str,
        value: float,
        metric_type: MetricType = MetricType.GAUGE,
        labels: Optional[Dict[str, str]] = None,
        unit: str = ""
    ):
        """Record a metric value"""
        if name not in self.metrics:
            self.metrics[name] = MetricSeries(
                name=name,
                metric_type=metric_type,
                labels=labels or {}
            )

        metric = Metric(
            metric_id=str(uuid.uuid4()),
            name=name,
            metric_type=metric_type,
            value=value,
            labels=labels or {},
            unit=unit
        )

        self.metrics[name].data_points.append(metric)

        # Limit data points
        if len(self.metrics[name].data_points) > 10000:
            self.metrics[name].data_points = self.metrics[name].data_points[-10000:]

    def increment_counter(
        self,
        name: str,
        value: float = 1,
        labels: Optional[Dict[str, str]] = None
    ):
        """Increment a counter metric"""
        if name not in self.metrics:
            self.record_metric(name, value, MetricType.COUNTER, labels)
        else:
            current = self.metrics[name].data_points[-1].value if self.metrics[name].data_points else 0
            self.record_metric(name, current + value, MetricType.COUNTER, labels)

    def get_metric(
        self,
        name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Optional[MetricSeries]:
        """Get metric series"""
        series = self.metrics.get(name)
        if not series:
            return None

        if start_time or end_time:
            filtered_points = []
            for point in series.data_points:
                if start_time and point.timestamp < start_time:
                    continue
                if end_time and point.timestamp > end_time:
                    continue
                filtered_points.append(point)

            series = MetricSeries(
                name=series.name,
                metric_type=series.metric_type,
                data_points=filtered_points,
                labels=series.labels
            )

        return series

    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get all current metrics"""
        result = {}
        for name, series in self.metrics.items():
            if series.data_points:
                latest = series.data_points[-1]
                result[name] = {
                    "value": latest.value,
                    "type": series.metric_type.value,
                    "timestamp": latest.timestamp.isoformat(),
                    "labels": latest.labels
                }
        return result

    def register_alert_rule(
        self,
        name: str,
        condition: str,
        severity: AlertSeverity,
        for_duration_seconds: int = 0,
        labels: Optional[Dict[str, str]] = None,
        annotations: Optional[Dict[str, str]] = None,
        notification_channels: Optional[List[str]] = None
    ) -> AlertRule:
        """Register an alert rule"""
        rule_id = str(uuid.uuid4())

        rule = AlertRule(
            rule_id=rule_id,
            name=name,
            condition=condition,
            severity=severity,
            for_duration_seconds=for_duration_seconds,
            labels=labels or {},
            annotations=annotations or {},
            notification_channels=notification_channels or ["log"]
        )

        self.alert_rules[rule_id] = rule
        return rule

    def trigger_alert(
        self,
        name: str,
        severity: AlertSeverity,
        source: str,
        message: str,
        labels: Optional[Dict[str, str]] = None
    ) -> Alert:
        """Trigger an alert"""
        alert_id = str(uuid.uuid4())

        alert = Alert(
            alert_id=alert_id,
            name=name,
            severity=severity,
            status=AlertStatus.ACTIVE,
            source=source,
            message=message,
            labels=labels or {}
        )

        self.alerts[alert_id] = alert
        logger.warning(f"Alert triggered: {name} ({severity.value}) - {message}")

        return alert

    def acknowledge_alert(
        self,
        alert_id: str,
        acknowledged_by: str
    ) -> Optional[Alert]:
        """Acknowledge an alert"""
        alert = self.alerts.get(alert_id)
        if alert and alert.status == AlertStatus.ACTIVE:
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.now()
            alert.acknowledged_by = acknowledged_by
            return alert
        return None

    def resolve_alert(
        self,
        alert_id: str,
        resolution_note: str = ""
    ) -> Optional[Alert]:
        """Resolve an alert"""
        alert = self.alerts.get(alert_id)
        if alert and alert.status in [AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED]:
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()
            alert.resolution_note = resolution_note
            return alert
        return None

    def get_active_alerts(
        self,
        severity: Optional[AlertSeverity] = None
    ) -> List[Alert]:
        """Get active alerts"""
        alerts = [
            a for a in self.alerts.values()
            if a.status == AlertStatus.ACTIVE
        ]

        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        return sorted(alerts, key=lambda a: a.triggered_at, reverse=True)

    def start_trace(
        self,
        operation_name: str,
        service_name: str,
        parent_span_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> TraceSpan:
        """Start a new trace span"""
        if not trace_id:
            trace_id = str(uuid.uuid4())

        span = TraceSpan(
            trace_id=trace_id,
            span_id=str(uuid.uuid4()),
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            service_name=service_name,
            started_at=datetime.now()
        )

        if trace_id not in self.traces:
            self.traces[trace_id] = []
        self.traces[trace_id].append(span)

        return span

    def end_trace(
        self,
        span: TraceSpan,
        status: str = "ok",
        tags: Optional[Dict[str, str]] = None
    ):
        """End a trace span"""
        span.ended_at = datetime.now()
        span.duration_ms = (span.ended_at - span.started_at).total_seconds() * 1000
        span.status = status
        if tags:
            span.tags.update(tags)

    def get_trace(self, trace_id: str) -> Optional[List[TraceSpan]]:
        """Get trace by ID"""
        return self.traces.get(trace_id)

    def collect_system_metrics(self) -> Dict[str, float]:
        """Collect system resource metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            self.system_metrics = {
                "cpu_usage_percent": cpu_percent,
                "memory_usage_percent": memory.percent,
                "memory_available_mb": memory.available / (1024 * 1024),
                "memory_total_mb": memory.total / (1024 * 1024),
                "disk_usage_percent": disk.percent,
                "disk_free_gb": disk.free / (1024 * 1024 * 1024),
                "disk_total_gb": disk.total / (1024 * 1024 * 1024)
            }

            # Record as metrics
            for name, value in self.system_metrics.items():
                self.record_metric(f"system_{name}", value, MetricType.GAUGE)

        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")

        return self.system_metrics

    def get_service_info(self, service_name: str) -> Optional[ServiceInfo]:
        """Get service information"""
        service = self.services.get(service_name)
        if service:
            service.uptime_seconds = (datetime.now() - service.started_at).total_seconds()
        return service

    def get_all_services(self) -> List[ServiceInfo]:
        """Get all registered services"""
        for service in self.services.values():
            service.uptime_seconds = (datetime.now() - service.started_at).total_seconds()
        return list(self.services.values())

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        return {
            "health": self.get_overall_health(),
            "system": self.collect_system_metrics(),
            "services": [s.to_dict() for s in self.get_all_services()],
            "active_alerts": [a.to_dict() for a in self.get_active_alerts()],
            "metrics_summary": {
                "total_series": len(self.metrics),
                "total_data_points": sum(
                    len(s.data_points) for s in self.metrics.values()
                )
            },
            "uptime_seconds": (datetime.now() - self.started_at).total_seconds(),
            "timestamp": datetime.now().isoformat()
        }

    def export_metrics_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []

        for name, series in self.metrics.items():
            if series.data_points:
                latest = series.data_points[-1]
                labels_str = ",".join(
                    f'{k}="{v}"' for k, v in latest.labels.items()
                )
                if labels_str:
                    lines.append(f"{name}{{{labels_str}}} {latest.value}")
                else:
                    lines.append(f"{name} {latest.value}")

        return "\n".join(lines)


# Singleton instance
monitoring_service = MonitoringService()
