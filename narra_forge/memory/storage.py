"""
Storage backend for NARRA_FORGE V2 memory system
Uses SQLite with async support (aiosqlite)
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiosqlite


class MemoryStorage:
    """
    SQLite-based storage for memory systems.

    Features:
    - Async operations (aiosqlite)
    - JSON serialization for complex data
    - Automatic schema creation
    """

    def __init__(self, db_path: Path):
        """
        Initialize storage.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    async def initialize(self) -> None:
        """Initialize database schema"""
        async with aiosqlite.connect(self.db_path) as db:
            # Structural memory: Worlds
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS worlds (
                    world_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    genre TEXT,
                    reality_laws JSON,
                    boundaries JSON,
                    anomalies JSON,
                    core_conflict TEXT,
                    existential_theme TEXT,
                    description TEXT,
                    linked_worlds JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Structural memory: Characters
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS characters (
                    character_id TEXT PRIMARY KEY,
                    world_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    internal_trajectory JSON,
                    contradictions JSON,
                    cognitive_limits JSON,
                    evolution_capacity REAL,
                    archetype TEXT,
                    role TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (world_id) REFERENCES worlds(world_id)
                )
                """
            )

            # Semantic memory: Nodes (events, motifs, relationships)
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS semantic_nodes (
                    node_id TEXT PRIMARY KEY,
                    node_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    embedding BLOB,
                    connections JSON,
                    significance REAL DEFAULT 0.5,
                    timestamp_in_story INTEGER,
                    world_id TEXT,
                    metadata JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (world_id) REFERENCES worlds(world_id)
                )
                """
            )

            # Evolutionary memory: Change log
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS evolution_log (
                    entry_id TEXT PRIMARY KEY,
                    entity_id TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    change_type TEXT NOT NULL,
                    before_state JSON,
                    after_state JSON,
                    trigger TEXT,
                    significance REAL DEFAULT 0.5,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Production jobs
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS production_jobs (
                    job_id TEXT PRIMARY KEY,
                    brief JSON NOT NULL,
                    status TEXT NOT NULL,
                    current_stage TEXT,
                    world_id TEXT,
                    tokens_used INTEGER DEFAULT 0,
                    cost_usd REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    output JSON,
                    error TEXT,
                    FOREIGN KEY (world_id) REFERENCES worlds(world_id)
                )
                """
            )

            # Create indexes
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_characters_world ON characters(world_id)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_semantic_world ON semantic_nodes(world_id)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_semantic_type ON semantic_nodes(node_type)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_evolution_entity ON evolution_log(entity_id)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_jobs_status ON production_jobs(status)"
            )

            await db.commit()

    async def save_world(self, world: Dict[str, Any]) -> None:
        """Save or update world"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO worlds
                (world_id, name, genre, reality_laws, boundaries, anomalies,
                 core_conflict, existential_theme, description, linked_worlds, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (
                    world["world_id"],
                    world["name"],
                    world.get("genre"),
                    json.dumps(world.get("reality_laws")),
                    json.dumps(world.get("boundaries")),
                    json.dumps(world.get("anomalies")),
                    world.get("core_conflict"),
                    world.get("existential_theme"),
                    world.get("description"),
                    json.dumps(world.get("linked_worlds", [])),
                ),
            )
            await db.commit()

    async def get_world(self, world_id: str) -> Optional[Dict[str, Any]]:
        """Get world by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM worlds WHERE world_id = ?", (world_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                return None

    async def save_character(self, character: Dict[str, Any]) -> None:
        """Save or update character"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO characters
                (character_id, world_id, name, internal_trajectory, contradictions,
                 cognitive_limits, evolution_capacity, archetype, role, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (
                    character["character_id"],
                    character["world_id"],
                    character["name"],
                    json.dumps(character.get("internal_trajectory")),
                    json.dumps(character.get("contradictions")),
                    json.dumps(character.get("cognitive_limits")),
                    character.get("evolution_capacity"),
                    character.get("archetype"),
                    character.get("role"),
                ),
            )
            await db.commit()

    async def get_characters_by_world(self, world_id: str) -> List[Dict[str, Any]]:
        """Get all characters in a world"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM characters WHERE world_id = ?", (world_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def save_semantic_node(self, node: Dict[str, Any]) -> None:
        """Save semantic node"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO semantic_nodes
                (node_id, node_type, content, embedding, connections,
                 significance, timestamp_in_story, world_id, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    node["node_id"],
                    node["node_type"],
                    node["content"],
                    node.get("embedding"),  # BLOB
                    json.dumps(node.get("connections", [])),
                    node.get("significance", 0.5),
                    node.get("timestamp_in_story"),
                    node.get("world_id"),
                    json.dumps(node.get("metadata", {})),
                ),
            )
            await db.commit()

    async def get_semantic_nodes_by_world(
        self, world_id: str, node_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get semantic nodes for a world"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if node_type:
                query = "SELECT * FROM semantic_nodes WHERE world_id = ? AND node_type = ?"
                params = (world_id, node_type)
            else:
                query = "SELECT * FROM semantic_nodes WHERE world_id = ?"
                params = (world_id,)

            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def save_evolution_entry(self, entry: Dict[str, Any]) -> None:
        """Save evolution entry"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO evolution_log
                (entry_id, entity_id, entity_type, change_type,
                 before_state, after_state, trigger, significance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry["entry_id"],
                    entry["entity_id"],
                    entry["entity_type"],
                    entry["change_type"],
                    json.dumps(entry.get("before_state")),
                    json.dumps(entry.get("after_state")),
                    entry.get("trigger"),
                    entry.get("significance", 0.5),
                ),
            )
            await db.commit()

    async def get_evolution_history(
        self, entity_id: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get evolution history for entity"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """
                SELECT * FROM evolution_log
                WHERE entity_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (entity_id, limit),
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def save_job(self, job: Dict[str, Any]) -> None:
        """Save or update production job"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO production_jobs
                (job_id, brief, status, current_stage, world_id,
                 tokens_used, cost_usd, started_at, completed_at, output, error)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job["job_id"],
                    json.dumps(job.get("brief")),
                    job["status"],
                    job.get("current_stage"),
                    job.get("world_id"),
                    job.get("tokens_used", 0),
                    job.get("cost_usd", 0.0),
                    job.get("started_at"),
                    job.get("completed_at"),
                    json.dumps(job.get("output")),
                    job.get("error"),
                ),
            )
            await db.commit()

    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM production_jobs WHERE job_id = ?", (job_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                return None

    async def list_jobs(
        self, status: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List production jobs"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if status:
                query = """
                    SELECT * FROM production_jobs
                    WHERE status = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """
                params = (status, limit)
            else:
                query = """
                    SELECT * FROM production_jobs
                    ORDER BY created_at DESC
                    LIMIT ?
                """
                params = (limit,)

            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
