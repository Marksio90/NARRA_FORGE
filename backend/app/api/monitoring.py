"""
Monitoring & Health API - NarraForge 3.0 Phase 5
Endpoints for system monitoring, health checks, and observability
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.services.monitoring import (
    monitoring_service,
    HealthStatus,
    MetricType,
    AlertSeverity,
    AlertStatus,
    NARRAFORGE_SERVICES
)

router = APIRouter(prefix="/monitoring")


# Request/Response Models
class HealthCheckRequest(BaseModel):
    """Request to register health check"""
    name: str
    service: str
    interval_seconds: int = 30
    timeout_seconds: int = 10
    is_critical: bool = False


class HealthCheckResponse(BaseModel):
    """Health check response"""
    success: bool
    check: Optional[Dict[str, Any]] = None
    message: str = ""


class MetricRecordRequest(BaseModel):
    """Request to record metric"""
    name: str
    value: float
    metric_type: str = "gauge"
    labels: Optional[Dict[str, str]] = None
    unit: str = ""


class AlertRuleRequest(BaseModel):
    """Request to create alert rule"""
    name: str
    condition: str
    severity: str = "warning"
    for_duration_seconds: int = 0
    labels: Optional[Dict[str, str]] = None
    annotations: Optional[Dict[str, str]] = None
    notification_channels: Optional[List[str]] = None


class AlertResponse(BaseModel):
    """Alert response"""
    success: bool
    alert: Optional[Dict[str, Any]] = None
    message: str = ""


class TraceStartRequest(BaseModel):
    """Request to start trace"""
    operation_name: str
    service_name: str
    parent_span_id: Optional[str] = None
    trace_id: Optional[str] = None


# Endpoints

@router.get("/health")
async def get_overall_health():
    """
    Get overall system health

    Returns aggregated health status of all services
    and critical components.
    """
    try:
        health = monitoring_service.get_overall_health()
        return {
            "success": True,
            **health
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/detailed")
async def get_detailed_health():
    """Get detailed health status for all checks"""
    try:
        results = {}
        for check_id, check in monitoring_service.health_checks.items():
            results[check_id] = check.to_dict()

        return {
            "success": True,
            "overall": monitoring_service.get_overall_health(),
            "checks": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/health/checks/register", response_model=HealthCheckResponse)
async def register_health_check(request: HealthCheckRequest):
    """Register a new health check"""
    try:
        check = monitoring_service.register_health_check(
            name=request.name,
            service=request.service,
            interval_seconds=request.interval_seconds,
            timeout_seconds=request.timeout_seconds,
            is_critical=request.is_critical
        )

        return HealthCheckResponse(
            success=True,
            check=check.to_dict(),
            message="Health check registered"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/health/checks/{check_id}/run")
async def run_health_check(check_id: str):
    """Run a specific health check"""
    try:
        result = await monitoring_service.run_health_check(check_id)
        return {
            "success": True,
            "result": result.to_dict()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/health/checks/run-all")
async def run_all_health_checks(background_tasks: BackgroundTasks):
    """Run all health checks"""
    try:
        results = await monitoring_service.run_all_health_checks()
        return {
            "success": True,
            "results": {k: v.to_dict() for k, v in results.items()},
            "count": len(results)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/history")
async def get_health_history(
    check_id: Optional[str] = None,
    limit: int = 100
):
    """Get health check history"""
    try:
        history = monitoring_service.health_history

        if check_id:
            history = [h for h in history if h.check_id == check_id]

        return {
            "success": True,
            "history": [h.to_dict() for h in history[-limit:]],
            "count": len(history[-limit:])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/metrics/record")
async def record_metric(request: MetricRecordRequest):
    """Record a metric value"""
    try:
        metric_type = MetricType(request.metric_type)

        monitoring_service.record_metric(
            name=request.name,
            value=request.value,
            metric_type=metric_type,
            labels=request.labels,
            unit=request.unit
        )

        return {
            "success": True,
            "message": f"Metric recorded: {request.name}"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/metrics/counter/{name}/increment")
async def increment_counter(
    name: str,
    value: float = 1,
    labels: Optional[Dict[str, str]] = None
):
    """Increment a counter metric"""
    try:
        monitoring_service.increment_counter(name, value, labels)
        return {
            "success": True,
            "message": f"Counter incremented: {name}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_all_metrics():
    """Get all current metrics"""
    try:
        metrics = monitoring_service.get_all_metrics()
        return {
            "success": True,
            "metrics": metrics,
            "count": len(metrics)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/{name}")
async def get_metric(
    name: str,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
):
    """Get specific metric with time range"""
    try:
        start = datetime.fromisoformat(start_time) if start_time else None
        end = datetime.fromisoformat(end_time) if end_time else None

        series = monitoring_service.get_metric(name, start, end)
        if not series:
            raise HTTPException(status_code=404, detail="Metric not found")

        return {
            "success": True,
            "metric": series.to_dict(),
            "data_points": [m.to_dict() for m in series.data_points]
        }

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/prometheus", response_class=PlainTextResponse)
async def export_prometheus():
    """Export metrics in Prometheus format"""
    try:
        return monitoring_service.export_metrics_prometheus()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/rules/create")
async def create_alert_rule(request: AlertRuleRequest):
    """Create an alert rule"""
    try:
        severity = AlertSeverity(request.severity)

        rule = monitoring_service.register_alert_rule(
            name=request.name,
            condition=request.condition,
            severity=severity,
            for_duration_seconds=request.for_duration_seconds,
            labels=request.labels,
            annotations=request.annotations,
            notification_channels=request.notification_channels
        )

        return {
            "success": True,
            "rule": rule.to_dict(),
            "message": "Alert rule created"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts/rules")
async def get_alert_rules():
    """Get all alert rules"""
    try:
        rules = list(monitoring_service.alert_rules.values())
        return {
            "success": True,
            "rules": [r.to_dict() for r in rules],
            "count": len(rules)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/trigger", response_model=AlertResponse)
async def trigger_alert(
    name: str,
    severity: str,
    source: str,
    message: str,
    labels: Optional[Dict[str, str]] = None
):
    """Manually trigger an alert"""
    try:
        sev = AlertSeverity(severity)

        alert = monitoring_service.trigger_alert(
            name=name,
            severity=sev,
            source=source,
            message=message,
            labels=labels
        )

        return AlertResponse(
            success=True,
            alert=alert.to_dict(),
            message="Alert triggered"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts/active")
async def get_active_alerts(severity: Optional[str] = None):
    """Get active alerts"""
    try:
        sev = AlertSeverity(severity) if severity else None
        alerts = monitoring_service.get_active_alerts(sev)

        return {
            "success": True,
            "alerts": [a.to_dict() for a in alerts],
            "count": len(alerts)
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, acknowledged_by: str):
    """Acknowledge an alert"""
    try:
        alert = monitoring_service.acknowledge_alert(alert_id, acknowledged_by)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found or not active")

        return {
            "success": True,
            "alert": alert.to_dict(),
            "message": "Alert acknowledged"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str, resolution_note: str = ""):
    """Resolve an alert"""
    try:
        alert = monitoring_service.resolve_alert(alert_id, resolution_note)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found or already resolved")

        return {
            "success": True,
            "alert": alert.to_dict(),
            "message": "Alert resolved"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/traces/start")
async def start_trace(request: TraceStartRequest):
    """Start a new trace span"""
    try:
        span = monitoring_service.start_trace(
            operation_name=request.operation_name,
            service_name=request.service_name,
            parent_span_id=request.parent_span_id,
            trace_id=request.trace_id
        )

        return {
            "success": True,
            "span": span.to_dict()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/traces/{trace_id}")
async def get_trace(trace_id: str):
    """Get trace by ID"""
    try:
        spans = monitoring_service.get_trace(trace_id)
        if not spans:
            raise HTTPException(status_code=404, detail="Trace not found")

        return {
            "success": True,
            "trace_id": trace_id,
            "spans": [s.to_dict() for s in spans],
            "count": len(spans)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system")
async def get_system_metrics():
    """Get system resource metrics"""
    try:
        metrics = monitoring_service.collect_system_metrics()
        return {
            "success": True,
            "system": metrics
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services")
async def get_services():
    """Get all registered services"""
    try:
        services = monitoring_service.get_all_services()
        return {
            "success": True,
            "services": [s.to_dict() for s in services],
            "count": len(services)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services/{service_name}")
async def get_service(service_name: str):
    """Get specific service info"""
    try:
        service = monitoring_service.get_service_info(service_name)
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")

        return {
            "success": True,
            "service": service.to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard")
async def get_dashboard():
    """Get comprehensive dashboard data"""
    try:
        dashboard = monitoring_service.get_dashboard_data()
        return {
            "success": True,
            **dashboard
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services/list")
async def list_narraforge_services():
    """List all NarraForge services"""
    return {
        "success": True,
        "services": NARRAFORGE_SERVICES,
        "count": len(NARRAFORGE_SERVICES)
    }
