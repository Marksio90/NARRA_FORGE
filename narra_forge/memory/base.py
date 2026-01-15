"""
Base memory system for NARRA_FORGE.
Implements triple memory architecture: structural, semantic, evolutionary.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import sqlite3
from pathlib import Path


@dataclass
class MemoryEntry:
    """Base memory entry."""
    entry_id: str
    memory_type: str  # "structural", "semantic", "evolutionary"
    world_id: str
    content: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]


class MemorySystem(ABC):
    """Abstract base for memory systems."""

    @abstractmethod
    def store(self, entry: MemoryEntry) -> bool:
        """Store a memory entry."""
        pass

    @abstractmethod
    def retrieve(self, entry_id: str) -> Optional[MemoryEntry]:
        """Retrieve specific entry."""
        pass

    @abstractmethod
    def query(self, filters: Dict[str, Any]) -> List[MemoryEntry]:
        """Query entries by filters."""
        pass

    @abstractmethod
    def update(self, entry_id: str, content: Dict[str, Any]) -> bool:
        """Update existing entry."""
        pass

    @abstractmethod
    def delete(self, entry_id: str) -> bool:
        """Delete entry."""
        pass


class SQLiteMemorySystem(MemorySystem):
    """
    SQLite-based memory implementation.
    Fast, persistent, queryable.
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Main memory table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_entries (
                entry_id TEXT PRIMARY KEY,
                memory_type TEXT NOT NULL,
                world_id TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                metadata TEXT
            )
        """)

        # Indexes for fast queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_world_type
            ON memory_entries(world_id, memory_type)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created
            ON memory_entries(created_at)
        """)

        conn.commit()
        conn.close()

    def store(self, entry: MemoryEntry) -> bool:
        """Store memory entry."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO memory_entries
                (entry_id, memory_type, world_id, content, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.entry_id,
                entry.memory_type,
                entry.world_id,
                json.dumps(entry.content),
                entry.created_at.isoformat(),
                entry.updated_at.isoformat(),
                json.dumps(entry.metadata)
            ))

            conn.commit()
            return True

        except Exception as e:
            print(f"Error storing memory: {e}")
            return False

        finally:
            conn.close()

    def retrieve(self, entry_id: str) -> Optional[MemoryEntry]:
        """Retrieve specific entry."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM memory_entries WHERE entry_id = ?
        """, (entry_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return MemoryEntry(
            entry_id=row[0],
            memory_type=row[1],
            world_id=row[2],
            content=json.loads(row[3]),
            created_at=datetime.fromisoformat(row[4]),
            updated_at=datetime.fromisoformat(row[5]),
            metadata=json.loads(row[6]) if row[6] else {}
        )

    def query(self, filters: Dict[str, Any]) -> List[MemoryEntry]:
        """Query entries by filters."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM memory_entries WHERE 1=1"
        params = []

        if "world_id" in filters:
            query += " AND world_id = ?"
            params.append(filters["world_id"])

        if "memory_type" in filters:
            query += " AND memory_type = ?"
            params.append(filters["memory_type"])

        if "limit" in filters:
            query += f" LIMIT {filters['limit']}"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        entries = []
        for row in rows:
            entries.append(MemoryEntry(
                entry_id=row[0],
                memory_type=row[1],
                world_id=row[2],
                content=json.loads(row[3]),
                created_at=datetime.fromisoformat(row[4]),
                updated_at=datetime.fromisoformat(row[5]),
                metadata=json.loads(row[6]) if row[6] else {}
            ))

        return entries

    def update(self, entry_id: str, content: Dict[str, Any]) -> bool:
        """Update existing entry."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE memory_entries
                SET content = ?, updated_at = ?
                WHERE entry_id = ?
            """, (
                json.dumps(content),
                datetime.now().isoformat(),
                entry_id
            ))

            conn.commit()
            return cursor.rowcount > 0

        except Exception as e:
            print(f"Error updating memory: {e}")
            return False

        finally:
            conn.close()

    def delete(self, entry_id: str) -> bool:
        """Delete entry."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                DELETE FROM memory_entries WHERE entry_id = ?
            """, (entry_id,))

            conn.commit()
            return cursor.rowcount > 0

        except Exception as e:
            print(f"Error deleting memory: {e}")
            return False

        finally:
            conn.close()

    def get_world_summary(self, world_id: str) -> Dict[str, Any]:
        """Get complete summary of a world's memory."""
        structural = self.query({"world_id": world_id, "memory_type": "structural"})
        semantic = self.query({"world_id": world_id, "memory_type": "semantic"})
        evolutionary = self.query({"world_id": world_id, "memory_type": "evolutionary"})

        return {
            "world_id": world_id,
            "structural_count": len(structural),
            "semantic_count": len(semantic),
            "evolutionary_count": len(evolutionary),
            "total_entries": len(structural) + len(semantic) + len(evolutionary)
        }
