"""
Event Bus / Message Queue - NarraForge 3.0 Phase 5
Asynchronous event-driven communication between services
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set, Awaitable
from enum import Enum
from datetime import datetime, timedelta
import uuid
import asyncio
from collections import defaultdict
import json
import logging

logger = logging.getLogger(__name__)


class EventPriority(Enum):
    """Event priority levels"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class EventStatus(Enum):
    """Event processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"
    EXPIRED = "expired"


class DeliveryMode(Enum):
    """Event delivery modes"""
    AT_MOST_ONCE = "at_most_once"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE = "exactly_once"


class SubscriptionType(Enum):
    """Subscription types"""
    PUSH = "push"  # Event pushed to handler
    PULL = "pull"  # Consumer pulls events


@dataclass
class Event:
    """Event message"""
    event_id: str
    event_type: str
    source: str
    data: Dict[str, Any]
    priority: EventPriority = EventPriority.NORMAL
    status: EventStatus = EventStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None  # ID of event that caused this one
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "source": self.source,
            "data": self.data,
            "priority": self.priority.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "correlation_id": self.correlation_id,
            "retry_count": self.retry_count,
            "metadata": self.metadata
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass
class Subscription:
    """Event subscription"""
    subscription_id: str
    event_types: List[str]  # Can use wildcards like "book.*"
    handler: Optional[Callable[[Event], Awaitable[None]]] = None
    subscriber_id: str = ""
    subscription_type: SubscriptionType = SubscriptionType.PUSH
    filter_expression: Optional[str] = None
    delivery_mode: DeliveryMode = DeliveryMode.AT_LEAST_ONCE
    max_concurrent: int = 10
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subscription_id": self.subscription_id,
            "event_types": self.event_types,
            "subscriber_id": self.subscriber_id,
            "subscription_type": self.subscription_type.value,
            "filter_expression": self.filter_expression,
            "delivery_mode": self.delivery_mode.value,
            "max_concurrent": self.max_concurrent,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active
        }


@dataclass
class Queue:
    """Message queue"""
    queue_id: str
    name: str
    max_size: int = 10000
    retention_hours: int = 24
    dead_letter_queue: Optional[str] = None
    events: List[Event] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "queue_id": self.queue_id,
            "name": self.name,
            "max_size": self.max_size,
            "retention_hours": self.retention_hours,
            "dead_letter_queue": self.dead_letter_queue,
            "events_count": len(self.events),
            "created_at": self.created_at.isoformat()
        }


@dataclass
class Topic:
    """Publish-subscribe topic"""
    topic_id: str
    name: str
    description: str = ""
    subscriptions: List[str] = field(default_factory=list)
    retention_hours: int = 24
    partitions: int = 1
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic_id": self.topic_id,
            "name": self.name,
            "description": self.description,
            "subscriptions_count": len(self.subscriptions),
            "retention_hours": self.retention_hours,
            "partitions": self.partitions,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class DeliveryAttempt:
    """Record of delivery attempt"""
    attempt_id: str
    event_id: str
    subscription_id: str
    status: str
    attempted_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "attempt_id": self.attempt_id,
            "event_id": self.event_id,
            "subscription_id": self.subscription_id,
            "status": self.status,
            "attempted_at": self.attempted_at.isoformat(),
            "error_message": self.error_message,
            "duration_ms": self.duration_ms
        }


# Pre-defined event types for NarraForge
NARRAFORGE_EVENTS = {
    # Book lifecycle events
    "book.created": "New book project created",
    "book.updated": "Book content updated",
    "book.completed": "Book generation completed",
    "book.published": "Book published to platform",
    # Chapter events
    "chapter.generated": "Chapter generation completed",
    "chapter.revised": "Chapter revision completed",
    "chapter.approved": "Chapter approved by user",
    # Character events
    "character.created": "New character created",
    "character.developed": "Character development updated",
    # Multimodal events
    "cover.generated": "Cover art generated",
    "illustration.created": "Illustration created",
    "audiobook.chapter_narrated": "Chapter narration completed",
    "trailer.generated": "Book trailer generated",
    # AI events
    "ai.analysis_complete": "AI analysis completed",
    "ai.suggestion_ready": "AI suggestion ready",
    "ai.coherence_check": "Coherence check completed",
    # Publishing events
    "publishing.submitted": "Book submitted to platform",
    "publishing.approved": "Book approved by platform",
    "publishing.live": "Book is live on platform",
    # Collaboration events
    "collaboration.user_joined": "User joined collaboration",
    "collaboration.edit_made": "Collaborative edit made",
    "collaboration.conflict_detected": "Edit conflict detected",
    # Analytics events
    "analytics.report_ready": "Analytics report ready",
    "analytics.alert_triggered": "Analytics alert triggered",
}


class EventBus:
    """
    Event Bus for NarraForge

    Features:
    - Publish-subscribe pattern
    - Message queues
    - Event routing with wildcards
    - Priority-based processing
    - Dead letter queues
    - Event replay
    - Exactly-once delivery
    - Event sourcing support
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

        # Topics
        self.topics: Dict[str, Topic] = {}

        # Queues
        self.queues: Dict[str, Queue] = {}

        # Subscriptions
        self.subscriptions: Dict[str, Subscription] = {}

        # Event store (for replay)
        self.event_store: List[Event] = []

        # Delivery attempts
        self.delivery_attempts: List[DeliveryAttempt] = []

        # Processing state
        self.processing_events: Set[str] = set()

        # Dead letter queue
        self.dead_letter_events: List[Event] = []

        # Metrics
        self.metrics: Dict[str, Any] = {
            "total_events_published": 0,
            "total_events_delivered": 0,
            "total_events_failed": 0,
            "dead_letter_count": 0
        }

        # Background tasks
        self._processing_task: Optional[asyncio.Task] = None

        self._register_default_topics()
        self._initialized = True

    def _register_default_topics(self):
        """Register default NarraForge topics"""
        default_topics = [
            ("book-events", "Book lifecycle events"),
            ("chapter-events", "Chapter generation events"),
            ("character-events", "Character development events"),
            ("multimodal-events", "Multimodal content events"),
            ("ai-events", "AI processing events"),
            ("publishing-events", "Publishing lifecycle events"),
            ("collaboration-events", "Collaboration events"),
            ("analytics-events", "Analytics and reporting events"),
            ("system-events", "System health and status events"),
        ]

        for name, description in default_topics:
            self.create_topic(name, description)

    def create_topic(
        self,
        name: str,
        description: str = "",
        retention_hours: int = 24,
        partitions: int = 1
    ) -> Topic:
        """Create a new topic"""
        topic_id = str(uuid.uuid4())

        topic = Topic(
            topic_id=topic_id,
            name=name,
            description=description,
            retention_hours=retention_hours,
            partitions=partitions
        )

        self.topics[name] = topic
        return topic

    def get_topic(self, name: str) -> Optional[Topic]:
        """Get topic by name"""
        return self.topics.get(name)

    def create_queue(
        self,
        name: str,
        max_size: int = 10000,
        retention_hours: int = 24,
        dead_letter_queue: Optional[str] = None
    ) -> Queue:
        """Create a message queue"""
        queue_id = str(uuid.uuid4())

        queue = Queue(
            queue_id=queue_id,
            name=name,
            max_size=max_size,
            retention_hours=retention_hours,
            dead_letter_queue=dead_letter_queue
        )

        self.queues[name] = queue
        return queue

    def get_queue(self, name: str) -> Optional[Queue]:
        """Get queue by name"""
        return self.queues.get(name)

    def subscribe(
        self,
        event_types: List[str],
        handler: Callable[[Event], Awaitable[None]],
        subscriber_id: str = "",
        filter_expression: Optional[str] = None,
        delivery_mode: DeliveryMode = DeliveryMode.AT_LEAST_ONCE,
        max_concurrent: int = 10
    ) -> Subscription:
        """Subscribe to event types"""
        subscription_id = str(uuid.uuid4())

        subscription = Subscription(
            subscription_id=subscription_id,
            event_types=event_types,
            handler=handler,
            subscriber_id=subscriber_id or subscription_id,
            filter_expression=filter_expression,
            delivery_mode=delivery_mode,
            max_concurrent=max_concurrent
        )

        self.subscriptions[subscription_id] = subscription

        # Register with topics
        for event_type in event_types:
            topic_name = event_type.split(".")[0] + "-events"
            if topic_name in self.topics:
                self.topics[topic_name].subscriptions.append(subscription_id)

        return subscription

    def unsubscribe(self, subscription_id: str):
        """Remove subscription"""
        if subscription_id in self.subscriptions:
            subscription = self.subscriptions[subscription_id]
            subscription.is_active = False

            # Remove from topics
            for topic in self.topics.values():
                if subscription_id in topic.subscriptions:
                    topic.subscriptions.remove(subscription_id)

            del self.subscriptions[subscription_id]

    async def publish(
        self,
        event_type: str,
        source: str,
        data: Dict[str, Any],
        priority: EventPriority = EventPriority.NORMAL,
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None,
        ttl_seconds: Optional[int] = None
    ) -> Event:
        """Publish an event"""
        event_id = str(uuid.uuid4())

        event = Event(
            event_id=event_id,
            event_type=event_type,
            source=source,
            data=data,
            priority=priority,
            correlation_id=correlation_id or event_id,
            causation_id=causation_id,
            expires_at=datetime.now() + timedelta(seconds=ttl_seconds) if ttl_seconds else None
        )

        # Store event
        self.event_store.append(event)
        self.metrics["total_events_published"] += 1

        # Find matching subscriptions
        matching_subscriptions = self._find_matching_subscriptions(event_type)

        # Deliver to subscribers
        for subscription in matching_subscriptions:
            if subscription.is_active:
                asyncio.create_task(
                    self._deliver_event(event, subscription)
                )

        # Add to relevant queues
        for queue in self.queues.values():
            if len(queue.events) < queue.max_size:
                queue.events.append(event)

        logger.info(f"Published event: {event_type} ({event_id})")
        return event

    def publish_sync(
        self,
        event_type: str,
        source: str,
        data: Dict[str, Any],
        priority: EventPriority = EventPriority.NORMAL
    ) -> Event:
        """Synchronous publish (for non-async contexts)"""
        event_id = str(uuid.uuid4())

        event = Event(
            event_id=event_id,
            event_type=event_type,
            source=source,
            data=data,
            priority=priority,
            correlation_id=event_id
        )

        self.event_store.append(event)
        self.metrics["total_events_published"] += 1

        return event

    async def _deliver_event(
        self,
        event: Event,
        subscription: Subscription
    ):
        """Deliver event to subscriber"""
        attempt_id = str(uuid.uuid4())
        start_time = datetime.now()

        attempt = DeliveryAttempt(
            attempt_id=attempt_id,
            event_id=event.event_id,
            subscription_id=subscription.subscription_id,
            status="processing",
            attempted_at=start_time
        )

        try:
            # Check filter
            if subscription.filter_expression:
                if not self._evaluate_filter(subscription.filter_expression, event):
                    attempt.status = "filtered"
                    self.delivery_attempts.append(attempt)
                    return

            # Mark as processing
            self.processing_events.add(event.event_id)

            # Call handler
            if subscription.handler:
                await subscription.handler(event)

            # Mark as delivered
            event.status = EventStatus.COMPLETED
            event.processed_at = datetime.now()
            attempt.status = "delivered"
            self.metrics["total_events_delivered"] += 1

        except Exception as e:
            attempt.status = "failed"
            attempt.error_message = str(e)
            event.retry_count += 1

            if event.retry_count >= event.max_retries:
                event.status = EventStatus.DEAD_LETTER
                self.dead_letter_events.append(event)
                self.metrics["dead_letter_count"] += 1
            else:
                event.status = EventStatus.PENDING
                # Retry with exponential backoff
                delay = 2 ** event.retry_count
                await asyncio.sleep(delay)
                await self._deliver_event(event, subscription)

            self.metrics["total_events_failed"] += 1

        finally:
            self.processing_events.discard(event.event_id)
            attempt.completed_at = datetime.now()
            attempt.duration_ms = (attempt.completed_at - start_time).total_seconds() * 1000
            self.delivery_attempts.append(attempt)

    def _find_matching_subscriptions(
        self,
        event_type: str
    ) -> List[Subscription]:
        """Find subscriptions matching event type"""
        matching = []

        for subscription in self.subscriptions.values():
            for pattern in subscription.event_types:
                if self._matches_pattern(event_type, pattern):
                    matching.append(subscription)
                    break

        return matching

    def _matches_pattern(self, event_type: str, pattern: str) -> bool:
        """Check if event type matches pattern (supports wildcards)"""
        if pattern == "*":
            return True

        if pattern.endswith(".*"):
            prefix = pattern[:-2]
            return event_type.startswith(prefix + ".")

        if pattern.endswith("*"):
            prefix = pattern[:-1]
            return event_type.startswith(prefix)

        return event_type == pattern

    def _evaluate_filter(self, expression: str, event: Event) -> bool:
        """Evaluate filter expression"""
        try:
            context = {
                "event": event.to_dict(),
                "data": event.data,
                "source": event.source,
                "priority": event.priority.value
            }
            return eval(expression, {"__builtins__": {}}, context)
        except Exception:
            return True

    async def pull_events(
        self,
        queue_name: str,
        max_events: int = 10,
        wait_seconds: int = 0
    ) -> List[Event]:
        """Pull events from a queue"""
        queue = self.queues.get(queue_name)
        if not queue:
            return []

        events = []
        end_time = datetime.now() + timedelta(seconds=wait_seconds) if wait_seconds else datetime.now()

        while len(events) < max_events:
            if queue.events:
                event = queue.events.pop(0)
                if not event.expires_at or event.expires_at > datetime.now():
                    events.append(event)
            elif datetime.now() >= end_time:
                break
            else:
                await asyncio.sleep(0.1)

        return events

    def acknowledge(self, event_id: str):
        """Acknowledge event processing"""
        for event in self.event_store:
            if event.event_id == event_id:
                event.status = EventStatus.COMPLETED
                event.processed_at = datetime.now()
                break

    def reject(self, event_id: str, requeue: bool = True):
        """Reject event processing"""
        for event in self.event_store:
            if event.event_id == event_id:
                if requeue and event.retry_count < event.max_retries:
                    event.retry_count += 1
                    event.status = EventStatus.PENDING
                else:
                    event.status = EventStatus.DEAD_LETTER
                    self.dead_letter_events.append(event)
                break

    def replay_events(
        self,
        event_type: Optional[str] = None,
        source: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        subscription_id: Optional[str] = None
    ) -> List[Event]:
        """Replay historical events"""
        events = self.event_store

        if event_type:
            events = [e for e in events if self._matches_pattern(e.event_type, event_type)]

        if source:
            events = [e for e in events if e.source == source]

        if start_time:
            events = [e for e in events if e.created_at >= start_time]

        if end_time:
            events = [e for e in events if e.created_at <= end_time]

        # Re-deliver to subscription if specified
        if subscription_id and subscription_id in self.subscriptions:
            subscription = self.subscriptions[subscription_id]
            for event in events:
                asyncio.create_task(self._deliver_event(event, subscription))

        return events

    def get_dead_letter_events(
        self,
        limit: int = 100
    ) -> List[Event]:
        """Get events from dead letter queue"""
        return self.dead_letter_events[-limit:]

    def retry_dead_letter(self, event_id: str) -> bool:
        """Retry a dead letter event"""
        for i, event in enumerate(self.dead_letter_events):
            if event.event_id == event_id:
                event.retry_count = 0
                event.status = EventStatus.PENDING
                self.dead_letter_events.pop(i)
                self.event_store.append(event)

                # Re-deliver
                matching = self._find_matching_subscriptions(event.event_type)
                for subscription in matching:
                    if subscription.is_active:
                        asyncio.create_task(
                            self._deliver_event(event, subscription)
                        )
                return True
        return False

    def get_event(self, event_id: str) -> Optional[Event]:
        """Get event by ID"""
        for event in self.event_store:
            if event.event_id == event_id:
                return event
        return None

    def get_events_by_correlation(
        self,
        correlation_id: str
    ) -> List[Event]:
        """Get all events with same correlation ID"""
        return [
            e for e in self.event_store
            if e.correlation_id == correlation_id
        ]

    def get_event_chain(self, event_id: str) -> List[Event]:
        """Get chain of events (causation chain)"""
        chain = []
        current_id = event_id

        while current_id:
            event = self.get_event(current_id)
            if event:
                chain.append(event)
                current_id = event.causation_id
            else:
                break

        return list(reversed(chain))

    def get_subscriptions(
        self,
        subscriber_id: Optional[str] = None,
        event_type: Optional[str] = None
    ) -> List[Subscription]:
        """Get subscriptions with filters"""
        subscriptions = list(self.subscriptions.values())

        if subscriber_id:
            subscriptions = [s for s in subscriptions if s.subscriber_id == subscriber_id]

        if event_type:
            subscriptions = [
                s for s in subscriptions
                if any(self._matches_pattern(event_type, p) for p in s.event_types)
            ]

        return subscriptions

    def get_topics(self) -> List[Topic]:
        """Get all topics"""
        return list(self.topics.values())

    def get_queues(self) -> List[Queue]:
        """Get all queues"""
        return list(self.queues.values())

    def get_metrics(self) -> Dict[str, Any]:
        """Get event bus metrics"""
        return {
            **self.metrics,
            "topics_count": len(self.topics),
            "queues_count": len(self.queues),
            "subscriptions_count": len(self.subscriptions),
            "events_in_store": len(self.event_store),
            "processing_count": len(self.processing_events),
            "pending_events": len([e for e in self.event_store if e.status == EventStatus.PENDING])
        }

    def get_delivery_attempts(
        self,
        event_id: Optional[str] = None,
        subscription_id: Optional[str] = None,
        limit: int = 100
    ) -> List[DeliveryAttempt]:
        """Get delivery attempts"""
        attempts = self.delivery_attempts

        if event_id:
            attempts = [a for a in attempts if a.event_id == event_id]

        if subscription_id:
            attempts = [a for a in attempts if a.subscription_id == subscription_id]

        return attempts[-limit:]

    def cleanup_expired(self):
        """Clean up expired events"""
        now = datetime.now()

        # Remove expired events from store
        self.event_store = [
            e for e in self.event_store
            if not e.expires_at or e.expires_at > now
        ]

        # Remove expired events from queues
        for queue in self.queues.values():
            retention_limit = now - timedelta(hours=queue.retention_hours)
            queue.events = [
                e for e in queue.events
                if e.created_at > retention_limit
            ]


# Singleton instance
event_bus = EventBus()
