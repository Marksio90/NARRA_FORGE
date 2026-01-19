"""Unit tests for Celery tasks."""

from unittest.mock import MagicMock, patch

from services.tasks import celery_app, get_task_status, health_check, revoke_task


def test_celery_app_configuration() -> None:
    """Test Celery app is properly configured."""
    assert celery_app.conf.task_serializer == "json"
    assert celery_app.conf.accept_content == ["json"]
    assert celery_app.conf.result_serializer == "json"
    assert celery_app.conf.timezone == "UTC"
    assert celery_app.conf.enable_utc is True
    assert celery_app.conf.task_track_started is True


def test_celery_task_routing() -> None:
    """Test task routing configuration."""
    assert "tasks.health_check" in celery_app.conf.task_routes
    assert "tasks.job.*" in celery_app.conf.task_routes
    assert "tasks.agent.*" in celery_app.conf.task_routes
    assert "tasks.qa.*" in celery_app.conf.task_routes

    assert celery_app.conf.task_routes["tasks.health_check"]["queue"] == "default"
    assert celery_app.conf.task_routes["tasks.job.*"]["queue"] == "jobs"
    assert celery_app.conf.task_routes["tasks.agent.*"]["queue"] == "agents"
    assert celery_app.conf.task_routes["tasks.qa.*"]["queue"] == "qa"


def test_celery_default_queue() -> None:
    """Test default queue configuration."""
    assert celery_app.conf.task_default_queue == "default"
    assert celery_app.conf.task_default_exchange == "default"
    assert celery_app.conf.task_default_routing_key == "default"


def test_celery_worker_settings() -> None:
    """Test worker settings."""
    assert celery_app.conf.worker_prefetch_multiplier == 4
    assert celery_app.conf.worker_max_tasks_per_child == 1000
    assert celery_app.conf.task_acks_late is True
    assert celery_app.conf.task_reject_on_worker_lost is True


def test_celery_result_settings() -> None:
    """Test result backend settings."""
    assert celery_app.conf.result_expires == 86400
    assert celery_app.conf.task_ignore_result is False
    assert celery_app.conf.task_store_errors_even_if_ignored is True


def test_health_check_task() -> None:
    """Test health check task."""
    result = health_check()

    assert isinstance(result, dict)
    assert result["status"] == "healthy"
    assert result["message"] == "Celery worker is operational"


def test_get_task_status_pending() -> None:
    """Test getting status of pending task."""
    task_id = "test-task-id-123"

    with patch("services.tasks.AsyncResult") as mock_result_class:
        mock_result = MagicMock()
        mock_result.state = "PENDING"
        mock_result.ready.return_value = False
        mock_result.failed.return_value = False
        mock_result_class.return_value = mock_result

        status = get_task_status(task_id)

        assert status["task_id"] == task_id
        assert status["status"] == "PENDING"
        assert status["result"] is None
        assert status["traceback"] is None


def test_get_task_status_success() -> None:
    """Test getting status of successful task."""
    task_id = "test-task-id-456"

    with patch("services.tasks.AsyncResult") as mock_result_class:
        mock_result = MagicMock()
        mock_result.state = "SUCCESS"
        mock_result.ready.return_value = True
        mock_result.result = {"data": "test"}
        mock_result.failed.return_value = False
        mock_result_class.return_value = mock_result

        status = get_task_status(task_id)

        assert status["task_id"] == task_id
        assert status["status"] == "SUCCESS"
        assert status["result"] == {"data": "test"}
        assert status["traceback"] is None


def test_get_task_status_failed() -> None:
    """Test getting status of failed task."""
    task_id = "test-task-id-789"

    with patch("services.tasks.AsyncResult") as mock_result_class:
        mock_result = MagicMock()
        mock_result.state = "FAILURE"
        mock_result.ready.return_value = True
        mock_result.result = Exception("Test error")
        mock_result.failed.return_value = True
        mock_result.traceback = "Traceback..."
        mock_result_class.return_value = mock_result

        status = get_task_status(task_id)

        assert status["task_id"] == task_id
        assert status["status"] == "FAILURE"
        assert status["traceback"] == "Traceback..."


def test_revoke_task_no_terminate() -> None:
    """Test revoking task without termination."""
    task_id = "test-task-revoke-1"

    with patch.object(celery_app.control, "revoke") as mock_revoke:
        result = revoke_task(task_id, terminate=False)

        assert result["task_id"] == task_id
        assert result["revoked"] is True
        assert result["terminated"] is False
        mock_revoke.assert_called_once_with(task_id, terminate=False)


def test_revoke_task_with_terminate() -> None:
    """Test revoking task with termination."""
    task_id = "test-task-revoke-2"

    with patch.object(celery_app.control, "revoke") as mock_revoke:
        result = revoke_task(task_id, terminate=True)

        assert result["task_id"] == task_id
        assert result["revoked"] is True
        assert result["terminated"] is True
        mock_revoke.assert_called_once_with(task_id, terminate=True)


def test_task_time_limits() -> None:
    """Test task time limit configuration."""
    assert celery_app.conf.task_time_limit == 3600  # 1 hour
    assert celery_app.conf.task_soft_time_limit == 3300  # 55 minutes
