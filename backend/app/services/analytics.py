"""
Analytics Dashboard - NarraForge 3.0 Phase 4

Comprehensive analytics system for tracking writing productivity,
book performance, reader engagement, and business metrics.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from datetime import datetime, timedelta
import uuid


# =============================================================================
# ENUMS
# =============================================================================

class MetricType(Enum):
    """Types of metrics"""
    WRITING = "writing"
    SALES = "sales"
    ENGAGEMENT = "engagement"
    MARKETING = "marketing"
    QUALITY = "quality"
    FINANCIAL = "financial"


class TimeRange(Enum):
    """Time ranges for analytics"""
    TODAY = "today"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
    ALL_TIME = "all_time"
    CUSTOM = "custom"


class ChartType(Enum):
    """Chart types for visualization"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    AREA = "area"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    TABLE = "table"


class TrendDirection(Enum):
    """Trend directions"""
    UP = "up"
    DOWN = "down"
    STABLE = "stable"


class AlertLevel(Enum):
    """Alert levels"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    CRITICAL = "critical"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class Metric:
    """A single metric value"""
    metric_id: str
    name: str
    value: float
    unit: str
    metric_type: MetricType
    timestamp: datetime
    previous_value: Optional[float]
    trend: TrendDirection
    trend_percent: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "metric_type": self.metric_type.value,
            "timestamp": self.timestamp.isoformat(),
            "previous_value": self.previous_value,
            "trend": self.trend.value,
            "trend_percent": self.trend_percent
        }


@dataclass
class TimeSeriesData:
    """Time series data for charts"""
    series_id: str
    name: str
    data_points: List[Tuple[datetime, float]]
    metric_type: MetricType
    unit: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "series_id": self.series_id,
            "name": self.name,
            "data_points": [
                {"timestamp": ts.isoformat(), "value": val}
                for ts, val in self.data_points
            ],
            "metric_type": self.metric_type.value,
            "unit": self.unit
        }


@dataclass
class WritingStats:
    """Writing productivity statistics"""
    period: TimeRange
    total_words: int
    daily_average: float
    best_day: int
    worst_day: int
    total_sessions: int
    average_session_words: float
    average_session_duration_minutes: float
    chapters_completed: int
    projects_active: int
    streak_days: int
    goal_completion_rate: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "period": self.period.value,
            "total_words": self.total_words,
            "daily_average": self.daily_average,
            "best_day": self.best_day,
            "worst_day": self.worst_day,
            "total_sessions": self.total_sessions,
            "average_session_words": self.average_session_words,
            "average_session_duration_minutes": self.average_session_duration_minutes,
            "chapters_completed": self.chapters_completed,
            "projects_active": self.projects_active,
            "streak_days": self.streak_days,
            "goal_completion_rate": self.goal_completion_rate
        }


@dataclass
class SalesStats:
    """Sales statistics"""
    period: TimeRange
    total_units: int
    total_revenue: float
    total_royalties: float
    currency: str
    by_platform: Dict[str, Dict[str, float]]
    by_book: Dict[str, Dict[str, float]]
    by_format: Dict[str, int]
    by_country: Dict[str, int]
    average_price: float
    return_rate: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "period": self.period.value,
            "total_units": self.total_units,
            "total_revenue": self.total_revenue,
            "total_royalties": self.total_royalties,
            "currency": self.currency,
            "by_platform": self.by_platform,
            "by_book": self.by_book,
            "by_format": self.by_format,
            "by_country": self.by_country,
            "average_price": self.average_price,
            "return_rate": self.return_rate
        }


@dataclass
class EngagementStats:
    """Reader engagement statistics"""
    period: TimeRange
    total_reads: int
    total_reviews: int
    average_rating: float
    rating_distribution: Dict[int, int]  # stars -> count
    completion_rate: float
    average_read_time_hours: float
    highlights_count: int
    shares_count: int
    recommendations: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "period": self.period.value,
            "total_reads": self.total_reads,
            "total_reviews": self.total_reviews,
            "average_rating": self.average_rating,
            "rating_distribution": self.rating_distribution,
            "completion_rate": self.completion_rate,
            "average_read_time_hours": self.average_read_time_hours,
            "highlights_count": self.highlights_count,
            "shares_count": self.shares_count,
            "recommendations": self.recommendations
        }


@dataclass
class QualityMetrics:
    """Content quality metrics"""
    book_id: str
    readability_score: float
    coherence_score: float
    engagement_score: float
    cultural_sensitivity_score: float
    trend_alignment_score: float
    overall_quality_score: float
    issues_found: int
    issues_resolved: int
    last_analyzed: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "book_id": self.book_id,
            "readability_score": self.readability_score,
            "coherence_score": self.coherence_score,
            "engagement_score": self.engagement_score,
            "cultural_sensitivity_score": self.cultural_sensitivity_score,
            "trend_alignment_score": self.trend_alignment_score,
            "overall_quality_score": self.overall_quality_score,
            "issues_found": self.issues_found,
            "issues_resolved": self.issues_resolved,
            "last_analyzed": self.last_analyzed.isoformat()
        }


@dataclass
class Alert:
    """Analytics alert"""
    alert_id: str
    level: AlertLevel
    title: str
    message: str
    metric_type: MetricType
    value: Optional[float]
    threshold: Optional[float]
    created_at: datetime
    acknowledged: bool
    action_url: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "level": self.level.value,
            "title": self.title,
            "message": self.message,
            "metric_type": self.metric_type.value,
            "value": self.value,
            "threshold": self.threshold,
            "created_at": self.created_at.isoformat(),
            "acknowledged": self.acknowledged,
            "action_url": self.action_url
        }


@dataclass
class DashboardWidget:
    """A dashboard widget configuration"""
    widget_id: str
    widget_type: str
    title: str
    metric_type: MetricType
    chart_type: ChartType
    time_range: TimeRange
    position: Tuple[int, int]  # row, col
    size: Tuple[int, int]  # width, height
    settings: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "widget_id": self.widget_id,
            "widget_type": self.widget_type,
            "title": self.title,
            "metric_type": self.metric_type.value,
            "chart_type": self.chart_type.value,
            "time_range": self.time_range.value,
            "position": {"row": self.position[0], "col": self.position[1]},
            "size": {"width": self.size[0], "height": self.size[1]},
            "settings": self.settings
        }


@dataclass
class Dashboard:
    """A custom dashboard"""
    dashboard_id: str
    user_id: str
    name: str
    widgets: List[DashboardWidget]
    is_default: bool
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dashboard_id": self.dashboard_id,
            "user_id": self.user_id,
            "name": self.name,
            "widgets": [w.to_dict() for w in self.widgets],
            "is_default": self.is_default,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class Report:
    """An analytics report"""
    report_id: str
    user_id: str
    name: str
    report_type: str
    time_range: TimeRange
    metrics: List[Metric]
    charts: List[TimeSeriesData]
    summary: str
    insights: List[str]
    recommendations: List[str]
    generated_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "user_id": self.user_id,
            "name": self.name,
            "report_type": self.report_type,
            "time_range": self.time_range.value,
            "metrics": [m.to_dict() for m in self.metrics],
            "charts": [c.to_dict() for c in self.charts],
            "summary": self.summary,
            "insights": self.insights,
            "recommendations": self.recommendations,
            "generated_at": self.generated_at.isoformat()
        }


# =============================================================================
# MAIN CLASS
# =============================================================================

class AnalyticsDashboard:
    """
    Analytics Dashboard System

    Provides comprehensive analytics, reporting, and visualization
    for writing productivity and book performance.
    """

    def __init__(self):
        self.dashboards: Dict[str, Dashboard] = {}
        self.reports: Dict[str, Report] = {}
        self.alerts: Dict[str, List[Alert]] = {}
        self.metrics_cache: Dict[str, Dict[str, Metric]] = {}

    async def get_overview(
        self,
        user_id: str,
        time_range: TimeRange = TimeRange.MONTH
    ) -> Dict[str, Any]:
        """
        Get overview dashboard data.
        """
        writing = await self.get_writing_stats(user_id, time_range)
        sales = await self.get_sales_stats(user_id, time_range)
        engagement = await self.get_engagement_stats(user_id, time_range)

        # Key metrics
        key_metrics = [
            self._create_metric("Słowa napisane", writing.total_words, "słów", MetricType.WRITING),
            self._create_metric("Przychody", sales.total_royalties, sales.currency, MetricType.FINANCIAL),
            self._create_metric("Sprzedane egzemplarze", sales.total_units, "szt.", MetricType.SALES),
            self._create_metric("Średnia ocena", engagement.average_rating, "★", MetricType.ENGAGEMENT),
            self._create_metric("Seria pisania", writing.streak_days, "dni", MetricType.WRITING),
            self._create_metric("Realizacja celów", writing.goal_completion_rate * 100, "%", MetricType.WRITING)
        ]

        # Alerts
        alerts = await self.get_active_alerts(user_id)

        return {
            "user_id": user_id,
            "time_range": time_range.value,
            "key_metrics": [m.to_dict() for m in key_metrics],
            "writing_summary": writing.to_dict(),
            "sales_summary": sales.to_dict(),
            "engagement_summary": engagement.to_dict(),
            "alerts": [a.to_dict() for a in alerts],
            "generated_at": datetime.now().isoformat()
        }

    async def get_writing_stats(
        self,
        user_id: str,
        time_range: TimeRange = TimeRange.MONTH
    ) -> WritingStats:
        """
        Get writing productivity statistics.
        """
        # In production, this would query actual data
        # For now, return sample data
        days = self._get_days_for_range(time_range)

        return WritingStats(
            period=time_range,
            total_words=days * 750,  # ~750 words/day average
            daily_average=750.0,
            best_day=2500,
            worst_day=100,
            total_sessions=days,
            average_session_words=750.0,
            average_session_duration_minutes=45.0,
            chapters_completed=days // 7,  # ~1 chapter/week
            projects_active=2,
            streak_days=min(days, 14),
            goal_completion_rate=0.78
        )

    async def get_sales_stats(
        self,
        user_id: str,
        time_range: TimeRange = TimeRange.MONTH
    ) -> SalesStats:
        """
        Get sales statistics.
        """
        days = self._get_days_for_range(time_range)

        return SalesStats(
            period=time_range,
            total_units=days * 5,
            total_revenue=days * 25.0,
            total_royalties=days * 17.5,
            currency="PLN",
            by_platform={
                "amazon_kdp": {"units": days * 3, "revenue": days * 15.0},
                "empik": {"units": days * 1, "revenue": days * 5.0},
                "legimi": {"units": days * 1, "revenue": days * 5.0}
            },
            by_book={
                "book_1": {"units": days * 3, "revenue": days * 15.0},
                "book_2": {"units": days * 2, "revenue": days * 10.0}
            },
            by_format={"ebook": days * 4, "paperback": days * 1},
            by_country={"PL": days * 4, "US": days * 1},
            average_price=19.99,
            return_rate=0.02
        )

    async def get_engagement_stats(
        self,
        user_id: str,
        time_range: TimeRange = TimeRange.MONTH
    ) -> EngagementStats:
        """
        Get reader engagement statistics.
        """
        days = self._get_days_for_range(time_range)

        return EngagementStats(
            period=time_range,
            total_reads=days * 50,
            total_reviews=days // 7,
            average_rating=4.3,
            rating_distribution={5: 45, 4: 30, 3: 15, 2: 7, 1: 3},
            completion_rate=0.72,
            average_read_time_hours=8.5,
            highlights_count=days * 10,
            shares_count=days * 2,
            recommendations=days * 5
        )

    async def get_quality_metrics(
        self,
        book_id: str
    ) -> QualityMetrics:
        """
        Get content quality metrics for a book.
        """
        return QualityMetrics(
            book_id=book_id,
            readability_score=78.5,
            coherence_score=85.2,
            engagement_score=72.8,
            cultural_sensitivity_score=95.0,
            trend_alignment_score=68.5,
            overall_quality_score=80.0,
            issues_found=12,
            issues_resolved=10,
            last_analyzed=datetime.now()
        )

    async def get_time_series(
        self,
        user_id: str,
        metric: str,
        time_range: TimeRange = TimeRange.MONTH,
        granularity: str = "day"
    ) -> TimeSeriesData:
        """
        Get time series data for a metric.
        """
        days = self._get_days_for_range(time_range)
        data_points = []

        for i in range(days):
            date = datetime.now() - timedelta(days=days - i - 1)
            if metric == "words":
                value = 500 + (i % 7) * 100  # Simulate daily variation
            elif metric == "sales":
                value = 3 + (i % 10)
            elif metric == "revenue":
                value = 15 + (i % 10) * 5
            else:
                value = i * 10

            data_points.append((date, value))

        return TimeSeriesData(
            series_id=str(uuid.uuid4()),
            name=metric,
            data_points=data_points,
            metric_type=self._get_metric_type(metric),
            unit=self._get_metric_unit(metric)
        )

    async def get_active_alerts(
        self,
        user_id: str
    ) -> List[Alert]:
        """
        Get active alerts for a user.
        """
        user_alerts = self.alerts.get(user_id, [])
        return [a for a in user_alerts if not a.acknowledged]

    async def create_alert(
        self,
        user_id: str,
        level: AlertLevel,
        title: str,
        message: str,
        metric_type: MetricType,
        value: Optional[float] = None,
        threshold: Optional[float] = None
    ) -> Alert:
        """
        Create a new alert.
        """
        alert = Alert(
            alert_id=str(uuid.uuid4()),
            level=level,
            title=title,
            message=message,
            metric_type=metric_type,
            value=value,
            threshold=threshold,
            created_at=datetime.now(),
            acknowledged=False,
            action_url=None
        )

        if user_id not in self.alerts:
            self.alerts[user_id] = []
        self.alerts[user_id].append(alert)

        return alert

    async def acknowledge_alert(
        self,
        alert_id: str,
        user_id: str
    ) -> bool:
        """
        Acknowledge an alert.
        """
        user_alerts = self.alerts.get(user_id, [])
        for alert in user_alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                return True
        return False

    async def create_dashboard(
        self,
        user_id: str,
        name: str,
        widgets: List[Dict[str, Any]]
    ) -> Dashboard:
        """
        Create a custom dashboard.
        """
        widget_objects = []
        for i, w in enumerate(widgets):
            widget = DashboardWidget(
                widget_id=str(uuid.uuid4()),
                widget_type=w.get("widget_type", "chart"),
                title=w.get("title", f"Widget {i+1}"),
                metric_type=MetricType(w.get("metric_type", "writing")),
                chart_type=ChartType(w.get("chart_type", "line")),
                time_range=TimeRange(w.get("time_range", "month")),
                position=(w.get("row", i), w.get("col", 0)),
                size=(w.get("width", 1), w.get("height", 1)),
                settings=w.get("settings", {})
            )
            widget_objects.append(widget)

        dashboard = Dashboard(
            dashboard_id=str(uuid.uuid4()),
            user_id=user_id,
            name=name,
            widgets=widget_objects,
            is_default=len(self.dashboards) == 0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.dashboards[dashboard.dashboard_id] = dashboard

        return dashboard

    async def generate_report(
        self,
        user_id: str,
        report_type: str,
        time_range: TimeRange = TimeRange.MONTH
    ) -> Report:
        """
        Generate an analytics report.
        """
        # Get relevant data
        writing = await self.get_writing_stats(user_id, time_range)
        sales = await self.get_sales_stats(user_id, time_range)
        engagement = await self.get_engagement_stats(user_id, time_range)

        # Create metrics
        metrics = [
            self._create_metric("Słowa", writing.total_words, "słów", MetricType.WRITING),
            self._create_metric("Przychody", sales.total_royalties, "PLN", MetricType.FINANCIAL),
            self._create_metric("Sprzedaż", sales.total_units, "szt.", MetricType.SALES),
            self._create_metric("Ocena", engagement.average_rating, "★", MetricType.ENGAGEMENT)
        ]

        # Get time series
        charts = [
            await self.get_time_series(user_id, "words", time_range),
            await self.get_time_series(user_id, "sales", time_range),
            await self.get_time_series(user_id, "revenue", time_range)
        ]

        # Generate insights
        insights = self._generate_insights(writing, sales, engagement)

        # Generate recommendations
        recommendations = self._generate_recommendations(writing, sales, engagement)

        # Generate summary
        summary = self._generate_summary(writing, sales, engagement, time_range)

        report = Report(
            report_id=str(uuid.uuid4()),
            user_id=user_id,
            name=f"Raport {report_type} - {time_range.value}",
            report_type=report_type,
            time_range=time_range,
            metrics=metrics,
            charts=charts,
            summary=summary,
            insights=insights,
            recommendations=recommendations,
            generated_at=datetime.now()
        )

        self.reports[report.report_id] = report

        return report

    async def get_comparison(
        self,
        user_id: str,
        period1: TimeRange,
        period2: TimeRange
    ) -> Dict[str, Any]:
        """
        Compare metrics between two periods.
        """
        writing1 = await self.get_writing_stats(user_id, period1)
        writing2 = await self.get_writing_stats(user_id, period2)

        sales1 = await self.get_sales_stats(user_id, period1)
        sales2 = await self.get_sales_stats(user_id, period2)

        def calc_change(v1, v2):
            if v2 == 0:
                return 0
            return ((v1 - v2) / v2) * 100

        return {
            "period1": period1.value,
            "period2": period2.value,
            "comparisons": {
                "words": {
                    "period1": writing1.total_words,
                    "period2": writing2.total_words,
                    "change_percent": calc_change(writing1.total_words, writing2.total_words)
                },
                "sales": {
                    "period1": sales1.total_units,
                    "period2": sales2.total_units,
                    "change_percent": calc_change(sales1.total_units, sales2.total_units)
                },
                "revenue": {
                    "period1": sales1.total_royalties,
                    "period2": sales2.total_royalties,
                    "change_percent": calc_change(sales1.total_royalties, sales2.total_royalties)
                },
                "daily_average": {
                    "period1": writing1.daily_average,
                    "period2": writing2.daily_average,
                    "change_percent": calc_change(writing1.daily_average, writing2.daily_average)
                }
            }
        }

    async def export_data(
        self,
        user_id: str,
        time_range: TimeRange,
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        Export analytics data.
        """
        writing = await self.get_writing_stats(user_id, time_range)
        sales = await self.get_sales_stats(user_id, time_range)
        engagement = await self.get_engagement_stats(user_id, time_range)

        data = {
            "export_date": datetime.now().isoformat(),
            "user_id": user_id,
            "time_range": time_range.value,
            "writing_stats": writing.to_dict(),
            "sales_stats": sales.to_dict(),
            "engagement_stats": engagement.to_dict()
        }

        return {
            "format": format,
            "data": data,
            "download_url": f"/api/v1/analytics/download/{user_id}/{time_range.value}"
        }

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _get_days_for_range(self, time_range: TimeRange) -> int:
        """Get number of days for a time range."""
        ranges = {
            TimeRange.TODAY: 1,
            TimeRange.WEEK: 7,
            TimeRange.MONTH: 30,
            TimeRange.QUARTER: 90,
            TimeRange.YEAR: 365,
            TimeRange.ALL_TIME: 365
        }
        return ranges.get(time_range, 30)

    def _create_metric(
        self,
        name: str,
        value: float,
        unit: str,
        metric_type: MetricType
    ) -> Metric:
        """Create a metric with trend calculation."""
        # Simulate previous value
        previous = value * 0.9  # 10% growth

        if value > previous:
            trend = TrendDirection.UP
            trend_percent = ((value - previous) / previous) * 100
        elif value < previous:
            trend = TrendDirection.DOWN
            trend_percent = ((previous - value) / previous) * -100
        else:
            trend = TrendDirection.STABLE
            trend_percent = 0

        return Metric(
            metric_id=str(uuid.uuid4()),
            name=name,
            value=value,
            unit=unit,
            metric_type=metric_type,
            timestamp=datetime.now(),
            previous_value=previous,
            trend=trend,
            trend_percent=trend_percent
        )

    def _get_metric_type(self, metric: str) -> MetricType:
        """Get metric type for a metric name."""
        types = {
            "words": MetricType.WRITING,
            "sales": MetricType.SALES,
            "revenue": MetricType.FINANCIAL,
            "engagement": MetricType.ENGAGEMENT
        }
        return types.get(metric, MetricType.WRITING)

    def _get_metric_unit(self, metric: str) -> str:
        """Get unit for a metric name."""
        units = {
            "words": "słów",
            "sales": "szt.",
            "revenue": "PLN",
            "engagement": "punktów"
        }
        return units.get(metric, "")

    def _generate_insights(
        self,
        writing: WritingStats,
        sales: SalesStats,
        engagement: EngagementStats
    ) -> List[str]:
        """Generate insights from data."""
        insights = []

        # Writing insights
        if writing.daily_average > 1000:
            insights.append("Twoja produktywność jest powyżej średniej - świetna robota!")
        if writing.streak_days >= 7:
            insights.append(f"Utrzymujesz serię {writing.streak_days} dni - kontynuuj!")
        if writing.goal_completion_rate < 0.5:
            insights.append("Cel dzienny jest rzadko osiągany - rozważ dostosowanie")

        # Sales insights
        if sales.total_units > 0:
            top_platform = max(sales.by_platform.items(), key=lambda x: x[1]["units"])[0]
            insights.append(f"Najlepiej sprzedajesz na platformie {top_platform}")
        if sales.return_rate > 0.05:
            insights.append("Zwroty są powyżej normy - sprawdź opisy produktów")

        # Engagement insights
        if engagement.average_rating >= 4.5:
            insights.append("Świetne oceny! Czytelnicy kochają Twoje książki")
        if engagement.completion_rate < 0.5:
            insights.append("Niska stopa ukończenia - sprawdź pacing książek")

        return insights

    def _generate_recommendations(
        self,
        writing: WritingStats,
        sales: SalesStats,
        engagement: EngagementStats
    ) -> List[str]:
        """Generate recommendations from data."""
        recommendations = []

        # Writing recommendations
        if writing.daily_average < 500:
            recommendations.append("Spróbuj pisać co najmniej 500 słów dziennie")
        if writing.goal_completion_rate < 0.7:
            recommendations.append("Ustaw realistyczny cel dzienny i trzymaj się go")

        # Sales recommendations
        if len(sales.by_platform) < 3:
            recommendations.append("Rozważ dystrybucję na więcej platform")

        # Engagement recommendations
        if engagement.total_reviews < 10:
            recommendations.append("Zachęcaj czytelników do pozostawienia recenzji")

        return recommendations

    def _generate_summary(
        self,
        writing: WritingStats,
        sales: SalesStats,
        engagement: EngagementStats,
        time_range: TimeRange
    ) -> str:
        """Generate a summary of the data."""
        period_name = {
            TimeRange.TODAY: "dziś",
            TimeRange.WEEK: "w tym tygodniu",
            TimeRange.MONTH: "w tym miesiącu",
            TimeRange.QUARTER: "w tym kwartale",
            TimeRange.YEAR: "w tym roku",
            TimeRange.ALL_TIME: "łącznie"
        }.get(time_range, "w wybranym okresie")

        return (
            f"Napisałeś {writing.total_words:,} słów {period_name}, "
            f"sprzedając {sales.total_units} egzemplarzy "
            f"i zarabiając {sales.total_royalties:.2f} {sales.currency}. "
            f"Średnia ocena: {engagement.average_rating:.1f}★."
        )

    # =========================================================================
    # PUBLIC GETTERS
    # =========================================================================

    def get_dashboard(self, dashboard_id: str) -> Optional[Dashboard]:
        """Get a dashboard by ID."""
        return self.dashboards.get(dashboard_id)

    def get_report(self, report_id: str) -> Optional[Report]:
        """Get a report by ID."""
        return self.reports.get(report_id)

    def list_dashboards(self, user_id: str) -> List[Dict[str, Any]]:
        """List dashboards for a user."""
        user_dashboards = [
            d for d in self.dashboards.values()
            if d.user_id == user_id
        ]
        return [d.to_dict() for d in user_dashboards]

    def list_reports(self, user_id: str) -> List[Dict[str, Any]]:
        """List reports for a user."""
        user_reports = [
            r for r in self.reports.values()
            if r.user_id == user_id
        ]
        return [
            {
                "report_id": r.report_id,
                "name": r.name,
                "report_type": r.report_type,
                "generated_at": r.generated_at.isoformat()
            }
            for r in user_reports
        ]


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_analytics_dashboard: Optional[AnalyticsDashboard] = None


def get_analytics_dashboard() -> AnalyticsDashboard:
    """Get the singleton analytics dashboard instance."""
    global _analytics_dashboard
    if _analytics_dashboard is None:
        _analytics_dashboard = AnalyticsDashboard()
    return _analytics_dashboard


# Singleton instance for API usage
analytics_dashboard = get_analytics_dashboard()
