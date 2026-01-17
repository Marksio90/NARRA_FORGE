"""
Unit tests for Sentry integration.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from narra_forge.monitoring.sentry import (
    add_breadcrumb,
    before_send_hook,
    capture_exception,
    capture_message,
    init_sentry,
    set_context,
    set_tag,
    set_user,
    SentrySpan,
    SentryTransaction,
)


class TestSentryInit:
    """Test Sentry initialization."""

    @patch("narra_forge.monitoring.sentry.sentry_sdk")
    def test_init_with_dsn(self, mock_sdk):
        """Test initialization with DSN."""
        init_sentry(
            dsn="https://test@example.com/123",
            environment="test",
            traces_sample_rate=0.5
        )

        mock_sdk.init.assert_called_once()
        call_kwargs = mock_sdk.init.call_args[1]

        assert call_kwargs["dsn"] == "https://test@example.com/123"
        assert call_kwargs["environment"] == "test"
        assert call_kwargs["traces_sample_rate"] == 0.5

    @patch("narra_forge.monitoring.sentry.sentry_sdk")
    @patch.dict("os.environ", {"SENTRY_DSN": "https://env@example.com/456"})
    def test_init_from_env(self, mock_sdk):
        """Test initialization from environment variable."""
        init_sentry()

        mock_sdk.init.assert_called_once()
        call_kwargs = mock_sdk.init.call_args[1]
        assert call_kwargs["dsn"] == "https://env@example.com/456"

    @patch("narra_forge.monitoring.sentry.sentry_sdk")
    @patch("builtins.print")
    def test_init_without_dsn(self, mock_print, mock_sdk):
        """Test initialization without DSN (should skip)."""
        init_sentry(dsn=None)

        mock_sdk.init.assert_not_called()
        mock_print.assert_called_once()
        assert "Sentry DSN not provided" in str(mock_print.call_args)


class TestBeforeSendHook:
    """Test before_send_hook filtering."""

    def test_filter_keyboard_interrupt(self):
        """Test filtering KeyboardInterrupt."""
        event = {"exception": {"values": [{"type": "KeyboardInterrupt"}]}}
        hint = {"exc_info": (KeyboardInterrupt, KeyboardInterrupt(), None)}

        result = before_send_hook(event, hint)
        assert result is None

    def test_filter_rate_limit_without_retry(self):
        """Test filtering RateLimitError without retry info."""

        class RateLimitError(Exception):
            pass

        event = {"exception": {"values": [{"type": "RateLimitError"}]}}
        hint = {"exc_info": (RateLimitError, RateLimitError(), None)}

        result = before_send_hook(event, hint)
        assert result is None

    def test_allow_rate_limit_with_retry(self):
        """Test allowing RateLimitError with retry info."""

        class RateLimitError(Exception):
            pass

        event = {
            "exception": {"values": [{"type": "RateLimitError"}]},
            "extra": {"retry_attempt": 3}
        }
        hint = {"exc_info": (RateLimitError, RateLimitError(), None)}

        result = before_send_hook(event, hint)
        assert result == event

    def test_allow_normal_exceptions(self):
        """Test allowing normal exceptions."""
        event = {"exception": {"values": [{"type": "ValueError"}]}}
        hint = {"exc_info": (ValueError, ValueError("test"), None)}

        result = before_send_hook(event, hint)
        assert result == event


class TestSentryHelpers:
    """Test Sentry helper functions."""

    @patch("narra_forge.monitoring.sentry.sentry_sdk")
    def test_set_context(self, mock_sdk):
        """Test setting context."""
        set_context("job", {"job_id": "123", "type": "short_story"})

        mock_sdk.set_context.assert_called_once_with(
            "job",
            {"job_id": "123", "type": "short_story"}
        )

    @patch("narra_forge.monitoring.sentry.sentry_sdk")
    def test_set_tag(self, mock_sdk):
        """Test setting tag."""
        set_tag("environment", "production")

        mock_sdk.set_tag.assert_called_once_with("environment", "production")

    @patch("narra_forge.monitoring.sentry.sentry_sdk")
    def test_set_user(self, mock_sdk):
        """Test setting user."""
        set_user(user_id="user_123", email="test@example.com")

        mock_sdk.set_user.assert_called_once_with({
            "id": "user_123",
            "email": "test@example.com"
        })

    @patch("narra_forge.monitoring.sentry.sentry_sdk")
    def test_set_user_without_id(self, mock_sdk):
        """Test setting user without ID."""
        set_user(email="test@example.com", username="tester")

        mock_sdk.set_user.assert_called_once_with({
            "email": "test@example.com",
            "username": "tester"
        })


class TestCaptureException:
    """Test exception capture."""

    @patch("narra_forge.monitoring.sentry.sentry_sdk")
    def test_capture_exception_basic(self, mock_sdk):
        """Test basic exception capture."""
        mock_sdk.capture_exception.return_value = "event_123"

        error = ValueError("test error")
        event_id = capture_exception(error)

        assert event_id == "event_123"
        mock_sdk.capture_exception.assert_called_once_with(error)

    @patch("narra_forge.monitoring.sentry.sentry_sdk")
    def test_capture_exception_with_tags(self, mock_sdk):
        """Test exception capture with tags."""
        mock_sdk.capture_exception.return_value = "event_456"

        error = ValueError("test error")
        event_id = capture_exception(
            error,
            tags={"agent": "a06", "model": "gpt-4o"}
        )

        assert event_id == "event_456"
        assert mock_sdk.set_tag.call_count == 2
        mock_sdk.set_tag.assert_any_call("agent", "a06")
        mock_sdk.set_tag.assert_any_call("model", "gpt-4o")

    @patch("narra_forge.monitoring.sentry.sentry_sdk")
    def test_capture_exception_with_extras(self, mock_sdk):
        """Test exception capture with extras."""
        mock_sdk.capture_exception.return_value = "event_789"

        error = ValueError("test error")
        event_id = capture_exception(
            error,
            extras={"input_data": {"key": "value"}}
        )

        assert event_id == "event_789"
        mock_sdk.set_extra.assert_called_once_with("input_data", {"key": "value"})


class TestCaptureMessage:
    """Test message capture."""

    @patch("narra_forge.monitoring.sentry.sentry_sdk")
    def test_capture_message_basic(self, mock_sdk):
        """Test basic message capture."""
        mock_sdk.capture_message.return_value = "msg_123"

        event_id = capture_message("Test message")

        assert event_id == "msg_123"
        mock_sdk.capture_message.assert_called_once_with("Test message", level="info")

    @patch("narra_forge.monitoring.sentry.sentry_sdk")
    def test_capture_message_with_level(self, mock_sdk):
        """Test message capture with custom level."""
        mock_sdk.capture_message.return_value = "msg_456"

        event_id = capture_message("Warning message", level="warning")

        assert event_id == "msg_456"
        mock_sdk.capture_message.assert_called_once_with("Warning message", level="warning")

    @patch("narra_forge.monitoring.sentry.sentry_sdk")
    def test_capture_message_with_tags(self, mock_sdk):
        """Test message capture with tags."""
        mock_sdk.capture_message.return_value = "msg_789"

        event_id = capture_message(
            "Tagged message",
            tags={"component": "test"}
        )

        assert event_id == "msg_789"
        mock_sdk.set_tag.assert_called_once_with("component", "test")


class TestAddBreadcrumb:
    """Test breadcrumb addition."""

    @patch("narra_forge.monitoring.sentry.sentry_sdk")
    def test_add_breadcrumb_basic(self, mock_sdk):
        """Test basic breadcrumb."""
        add_breadcrumb("Test breadcrumb")

        mock_sdk.add_breadcrumb.assert_called_once_with(
            message="Test breadcrumb",
            category="default",
            level="info",
            data={}
        )

    @patch("narra_forge.monitoring.sentry.sentry_sdk")
    def test_add_breadcrumb_with_data(self, mock_sdk):
        """Test breadcrumb with data."""
        add_breadcrumb(
            message="Pipeline started",
            category="pipeline",
            level="info",
            data={"job_id": "123", "type": "short_story"}
        )

        mock_sdk.add_breadcrumb.assert_called_once_with(
            message="Pipeline started",
            category="pipeline",
            level="info",
            data={"job_id": "123", "type": "short_story"}
        )


class TestSentryTransaction:
    """Test SentryTransaction context manager."""

    @patch("narra_forge.monitoring.sentry.sentry_sdk")
    def test_transaction_context_manager(self, mock_sdk):
        """Test transaction as context manager."""
        mock_transaction = MagicMock()
        mock_sdk.start_transaction.return_value = mock_transaction

        with SentryTransaction(
            op="test.operation",
            name="test_transaction",
            description="Test description"
        ) as transaction:
            assert transaction == mock_transaction

        mock_sdk.start_transaction.assert_called_once_with(
            op="test.operation",
            name="test_transaction",
            description="Test description"
        )
        mock_transaction.__enter__.assert_called_once()
        mock_transaction.__exit__.assert_called_once()


class TestSentrySpan:
    """Test SentrySpan context manager."""

    @patch("narra_forge.monitoring.sentry.sentry_sdk")
    def test_span_context_manager(self, mock_sdk):
        """Test span as context manager."""
        mock_span = MagicMock()
        mock_sdk.start_span.return_value = mock_span

        with SentrySpan(
            op="test.step",
            description="Test step"
        ) as span:
            assert span == mock_span

        mock_sdk.start_span.assert_called_once_with(
            op="test.step",
            description="Test step"
        )
        mock_span.__enter__.assert_called_once()
        mock_span.__exit__.assert_called_once()


@pytest.mark.integration
class TestSentryIntegration:
    """Integration tests for Sentry (require real DSN)."""

    @pytest.mark.skipif(
        not pytest.config.getoption("--integration", default=False),
        reason="Integration tests disabled"
    )
    def test_real_sentry_capture(self):
        """Test real Sentry capture (requires DSN in env)."""
        import os

        dsn = os.getenv("SENTRY_DSN")
        if not dsn:
            pytest.skip("SENTRY_DSN not set")

        init_sentry(dsn=dsn, environment="test")

        # Capture test error
        try:
            raise ValueError("Integration test error")
        except Exception as e:
            event_id = capture_exception(e)
            assert event_id is not None
