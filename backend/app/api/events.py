"""
Event Bus API - NarraForge 3.0 Phase 5
Endpoints for event-driven messaging and pub/sub
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.services.event_bus import (
    event_bus,
    EventPriority,
    DeliveryMode,
    NARRAFORGE_EVENTS
)

router = APIRouter(prefix="/events")


# Request/Response Models
class PublishEventRequest(BaseModel):
    """Request to publish an event"""
    event_type: str
    source: str
    data: Dict[str, Any]
    priority: str = "normal"
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    ttl_seconds: Optional[int] = None


class EventResponse(BaseModel):
    """Event response"""
    success: bool
    event: Optional[Dict[str, Any]] = None
    message: str = ""


class TopicCreateRequest(BaseModel):
    """Request to create topic"""
    name: str
    description: str = ""
    retention_hours: int = 24
    partitions: int = 1


class TopicResponse(BaseModel):
    """Topic response"""
    success: bool
    topic: Optional[Dict[str, Any]] = None
    message: str = ""


class QueueCreateRequest(BaseModel):
    """Request to create queue"""
    name: str
    max_size: int = 10000
    retention_hours: int = 24
    dead_letter_queue: Optional[str] = None


class QueueResponse(BaseModel):
    """Queue response"""
    success: bool
    queue: Optional[Dict[str, Any]] = None
    message: str = ""


class SubscribeRequest(BaseModel):
    """Request to subscribe to events"""
    event_types: List[str]
    subscriber_id: str
    filter_expression: Optional[str] = None
    delivery_mode: str = "at_least_once"
    max_concurrent: int = 10


class SubscriptionResponse(BaseModel):
    """Subscription response"""
    success: bool
    subscription: Optional[Dict[str, Any]] = None
    message: str = ""


# Endpoints

@router.get("/health")
async def event_bus_health():
    """Get event bus health status"""
    metrics = event_bus.get_metrics()
    return {
        "success": True,
        "status": "healthy",
        "metrics": metrics
    }


@router.post("/publish", response_model=EventResponse)
async def publish_event(request: PublishEventRequest):
    """
    Publish an event

    Events are delivered to all matching subscribers
    and stored for replay capability.
    """
    try:
        priority = EventPriority[request.priority.upper()]

        event = await event_bus.publish(
            event_type=request.event_type,
            source=request.source,
            data=request.data,
            priority=priority,
            correlation_id=request.correlation_id,
            causation_id=request.causation_id,
            ttl_seconds=request.ttl_seconds
        )

        return EventResponse(
            success=True,
            event=event.to_dict(),
            message=f"Event published: {request.event_type}"
        )

    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid priority: {request.priority}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/{event_id}")
async def get_event(event_id: str):
    """Get event by ID"""
    try:
        event = event_bus.get_event(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        return {
            "success": True,
            "event": event.to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/correlation/{correlation_id}")
async def get_events_by_correlation(correlation_id: str):
    """Get all events with same correlation ID"""
    try:
        events = event_bus.get_events_by_correlation(correlation_id)
        return {
            "success": True,
            "events": [e.to_dict() for e in events],
            "count": len(events)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/{event_id}/chain")
async def get_event_chain(event_id: str):
    """Get chain of related events (causation chain)"""
    try:
        chain = event_bus.get_event_chain(event_id)
        return {
            "success": True,
            "chain": [e.to_dict() for e in chain],
            "count": len(chain)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/topics/create", response_model=TopicResponse)
async def create_topic(request: TopicCreateRequest):
    """Create a new topic"""
    try:
        topic = event_bus.create_topic(
            name=request.name,
            description=request.description,
            retention_hours=request.retention_hours,
            partitions=request.partitions
        )

        return TopicResponse(
            success=True,
            topic=topic.to_dict(),
            message="Topic created"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/topics")
async def get_topics():
    """Get all topics"""
    try:
        topics = event_bus.get_topics()
        return {
            "success": True,
            "topics": [t.to_dict() for t in topics],
            "count": len(topics)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/topics/{topic_name}")
async def get_topic(topic_name: str):
    """Get topic details"""
    try:
        topic = event_bus.get_topic(topic_name)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")

        return {
            "success": True,
            "topic": topic.to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/queues/create", response_model=QueueResponse)
async def create_queue(request: QueueCreateRequest):
    """Create a message queue"""
    try:
        queue = event_bus.create_queue(
            name=request.name,
            max_size=request.max_size,
            retention_hours=request.retention_hours,
            dead_letter_queue=request.dead_letter_queue
        )

        return QueueResponse(
            success=True,
            queue=queue.to_dict(),
            message="Queue created"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queues")
async def get_queues():
    """Get all queues"""
    try:
        queues = event_bus.get_queues()
        return {
            "success": True,
            "queues": [q.to_dict() for q in queues],
            "count": len(queues)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queues/{queue_name}/pull")
async def pull_events(
    queue_name: str,
    max_events: int = 10,
    wait_seconds: int = 0
):
    """Pull events from a queue"""
    try:
        events = await event_bus.pull_events(
            queue_name=queue_name,
            max_events=max_events,
            wait_seconds=wait_seconds
        )

        return {
            "success": True,
            "events": [e.to_dict() for e in events],
            "count": len(events)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subscriptions/create", response_model=SubscriptionResponse)
async def create_subscription(request: SubscribeRequest):
    """
    Subscribe to event types

    Supports wildcards like "book.*" for all book events.
    """
    try:
        delivery = DeliveryMode(request.delivery_mode)

        # Note: In production, handler would be a webhook or callback
        subscription = event_bus.subscribe(
            event_types=request.event_types,
            handler=None,  # Would be set up for actual delivery
            subscriber_id=request.subscriber_id,
            filter_expression=request.filter_expression,
            delivery_mode=delivery,
            max_concurrent=request.max_concurrent
        )

        return SubscriptionResponse(
            success=True,
            subscription=subscription.to_dict(),
            message=f"Subscribed to {len(request.event_types)} event types"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subscriptions")
async def get_subscriptions(
    subscriber_id: Optional[str] = None,
    event_type: Optional[str] = None
):
    """Get subscriptions"""
    try:
        subscriptions = event_bus.get_subscriptions(
            subscriber_id=subscriber_id,
            event_type=event_type
        )

        return {
            "success": True,
            "subscriptions": [s.to_dict() for s in subscriptions],
            "count": len(subscriptions)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/subscriptions/{subscription_id}")
async def unsubscribe(subscription_id: str):
    """Remove subscription"""
    try:
        event_bus.unsubscribe(subscription_id)
        return {
            "success": True,
            "message": "Unsubscribed successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/events/{event_id}/acknowledge")
async def acknowledge_event(event_id: str):
    """Acknowledge event processing"""
    try:
        event_bus.acknowledge(event_id)
        return {
            "success": True,
            "message": "Event acknowledged"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/events/{event_id}/reject")
async def reject_event(event_id: str, requeue: bool = True):
    """Reject event processing"""
    try:
        event_bus.reject(event_id, requeue)
        return {
            "success": True,
            "message": f"Event rejected" + (" and requeued" if requeue else "")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dead-letter")
async def get_dead_letter_events(limit: int = 100):
    """Get dead letter events"""
    try:
        events = event_bus.get_dead_letter_events(limit)
        return {
            "success": True,
            "events": [e.to_dict() for e in events],
            "count": len(events)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dead-letter/{event_id}/retry")
async def retry_dead_letter(event_id: str):
    """Retry a dead letter event"""
    try:
        success = event_bus.retry_dead_letter(event_id)
        if not success:
            raise HTTPException(status_code=404, detail="Event not found in dead letter queue")

        return {
            "success": True,
            "message": "Event requeued for retry"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/replay")
async def replay_events(
    event_type: Optional[str] = None,
    source: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    subscription_id: Optional[str] = None
):
    """Replay historical events"""
    try:
        start = datetime.fromisoformat(start_time) if start_time else None
        end = datetime.fromisoformat(end_time) if end_time else None

        events = event_bus.replay_events(
            event_type=event_type,
            source=source,
            start_time=start,
            end_time=end,
            subscription_id=subscription_id
        )

        return {
            "success": True,
            "events_replayed": len(events),
            "message": f"Replayed {len(events)} events"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/delivery-attempts")
async def get_delivery_attempts(
    event_id: Optional[str] = None,
    subscription_id: Optional[str] = None,
    limit: int = 100
):
    """Get delivery attempt history"""
    try:
        attempts = event_bus.get_delivery_attempts(
            event_id=event_id,
            subscription_id=subscription_id,
            limit=limit
        )

        return {
            "success": True,
            "attempts": [a.to_dict() for a in attempts],
            "count": len(attempts)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/event-types")
async def get_event_types():
    """Get predefined NarraForge event types"""
    return {
        "success": True,
        "event_types": NARRAFORGE_EVENTS
    }


@router.get("/metrics")
async def get_event_bus_metrics():
    """Get event bus metrics"""
    try:
        metrics = event_bus.get_metrics()
        return {
            "success": True,
            "metrics": metrics
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup")
async def cleanup_expired():
    """Clean up expired events"""
    try:
        event_bus.cleanup_expired()
        return {
            "success": True,
            "message": "Cleanup completed"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
