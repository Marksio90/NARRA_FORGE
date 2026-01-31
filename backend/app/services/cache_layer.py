"""
Caching Layer - NarraForge 3.0 Phase 5
Multi-tier caching system for optimal performance
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, TypeVar, Generic
from enum import Enum
from datetime import datetime, timedelta
import uuid
import hashlib
import json
import asyncio
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CacheLevel(Enum):
    """Cache hierarchy levels"""
    L1_MEMORY = "l1_memory"  # Fastest, smallest
    L2_LOCAL = "l2_local"  # Fast, larger
    L3_DISTRIBUTED = "l3_distributed"  # Slower, largest


class EvictionPolicy(Enum):
    """Cache eviction policies"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    TTL = "ttl"  # Time To Live only
    RANDOM = "random"  # Random eviction


class CacheStrategy(Enum):
    """Caching strategies"""
    CACHE_ASIDE = "cache_aside"  # Application manages cache
    READ_THROUGH = "read_through"  # Cache handles reads
    WRITE_THROUGH = "write_through"  # Cache handles writes
    WRITE_BEHIND = "write_behind"  # Async write to store
    REFRESH_AHEAD = "refresh_ahead"  # Proactive refresh


@dataclass
class CacheEntry:
    """Single cache entry"""
    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    access_count: int = 0
    size_bytes: int = 0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "created_at": self.created_at.isoformat(),
            "accessed_at": self.accessed_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "access_count": self.access_count,
            "size_bytes": self.size_bytes,
            "tags": self.tags
        }


@dataclass
class CacheConfig:
    """Cache configuration"""
    max_size: int = 1000  # Max entries
    max_memory_mb: int = 100  # Max memory in MB
    default_ttl_seconds: int = 300  # Default TTL
    eviction_policy: EvictionPolicy = EvictionPolicy.LRU
    strategy: CacheStrategy = CacheStrategy.CACHE_ASIDE
    enable_stats: bool = True
    enable_compression: bool = False
    compression_threshold_bytes: int = 1024

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_size": self.max_size,
            "max_memory_mb": self.max_memory_mb,
            "default_ttl_seconds": self.default_ttl_seconds,
            "eviction_policy": self.eviction_policy.value,
            "strategy": self.strategy.value
        }


