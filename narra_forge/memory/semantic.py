"""
Semantic Memory - LIVING CONTENT of stories

Stores:
- Events (what happens)
- Motifs (recurring themes)
- Relationships (between entities)
- Conflicts (tensions, drama)

This is the CONTENT layer - the substance of narratives.
"""
from typing import List, Optional
from uuid import uuid4

from narra_forge.core.types import SemanticNode
from narra_forge.memory.storage import MemoryStorage


class SemanticMemory:
    """
    Semantic memory system.

    Manages narrative content: events, motifs, relationships, conflicts.
    """

    def __init__(self, storage: MemoryStorage):
        """
        Initialize semantic memory.

        Args:
            storage: MemoryStorage instance
        """
        self.storage = storage

    async def add_node(
        self,
        node_type: str,
        content: str,
        world_id: Optional[str] = None,
        connections: Optional[List[str]] = None,
        significance: float = 0.5,
        timestamp_in_story: Optional[int] = None,
        metadata: Optional[dict] = None,
    ) -> SemanticNode:
        """
        Add a semantic node.

        Args:
            node_type: Type of node ("event", "motif", "relationship", "conflict")
            content: Content description
            world_id: World this belongs to (optional)
            connections: Connected node IDs
            significance: Importance (0.0-1.0)
            timestamp_in_story: Position in narrative
            metadata: Additional metadata

        Returns:
            SemanticNode instance
        """
        node = SemanticNode(
            node_id=f"node_{uuid4().hex[:12]}",
            node_type=node_type,
            content=content,
            connections=connections or [],
            significance=significance,
            timestamp_in_story=timestamp_in_story,
            world_id=world_id,
            metadata=metadata or {},
        )

        # Save to storage
        node_dict = {
            "node_id": node.node_id,
            "node_type": node.node_type,
            "content": node.content,
            "embedding": None,  # TODO: Add OpenAI embeddings
            "connections": node.connections,
            "significance": node.significance,
            "timestamp_in_story": node.timestamp_in_story,
            "world_id": node.world_id,
            "metadata": node.metadata,
        }
        await self.storage.save_semantic_node(node_dict)

        return node

    async def get_nodes_by_world(
        self, world_id: str, node_type: Optional[str] = None
    ) -> List[SemanticNode]:
        """
        Get semantic nodes for a world.

        Args:
            world_id: World ID
            node_type: Filter by type (optional)

        Returns:
            List of SemanticNode instances
        """
        import json

        node_dicts = await self.storage.get_semantic_nodes_by_world(world_id, node_type)

        nodes = []
        for nd in node_dicts:
            node = SemanticNode(
                node_id=nd["node_id"],
                node_type=nd["node_type"],
                content=nd["content"],
                embedding=None,  # TODO: Deserialize embedding
                connections=json.loads(nd["connections"]),
                significance=nd["significance"],
                timestamp_in_story=nd.get("timestamp_in_story"),
                world_id=nd.get("world_id"),
                metadata=json.loads(nd.get("metadata", "{}")),
            )
            nodes.append(node)

        return nodes

    async def add_event(
        self,
        content: str,
        world_id: str,
        timestamp_in_story: int,
        significance: float = 0.5,
        **kwargs,
    ) -> SemanticNode:
        """Add an event node"""
        return await self.add_node(
            node_type="event",
            content=content,
            world_id=world_id,
            timestamp_in_story=timestamp_in_story,
            significance=significance,
            **kwargs,
        )

    async def add_motif(
        self,
        content: str,
        world_id: str,
        significance: float = 0.5,
        **kwargs,
    ) -> SemanticNode:
        """Add a motif node"""
        return await self.add_node(
            node_type="motif",
            content=content,
            world_id=world_id,
            significance=significance,
            **kwargs,
        )

    async def add_relationship(
        self,
        content: str,
        world_id: str,
        connected_entities: List[str],
        significance: float = 0.5,
        **kwargs,
    ) -> SemanticNode:
        """Add a relationship node"""
        return await self.add_node(
            node_type="relationship",
            content=content,
            world_id=world_id,
            connections=connected_entities,
            significance=significance,
            **kwargs,
        )

    async def add_conflict(
        self,
        content: str,
        world_id: str,
        involved_entities: List[str],
        significance: float = 0.8,
        **kwargs,
    ) -> SemanticNode:
        """Add a conflict node"""
        return await self.add_node(
            node_type="conflict",
            content=content,
            world_id=world_id,
            connections=involved_entities,
            significance=significance,
            **kwargs,
        )

    async def connect_nodes(self, node_id_a: str, node_id_b: str) -> None:
        """
        Create a connection between two nodes.

        Args:
            node_id_a: First node
            node_id_b: Second node
        """
        # TODO: Implement bidirectional connection
        pass

    async def get_connected_nodes(self, node_id: str) -> List[SemanticNode]:
        """
        Get all nodes connected to this node.

        Args:
            node_id: Node ID

        Returns:
            List of connected nodes
        """
        # TODO: Implement traversal
        return []
