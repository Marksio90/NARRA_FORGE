"""
NarraForge Multi-Agent System

Professional AI agents for world-class book generation:
- World Builder Agent: Rich, consistent fictional worlds
- Character Creator Agent: Psychologically deep characters
- Plot Architect Agent: Compelling story structures
- Prose Writer Agent: Publication-quality prose
- Quality Control Agent: Professional editorial validation

Each agent is a specialist with domain expertise and advanced prompting techniques.
"""

from app.agents.world_builder_agent import WorldBuilderAgent
from app.agents.character_creator_agent import CharacterCreatorAgent
from app.agents.plot_architect_agent import PlotArchitectAgent
from app.agents.prose_writer_agent import ProseWriterAgent
from app.agents.quality_control_agent import QualityControlAgent

__all__ = [
    'WorldBuilderAgent',
    'CharacterCreatorAgent',
    'PlotArchitectAgent',
    'ProseWriterAgent',
    'QualityControlAgent',
]