@dataclass
class CacheStats:
    """Cache statistics"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    expirations: int = 0
    writes: int = 0
    deletes: int = 0
    current_size: int = 0
    current_memory_bytes: int = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "expirations": self.expirations,
            "writes": self.writes,
            "deletes": self.deletes,
            "current_size": self.current_size,
            "current_memory_bytes": self.current_memory_bytes,
            "hit_rate": self.hit_rate
        }


@dataclass
class CacheNamespace:
    """Isolated cache namespace"""
    name: str
    config: CacheConfig
    entries: Dict[str, CacheEntry] = field(default_factory=dict)
    stats: CacheStats = field(default_factory=CacheStats)
    access_order: List[str] = field(default_factory=list)  # For LRU
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "config": self.config.to_dict(),
            "stats": self.stats.to_dict(),
            "entries_count": len(self.entries),
            "created_at": self.created_at.isoformat()
        }


class LRUCache(Generic[T]):
    """LRU Cache implementation"""

    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self._cache: OrderedDict[str, T] = OrderedDict()

    def get(self, key: str) -> Optional[T]:
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def put(self, key: str, value: T):
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = value

        while len(self._cache) > self.max_size:
            self._cache.popitem(last=False)

    def delete(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self):
        self._cache.clear()

    def __len__(self) -> int:
        return len(self._cache)

    def keys(self) -> List[str]:
        return list(self._cache.keys())


# Cache key patterns for NarraForge
CACHE_PATTERNS: Dict[str, Dict[str, Any]] = {
    "project": {
        "pattern": "project:{project_id}",
        "ttl": 3600,
        "tags": ["project"]
    },
    "chapter": {
        "pattern": "chapter:{project_id}:{chapter_id}",
        "ttl": 1800,
        "tags": ["chapter", "content"]
    },
    "character": {
        "pattern": "character:{project_id}:{character_id}",
        "ttl": 3600,
        "tags": ["character"]
    },
    "cover": {
        "pattern": "cover:{project_id}:{variant}",
        "ttl": 7200,
        "tags": ["cover", "image"]
    },
    "illustration": {
        "pattern": "illustration:{project_id}:{illustration_id}",
        "ttl": 7200,
        "tags": ["illustration", "image"]
    },
    "audiobook_segment": {
        "pattern": "audio:{project_id}:{segment_id}",
        "ttl": 3600,
        "tags": ["audio", "audiobook"]
    },
    "translation": {
        "pattern": "translation:{project_id}:{language}:{chapter_id}",
        "ttl": 3600,
        "tags": ["translation"]
    },
    "analysis": {
        "pattern": "analysis:{type}:{project_id}",
        "ttl": 1800,
        "tags": ["analysis", "ai"]
    },
    "user_session": {
        "pattern": "session:{user_id}",
        "ttl": 7200,
        "tags": ["session", "user"]
    },
    "api_response": {
        "pattern": "api:{endpoint}:{hash}",
        "ttl": 300,
        "tags": ["api"]
    }
}


class CacheLayer:
    """
    Multi-tier Caching Layer for NarraForge

    Features:
    - Multi-level cache hierarchy (L1, L2, L3)
    - Multiple eviction policies (LRU, LFU, FIFO, TTL)
    - Cache namespaces for isolation
    - Tag-based invalidation
    - Pattern-based keys
    - Cache warming
    - Read-through and write-through support
    - Statistics and monitoring
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

        # Cache namespaces
        self.namespaces: Dict[str, CacheNamespace] = {}

        # L1 Cache (fast, in-memory, small)
        self.l1_cache: LRUCache[Any] = LRUCache(max_size=1000)

        # L2 Cache (larger, still in-memory)
        self.l2_cache: Dict[str, CacheEntry] = {}

        # L3 would typically be Redis/Memcached - simulated here
        self.l3_cache: Dict[str, CacheEntry] = {}

        # Global stats
        self.global_stats: CacheStats = CacheStats()

        # Cache patterns
        self.patterns = CACHE_PATTERNS

        # Loaders for read-through
        self.loaders: Dict[str, Callable] = {}

        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None

        self._create_default_namespaces()
        self._initialized = True

    def _create_default_namespaces(self):
        """Create default cache namespaces"""
        default_namespaces = [
            ("projects", CacheConfig(max_size=500, default_ttl_seconds=3600)),
            ("chapters", CacheConfig(max_size=2000, default_ttl_seconds=1800)),
            ("characters", CacheConfig(max_size=1000, default_ttl_seconds=3600)),
            ("media", CacheConfig(max_size=500, default_ttl_seconds=7200, max_memory_mb=500)),
            ("translations", CacheConfig(max_size=1000, default_ttl_seconds=3600)),
            ("analysis", CacheConfig(max_size=500, default_ttl_seconds=1800)),
            ("sessions", CacheConfig(max_size=10000, default_ttl_seconds=7200)),
            ("api", CacheConfig(max_size=5000, default_ttl_seconds=300)),
        ]

        for name, config in default_namespaces:
            self.create_namespace(name, config)

    def create_namespace(
        self,
        name: str,
        config: Optional[CacheConfig] = None
    ) -> CacheNamespace:
        """Create a cache namespace"""
        if config is None:
            config = CacheConfig()

        namespace = CacheNamespace(
            name=name,
            config=config
        )

        self.namespaces[name] = namespace
        return namespace

    def get_namespace(self, name: str) -> Optional[CacheNamespace]:
        """Get namespace by name"""
        return self.namespaces.get(name)

    def _generate_key(
        self,
        pattern_name: str,
        **kwargs
    ) -> str:
        """Generate cache key from pattern"""
        if pattern_name in self.patterns:
            pattern = self.patterns[pattern_name]["pattern"]
            return pattern.format(**kwargs)

        # Fallback to simple key
        return f"{pattern_name}:" + ":".join(str(v) for v in kwargs.values())

    def _estimate_size(self, value: Any) -> int:
        """Estimate size of value in bytes"""
        try:
            return len(json.dumps(value).encode('utf-8'))
        except (TypeError, ValueError):
            return len(str(value).encode('utf-8'))

    def get(
        self,
        key: str,
        namespace: str = "default",
        level: Optional[CacheLevel] = None
    ) -> Optional[Any]:
        """Get value from cache"""
        # Try L1 first
        if level is None or level == CacheLevel.L1_MEMORY:
            value = self.l1_cache.get(key)
            if value is not None:
                self.global_stats.hits += 1
                return value

        # Try namespace cache (L2)
        if namespace in self.namespaces:
            ns = self.namespaces[namespace]
            entry = ns.entries.get(key)

            if entry:
                if entry.is_expired():
                    self._evict_entry(ns, key)
                    ns.stats.expirations += 1
                else:
                    entry.accessed_at = datetime.now()
                    entry.access_count += 1
                    ns.stats.hits += 1
                    self.global_stats.hits += 1

                    # Promote to L1
                    self.l1_cache.put(key, entry.value)

                    return entry.value

        # Try L3
        if level is None or level == CacheLevel.L3_DISTRIBUTED:
            entry = self.l3_cache.get(key)
            if entry and not entry.is_expired():
                self.global_stats.hits += 1

                # Promote to L1 and L2
                self.l1_cache.put(key, entry.value)

                return entry.value

        self.global_stats.misses += 1
        if namespace in self.namespaces:
            self.namespaces[namespace].stats.misses += 1

        return None

    async def get_or_load(
        self,
        key: str,
        loader: Callable[[], Any],
        namespace: str = "default",
        ttl_seconds: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> Any:
        """Get from cache or load if missing"""
        value = self.get(key, namespace)

        if value is not None:
            return value

        # Load value
        if asyncio.iscoroutinefunction(loader):
            value = await loader()
        else:
            value = loader()

        # Store in cache
        self.set(key, value, namespace, ttl_seconds, tags)

        return value

    def set(
        self,
        key: str,
        value: Any,
        namespace: str = "default",
        ttl_seconds: Optional[int] = None,
        tags: Optional[List[str]] = None,
        level: CacheLevel = CacheLevel.L2_LOCAL
    ):
        """Set value in cache"""
        ns = self.namespaces.get(namespace)
        if not ns:
            ns = self.create_namespace(namespace)

        # Calculate TTL
        if ttl_seconds is None:
            ttl_seconds = ns.config.default_ttl_seconds

        expires_at = datetime.now() + timedelta(seconds=ttl_seconds) if ttl_seconds > 0 else None

        # Create entry
        entry = CacheEntry(
            key=key,
            value=value,
            expires_at=expires_at,
            size_bytes=self._estimate_size(value),
            tags=tags or []
        )

        # Check capacity and evict if needed
        while len(ns.entries) >= ns.config.max_size:
            self._evict_one(ns)

        # Store in namespace
        ns.entries[key] = entry
        ns.stats.writes += 1
        ns.stats.current_size = len(ns.entries)
        ns.stats.current_memory_bytes += entry.size_bytes

        self.global_stats.writes += 1

        # Update L1
        self.l1_cache.put(key, value)

        # Update L3 if specified
        if level == CacheLevel.L3_DISTRIBUTED:
            self.l3_cache[key] = entry

        logger.debug(f"Cached: {key} in {namespace} (TTL: {ttl_seconds}s)")

    def delete(
        self,
        key: str,
        namespace: str = "default"
    ) -> bool:
        """Delete value from cache"""
        deleted = False

        # Delete from L1
        self.l1_cache.delete(key)

        # Delete from namespace
        if namespace in self.namespaces:
            ns = self.namespaces[namespace]
            if key in ns.entries:
                entry = ns.entries.pop(key)
                ns.stats.deletes += 1
                ns.stats.current_size = len(ns.entries)
                ns.stats.current_memory_bytes -= entry.size_bytes
                deleted = True

        # Delete from L3
        if key in self.l3_cache:
            del self.l3_cache[key]
            deleted = True

        if deleted:
            self.global_stats.deletes += 1

        return deleted

    def invalidate_by_tags(
        self,
        tags: List[str],
        namespace: Optional[str] = None
    ) -> int:
        """Invalidate all entries with matching tags"""
        count = 0

        namespaces = [self.namespaces[namespace]] if namespace else self.namespaces.values()

        for ns in namespaces:
            keys_to_delete = []
            for key, entry in ns.entries.items():
                if any(tag in entry.tags for tag in tags):
                    keys_to_delete.append(key)

            for key in keys_to_delete:
                self.delete(key, ns.name)
                count += 1

        logger.info(f"Invalidated {count} entries by tags: {tags}")
        return count

    def invalidate_by_pattern(
        self,
        pattern: str,
        namespace: Optional[str] = None
    ) -> int:
        """Invalidate entries matching key pattern"""
        count = 0

        namespaces = [self.namespaces[namespace]] if namespace else self.namespaces.values()

        for ns in namespaces:
            keys_to_delete = []
            for key in ns.entries.keys():
                if self._matches_pattern(key, pattern):
                    keys_to_delete.append(key)

            for key in keys_to_delete:
                self.delete(key, ns.name)
                count += 1

        logger.info(f"Invalidated {count} entries by pattern: {pattern}")
        return count

    def _matches_pattern(self, key: str, pattern: str) -> bool:
        """Check if key matches pattern (supports * wildcard)"""
        import fnmatch
        return fnmatch.fnmatch(key, pattern)

    def _evict_one(self, namespace: CacheNamespace):
        """Evict one entry based on policy"""
        if not namespace.entries:
            return

        policy = namespace.config.eviction_policy

        if policy == EvictionPolicy.LRU:
            # Find least recently used
            oldest_key = min(
                namespace.entries.keys(),
                key=lambda k: namespace.entries[k].accessed_at
            )
        elif policy == EvictionPolicy.LFU:
            # Find least frequently used
            oldest_key = min(
                namespace.entries.keys(),
                key=lambda k: namespace.entries[k].access_count
            )
        elif policy == EvictionPolicy.FIFO:
            # Find oldest
            oldest_key = min(
                namespace.entries.keys(),
                key=lambda k: namespace.entries[k].created_at
            )
        elif policy == EvictionPolicy.TTL:
            # Find nearest to expiration
            oldest_key = min(
                namespace.entries.keys(),
                key=lambda k: namespace.entries[k].expires_at or datetime.max
            )
        else:
            # Random
            import random
            oldest_key = random.choice(list(namespace.entries.keys()))

        self._evict_entry(namespace, oldest_key)

    def _evict_entry(self, namespace: CacheNamespace, key: str):
        """Evict specific entry"""
        if key in namespace.entries:
            entry = namespace.entries.pop(key)
            namespace.stats.evictions += 1
            namespace.stats.current_size = len(namespace.entries)
            namespace.stats.current_memory_bytes -= entry.size_bytes

            self.global_stats.evictions += 1
            self.l1_cache.delete(key)

    def clear(self, namespace: Optional[str] = None):
        """Clear cache"""
        if namespace:
            if namespace in self.namespaces:
                ns = self.namespaces[namespace]
                ns.entries.clear()
                ns.stats = CacheStats()
        else:
            for ns in self.namespaces.values():
                ns.entries.clear()
                ns.stats = CacheStats()
            self.l1_cache.clear()
            self.l3_cache.clear()
            self.global_stats = CacheStats()

    def warm(
        self,
        items: List[Dict[str, Any]],
        namespace: str = "default"
    ):
        """Warm cache with items"""
        for item in items:
            key = item.get("key")
            value = item.get("value")
            ttl = item.get("ttl_seconds")
            tags = item.get("tags", [])

            if key and value:
                self.set(key, value, namespace, ttl, tags)

        logger.info(f"Warmed {len(items)} items in {namespace}")

    async def refresh(
        self,
        key: str,
        loader: Callable[[], Any],
        namespace: str = "default"
    ) -> Any:
        """Refresh cached value"""
        if asyncio.iscoroutinefunction(loader):
            value = await loader()
        else:
            value = loader()

        # Get existing entry for TTL
        ns = self.namespaces.get(namespace)
        ttl = ns.config.default_ttl_seconds if ns else 300
        tags = []

        if ns and key in ns.entries:
            old_entry = ns.entries[key]
            tags = old_entry.tags
            if old_entry.expires_at:
                ttl = (old_entry.expires_at - old_entry.created_at).seconds

        self.set(key, value, namespace, ttl, tags)
        return value

    def register_loader(
        self,
        pattern_name: str,
        loader: Callable
    ):
        """Register loader for read-through caching"""
        self.loaders[pattern_name] = loader

    def get_stats(
        self,
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get cache statistics"""
        if namespace:
            ns = self.namespaces.get(namespace)
            return ns.stats.to_dict() if ns else {}

        return {
            "global": self.global_stats.to_dict(),
            "namespaces": {
                name: ns.stats.to_dict()
                for name, ns in self.namespaces.items()
            },
            "l1_size": len(self.l1_cache),
            "l3_size": len(self.l3_cache)
        }

    def get_keys(
        self,
        namespace: str = "default",
        pattern: Optional[str] = None
    ) -> List[str]:
        """Get all keys in namespace"""
        ns = self.namespaces.get(namespace)
        if not ns:
            return []

        keys = list(ns.entries.keys())

        if pattern:
            keys = [k for k in keys if self._matches_pattern(k, pattern)]

        return keys

    def get_entries(
        self,
        namespace: str = "default",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get cache entries for inspection"""
        ns = self.namespaces.get(namespace)
        if not ns:
            return []

        return [
            entry.to_dict()
            for entry in list(ns.entries.values())[:limit]
        ]

    def get_namespaces(self) -> List[Dict[str, Any]]:
        """Get all namespaces"""
        return [ns.to_dict() for ns in self.namespaces.values()]

    async def cleanup(self):
        """Clean up expired entries"""
        total_cleaned = 0

        for ns in self.namespaces.values():
            keys_to_delete = [
                key for key, entry in ns.entries.items()
                if entry.is_expired()
            ]

            for key in keys_to_delete:
                self._evict_entry(ns, key)
                ns.stats.expirations += 1
                total_cleaned += 1

        # Clean L3
        keys_to_delete = [
            key for key, entry in self.l3_cache.items()
            if entry.is_expired()
        ]
        for key in keys_to_delete:
            del self.l3_cache[key]
            total_cleaned += 1

        logger.info(f"Cleaned up {total_cleaned} expired entries")
        return total_cleaned


# Singleton instance
cache_layer = CacheLayer()
