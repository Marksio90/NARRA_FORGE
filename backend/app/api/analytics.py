"""
Analytics Dashboard API - NarraForge 3.0 Phase 4
Endpoints for comprehensive analytics, reporting, and insights
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.services.analytics import (
    analytics_dashboard,
    MetricType,
    TimeRange,
    ChartType,
    TrendDirection,
    AlertLevel
)

router = APIRouter(prefix="/analytics")


# Request/Response Models
class DashboardRequest(BaseModel):
    """Request to create or configure dashboard"""
    name: str
    widgets: List[Dict[str, Any]] = []
    refresh_interval_minutes: int = 15
    is_default: bool = False


class DashboardResponse(BaseModel):
    """Dashboard response"""
    success: bool
    dashboard: Optional[Dict[str, Any]] = None
    message: str = ""


class WidgetRequest(BaseModel):
    """Request to add/update widget"""
    widget_type: str
    title: str
    metric_type: str
    chart_type: str = "line"
    time_range: str = "month"
    filters: Optional[Dict[str, Any]] = None
    position: Optional[Dict[str, int]] = None
    size: Optional[Dict[str, int]] = None


class ReportRequest(BaseModel):
    """Request to generate report"""
    report_type: str
    time_range: str = "month"
    include_sections: List[str] = []
    format: str = "pdf"
    custom_date_start: Optional[str] = None
    custom_date_end: Optional[str] = None


class ReportResponse(BaseModel):
    """Report response"""
    success: bool
    report: Optional[Dict[str, Any]] = None
    download_url: Optional[str] = None
    message: str = ""


class AlertConfigRequest(BaseModel):
    """Request to configure alerts"""
    metric_type: str
    condition: str  # above, below, change
    threshold: float
    alert_level: str = "warning"
    notification_channels: List[str] = ["email"]
    is_active: bool = True


# Endpoints

@router.get("/overview/{user_id}")
async def get_analytics_overview(user_id: str, time_range: str = "month"):
    """
    Get analytics overview

    Provides high-level metrics including:
    - Total books and words written
    - Sales and revenue
    - Reader engagement
    - Quality scores
    """
    try:
        range_enum = TimeRange(time_range)
        overview = analytics_dashboard.get_overview(user_id, range_enum)

        return {
            "success": True,
            "overview": overview
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/writing/{user_id}")
async def get_writing_stats(user_id: str, time_range: str = "month"):
    """Get detailed writing statistics"""
    try:
        range_enum = TimeRange(time_range)
        stats = analytics_dashboard.get_writing_stats(user_id, range_enum)

        return {
            "success": True,
            "stats": stats.to_dict() if hasattr(stats, 'to_dict') else stats
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sales/{user_id}")
async def get_sales_stats(user_id: str, time_range: str = "month"):
    """Get detailed sales statistics"""
    try:
        range_enum = TimeRange(time_range)
        stats = analytics_dashboard.get_sales_stats(user_id, range_enum)

        return {
            "success": True,
            "stats": stats.to_dict() if hasattr(stats, 'to_dict') else stats
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/engagement/{user_id}")
async def get_engagement_stats(user_id: str, time_range: str = "month"):
    """Get reader engagement statistics"""
    try:
        range_enum = TimeRange(time_range)
        stats = analytics_dashboard.get_engagement_stats(user_id, range_enum)

        return {
            "success": True,
            "stats": stats.to_dict() if hasattr(stats, 'to_dict') else stats
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quality/{user_id}")
async def get_quality_metrics(user_id: str, project_id: Optional[str] = None):
    """Get quality metrics for books"""
    try:
        metrics = analytics_dashboard.get_quality_metrics(
            user_id=user_id,
            project_id=project_id
        )

        return {
            "success": True,
            "metrics": metrics.to_dict() if hasattr(metrics, 'to_dict') else metrics
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends/{user_id}")
async def get_trends(
    user_id: str,
    metric_type: str,
    time_range: str = "month"
):
    """Get trend data for a specific metric"""
    try:
        metric = MetricType(metric_type)
        range_enum = TimeRange(time_range)

        trends = analytics_dashboard.get_trends(
            user_id=user_id,
            metric_type=metric,
            time_range=range_enum
        )

        return {
            "success": True,
            "trends": trends
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timeseries/{user_id}")
async def get_timeseries_data(
    user_id: str,
    metric_type: str,
    time_range: str = "month",
    granularity: str = "day"
):
    """Get time series data for charts"""
    try:
        metric = MetricType(metric_type)
        range_enum = TimeRange(time_range)

        data = analytics_dashboard.get_timeseries(
            user_id=user_id,
            metric_type=metric,
            time_range=range_enum,
            granularity=granularity
        )

        return {
            "success": True,
            "data": data.to_dict() if hasattr(data, 'to_dict') else data
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dashboards/create", response_model=DashboardResponse)
async def create_dashboard(user_id: str, request: DashboardRequest):
    """Create a custom dashboard"""
    try:
        dashboard = analytics_dashboard.create_dashboard(
            user_id=user_id,
            name=request.name,
            widgets=request.widgets,
            refresh_interval_minutes=request.refresh_interval_minutes,
            is_default=request.is_default
        )

        return DashboardResponse(
            success=True,
            dashboard=dashboard.to_dict(),
            message="Dashboard created"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboards/{user_id}")
async def get_user_dashboards(user_id: str):
    """Get all dashboards for a user"""
    try:
        dashboards = analytics_dashboard.get_dashboards(user_id)

        return {
            "success": True,
            "dashboards": [d.to_dict() for d in dashboards],
            "count": len(dashboards)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboards/{user_id}/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(user_id: str, dashboard_id: str):
    """Get a specific dashboard with populated data"""
    try:
        dashboard = analytics_dashboard.get_dashboard(user_id, dashboard_id)

        if not dashboard:
            raise HTTPException(status_code=404, detail="Dashboard not found")

        return DashboardResponse(
            success=True,
            dashboard=dashboard.to_dict(),
            message="Dashboard retrieved"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/dashboards/{dashboard_id}")
async def update_dashboard(dashboard_id: str, request: DashboardRequest):
    """Update a dashboard"""
    try:
        dashboard = analytics_dashboard.update_dashboard(
            dashboard_id=dashboard_id,
            name=request.name,
            widgets=request.widgets,
            refresh_interval_minutes=request.refresh_interval_minutes,
            is_default=request.is_default
        )

        return {
            "success": True,
            "dashboard": dashboard.to_dict(),
            "message": "Dashboard updated"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/dashboards/{dashboard_id}")
async def delete_dashboard(dashboard_id: str):
    """Delete a dashboard"""
    try:
        analytics_dashboard.delete_dashboard(dashboard_id)

        return {
            "success": True,
            "message": "Dashboard deleted"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dashboards/{dashboard_id}/widgets")
async def add_widget(dashboard_id: str, request: WidgetRequest):
    """Add a widget to a dashboard"""
    try:
        metric = MetricType(request.metric_type)
        chart = ChartType(request.chart_type)
        time_range = TimeRange(request.time_range)

        widget = analytics_dashboard.add_widget(
            dashboard_id=dashboard_id,
            widget_type=request.widget_type,
            title=request.title,
            metric_type=metric,
            chart_type=chart,
            time_range=time_range,
            filters=request.filters,
            position=request.position,
            size=request.size
        )

        return {
            "success": True,
            "widget": widget.to_dict(),
            "message": "Widget added"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/dashboards/{dashboard_id}/widgets/{widget_id}")
async def remove_widget(dashboard_id: str, widget_id: str):
    """Remove a widget from a dashboard"""
    try:
        analytics_dashboard.remove_widget(dashboard_id, widget_id)

        return {
            "success": True,
            "message": "Widget removed"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reports/generate", response_model=ReportResponse)
async def generate_report(user_id: str, request: ReportRequest):
    """
    Generate an analytics report

    Types: summary, sales, writing, engagement, quality, comprehensive
    Formats: pdf, xlsx, html
    """
    try:
        range_enum = TimeRange(request.time_range)

        report = analytics_dashboard.generate_report(
            user_id=user_id,
            report_type=request.report_type,
            time_range=range_enum,
            include_sections=request.include_sections,
            format=request.format,
            custom_date_start=request.custom_date_start,
            custom_date_end=request.custom_date_end
        )

        return ReportResponse(
            success=True,
            report=report.to_dict() if hasattr(report, 'to_dict') else report,
            download_url=report.get("download_url") if isinstance(report, dict) else None,
            message=f"Report generated in {request.format} format"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/{user_id}")
async def get_user_reports(user_id: str, limit: int = 20):
    """Get previously generated reports"""
    try:
        reports = analytics_dashboard.get_reports(user_id, limit)

        return {
            "success": True,
            "reports": [r.to_dict() for r in reports],
            "count": len(reports)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/{user_id}/{report_id}")
async def get_report(user_id: str, report_id: str):
    """Get a specific report"""
    try:
        report = analytics_dashboard.get_report(user_id, report_id)

        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        return {
            "success": True,
            "report": report.to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/configure")
async def configure_alert(user_id: str, request: AlertConfigRequest):
    """Configure an alert for a metric"""
    try:
        metric = MetricType(request.metric_type)
        level = AlertLevel(request.alert_level)

        alert = analytics_dashboard.configure_alert(
            user_id=user_id,
            metric_type=metric,
            condition=request.condition,
            threshold=request.threshold,
            alert_level=level,
            notification_channels=request.notification_channels,
            is_active=request.is_active
        )

        return {
            "success": True,
            "alert": alert,
            "message": "Alert configured"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts/{user_id}")
async def get_alerts(user_id: str, active_only: bool = True):
    """Get configured alerts"""
    try:
        alerts = analytics_dashboard.get_alerts(user_id, active_only)

        return {
            "success": True,
            "alerts": [a.to_dict() for a in alerts],
            "count": len(alerts)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts/{user_id}/triggered")
async def get_triggered_alerts(user_id: str, acknowledged: bool = False):
    """Get triggered alerts"""
    try:
        alerts = analytics_dashboard.get_triggered_alerts(user_id, acknowledged)

        return {
            "success": True,
            "alerts": alerts,
            "count": len(alerts)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    """Acknowledge a triggered alert"""
    try:
        analytics_dashboard.acknowledge_alert(alert_id)

        return {
            "success": True,
            "message": "Alert acknowledged"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/alerts/{alert_id}")
async def delete_alert(alert_id: str):
    """Delete an alert configuration"""
    try:
        analytics_dashboard.delete_alert(alert_id)

        return {
            "success": True,
            "message": "Alert deleted"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compare/{user_id}")
async def compare_periods(
    user_id: str,
    metric_type: str,
    period1_start: str,
    period1_end: str,
    period2_start: str,
    period2_end: str
):
    """Compare metrics between two time periods"""
    try:
        metric = MetricType(metric_type)

        comparison = analytics_dashboard.compare_periods(
            user_id=user_id,
            metric_type=metric,
            period1_start=period1_start,
            period1_end=period1_end,
            period2_start=period2_start,
            period2_end=period2_end
        )

        return {
            "success": True,
            "comparison": comparison
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/analytics")
async def get_project_analytics(user_id: str, project_id: str):
    """Get comprehensive analytics for a specific project"""
    try:
        analytics = analytics_dashboard.get_project_analytics(
            user_id=user_id,
            project_id=project_id
        )

        return {
            "success": True,
            "analytics": analytics
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/benchmarks/{user_id}")
async def get_benchmarks(user_id: str, genre: Optional[str] = None):
    """Get performance benchmarks compared to similar works"""
    try:
        benchmarks = analytics_dashboard.get_benchmarks(
            user_id=user_id,
            genre=genre
        )

        return {
            "success": True,
            "benchmarks": benchmarks
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights/{user_id}")
async def get_ai_insights(user_id: str):
    """Get AI-generated insights and recommendations"""
    try:
        insights = analytics_dashboard.get_insights(user_id)

        return {
            "success": True,
            "insights": insights
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/{user_id}")
async def export_analytics_data(
    user_id: str,
    metrics: List[str],
    time_range: str = "year",
    format: str = "csv"
):
    """Export raw analytics data"""
    try:
        metric_types = [MetricType(m) for m in metrics]
        range_enum = TimeRange(time_range)

        export = analytics_dashboard.export_data(
            user_id=user_id,
            metrics=metric_types,
            time_range=range_enum,
            format=format
        )

        return {
            "success": True,
            "export": export
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
