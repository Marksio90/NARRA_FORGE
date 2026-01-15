"""
AI Models module for NARRA_FORGE V2

ONLY OpenAI provider supported.

Usage:
    from narra_forge.models import OpenAIClient, ModelRouter

    client = OpenAIClient(config)
    router = ModelRouter(config, client)

    # Auto-routed generation
    text, call = await router.generate(
        prompt="...",
        stage=PipelineStage.SEQUENTIAL_GENERATION
    )
"""
from narra_forge.models.model_router import ModelRouter
from narra_forge.models.openai_client import OpenAIClient

__all__ = [
    "OpenAIClient",
    "ModelRouter",
]
