#!/usr/bin/env python3
"""
Test script for Sentry integration.
Sends test events to verify Sentry is working correctly.

Usage:
    python monitoring/test_sentry.py
"""

import asyncio
import os
import time

from narra_forge.monitoring.sentry import (
    add_breadcrumb,
    capture_exception,
    capture_message,
    init_sentry,
    set_context,
    set_tag,
    SentrySpan,
    SentryTransaction,
)


def test_error_capture():
    """Test 1: Capture exception."""
    print("\n1️⃣  Testing error capture...")

    try:
        # Intentionally raise error
        raise ValueError("This is a test error from NARRA_FORGE")
    except Exception as e:
        event_id = capture_exception(
            e,
            tags={"test": "error_capture", "component": "test_suite"},
            extras={"description": "Testing Sentry error tracking"}
        )
        print(f"   ✓ Error captured: {event_id}")


def test_message_capture():
    """Test 2: Capture message."""
    print("\n2️⃣  Testing message capture...")

    event_id = capture_message(
        "Test message from NARRA_FORGE monitoring",
        level="info",
        tags={"test": "message_capture"}
    )
    print(f"   ✓ Message captured: {event_id}")


def test_breadcrumbs():
    """Test 3: Breadcrumbs."""
    print("\n3️⃣  Testing breadcrumbs...")

    # Add breadcrumbs
    add_breadcrumb(
        message="Test started",
        category="test",
        level="info",
        data={"timestamp": time.time()}
    )

    add_breadcrumb(
        message="Processing step 1",
        category="test",
        level="info"
    )

    add_breadcrumb(
        message="Processing step 2",
        category="test",
        level="info"
    )

    # Trigger error - breadcrumbs will be attached
    try:
        raise RuntimeError("Error with breadcrumbs attached")
    except Exception as e:
        event_id = capture_exception(e)
        print(f"   ✓ Error with breadcrumbs captured: {event_id}")


def test_context():
    """Test 4: Custom context."""
    print("\n4️⃣  Testing custom context...")

    # Set context
    set_context("job", {
        "job_id": "test_job_123",
        "production_type": "short_story",
        "genre": "fantasy"
    })

    set_tag("environment", "test")
    set_tag("component", "sentry_test")

    # Trigger error - context will be attached
    try:
        raise ValueError("Error with custom context")
    except Exception as e:
        event_id = capture_exception(e)
        print(f"   ✓ Error with context captured: {event_id}")


async def test_transaction():
    """Test 5: Performance transaction."""
    print("\n5️⃣  Testing performance transaction...")

    with SentryTransaction(
        op="test.execute",
        name="sentry_integration_test",
        description="Testing Sentry transaction tracking"
    ) as transaction:
        transaction.set_tag("test", "performance")

        # Simulate work with spans
        with SentrySpan(op="test.step1", description="Step 1"):
            await asyncio.sleep(0.1)
            print("   ✓ Step 1 completed")

        with SentrySpan(op="test.step2", description="Step 2"):
            await asyncio.sleep(0.1)
            print("   ✓ Step 2 completed")

        with SentrySpan(op="test.step3", description="Step 3"):
            await asyncio.sleep(0.1)
            print("   ✓ Step 3 completed")

    print("   ✓ Transaction completed")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 NARRA_FORGE Sentry Integration Test")
    print("=" * 60)

    # Get Sentry DSN
    dsn = os.getenv("SENTRY_DSN")

    if not dsn:
        print("\n❌ ERROR: SENTRY_DSN not set")
        print()
        print("Please set SENTRY_DSN environment variable:")
        print("  export SENTRY_DSN='https://your-dsn@o123.ingest.sentry.io/456'")
        print()
        print("Or add to .env file:")
        print("  SENTRY_DSN=https://your-dsn@o123.ingest.sentry.io/456")
        print()
        return 1

    # Initialize Sentry
    print("\n📡 Initializing Sentry...")
    init_sentry(
        dsn=dsn,
        environment="test",
        release="narra-forge@2.0.0-test",
        traces_sample_rate=1.0,  # 100% for testing
        debug=True  # Enable debug logging
    )
    print("   ✓ Sentry initialized")

    # Run tests
    test_error_capture()
    test_message_capture()
    test_breadcrumbs()
    test_context()
    await test_transaction()

    # Summary
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
    print()
    print("📊 Check Sentry dashboard for events:")
    print("   https://sentry.io/organizations/your-org/issues/")
    print()
    print("Expected events:")
    print("   - 3 errors (ValueError, RuntimeError, ValueError)")
    print("   - 1 message (info level)")
    print("   - 1 transaction (sentry_integration_test)")
    print()
    print("⏱️  Note: Events may take 1-2 minutes to appear in Sentry")
    print()

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
