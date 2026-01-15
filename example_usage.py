"""
NARRA_FORGE - Example Usage
Demonstrates how to use the narrative generation system.
"""
import asyncio
import os
from pathlib import Path

from narra_forge.core.config import get_default_config
from narra_forge.core.orchestrator import NarrativeOrchestrator
from narra_forge.core.types import PipelineStage

# Import agents
from narra_forge.agents.brief_interpreter import BriefInterpreterAgent
from narra_forge.agents.world_architect import WorldArchitectAgent
from narra_forge.agents.character_architect import CharacterArchitectAgent

# Import model backends
from narra_forge.models.backend import ModelOrchestrator
from narra_forge.models.anthropic_backend import AnthropicBackend


async def main():
    """
    Main execution function.
    Demonstrates complete narrative generation pipeline.
    """

    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║                    NARRA_FORGE                            ║
    ║                                                           ║
    ║        Autonomous Multi-World Narrative System            ║
    ║             of Absolute Publishing Class                  ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    # 1. Load configuration
    print("[1/5] Loading configuration...")
    config = get_default_config()

    # Ensure API keys are set
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("WARNING: ANTHROPIC_API_KEY not set in environment")
        print("Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        return

    # 2. Initialize model backends
    print("[2/5] Initializing model backends...")

    backends = {}

    # Initialize Anthropic backends
    for model_name, model_config in config.models.items():
        if model_config.provider == "anthropic":
            backends[model_name] = AnthropicBackend(model_config.__dict__)

    model_orchestrator = ModelOrchestrator(
        backends=backends,
        default=config.default_model
    )

    # 3. Initialize orchestrator
    print("[3/5] Initializing orchestrator...")
    orchestrator = NarrativeOrchestrator(config)
    orchestrator.model_orchestrator = model_orchestrator

    # 4. Register agents for each pipeline stage
    print("[4/5] Registering agents...")

    memory_system = orchestrator.memory_system

    # Stage 1: Brief Interpretation
    brief_agent = BriefInterpreterAgent(
        name="BriefInterpreter",
        model_orchestrator=model_orchestrator,
        memory_system=memory_system,
        config={"preferred_model": "claude-sonnet"}
    )
    orchestrator.register_agent(PipelineStage.BRIEF_INTERPRETATION, brief_agent)

    # Stage 2: World Architecture
    world_agent = WorldArchitectAgent(
        name="WorldArchitect",
        model_orchestrator=model_orchestrator,
        memory_system=memory_system,
        config={"preferred_model": "claude-opus", "temperature": 0.8}
    )
    orchestrator.register_agent(PipelineStage.WORLD_ARCHITECTURE, world_agent)

    # Stage 3: Character Architecture
    character_agent = CharacterArchitectAgent(
        name="CharacterArchitect",
        model_orchestrator=model_orchestrator,
        memory_system=memory_system,
        config={"preferred_model": "claude-opus", "temperature": 0.8}
    )
    orchestrator.register_agent(PipelineStage.CHARACTER_ARCHITECTURE, character_agent)

    # NOTE: Stages 4-10 would be registered here in complete implementation
    # For demonstration, we'll run partial pipeline

    # 5. Execute narrative production
    print("[5/5] Ready for narrative production\n")

    # Example request
    user_request = """
Stwórz mroczną opowieść science fiction o ostatnim pilocie
transportowym w umierającym systemie gwiezdnym, który odkrywa,
że jego ładunek zawiera coś, co może ocalić lub zniszczyć
to, co pozostało z ludzkości.

Forma: opowiadanie (około 5000 słów)
Ton: mroczny, filozoficzny
Temat: samotność, odpowiedzialność, cena przetrwania
    """

    print("User Request:")
    print(user_request)
    print("\n" + "="*60 + "\n")

    # Run production
    result = await orchestrator.produce_narrative(user_request)

    # Display results
    if result["success"]:
        print("\n✓ PRODUCTION SUCCESSFUL\n")
        print(f"Project ID: {result['project_id']}")
        print(f"Duration: {result['duration_seconds']:.2f}s")

        # Display metadata
        if "metadata" in result:
            metadata = result["metadata"]

            if "brief" in metadata:
                brief = metadata["brief"]
                print(f"\nForm: {brief.form.value}")
                print(f"Genre: {brief.genre.value}")
                print(f"World Scale: {brief.world_scale}")

            if "world" in metadata:
                world = metadata["world"]
                print(f"\nWorld: {world.name}")
                print(f"Theme: {world.existential_theme}")

            if "characters" in metadata:
                characters = metadata["characters"]
                print(f"\nCharacters: {len(characters)}")
                for char in characters:
                    print(f"  - {char.name}: {char.internal_trajectory}")

    else:
        print("\n❌ PRODUCTION FAILED\n")
        print(f"Error: {result.get('error')}")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
