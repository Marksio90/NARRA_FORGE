"""
Shared fixtures for long-form testing.
"""

import pytest
from pathlib import Path
from typing import Dict, List

from narra_forge.core.types import (
    ProductionBrief,
    ProductionType,
    Genre,
)


# ═══════════════════════════════════════════
# PYTEST MARKERS
# ═══════════════════════════════════════════

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "mock: Mock tests (no API calls, free)"
    )
    config.addinivalue_line(
        "markers",
        "integration: Integration tests (real API calls, paid)"
    )
    config.addinivalue_line(
        "markers",
        "stress: Stress tests (extreme scenarios, expensive)"
    )
    config.addinivalue_line(
        "markers",
        "slow: Slow tests (>1 hour)"
    )


# ═══════════════════════════════════════════
# COST LIMIT HOOK
# ═══════════════════════════════════════════

def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--max-cost",
        action="store",
        default=None,
        type=float,
        help="Maximum cost (USD) for integration tests"
    )
    parser.addoption(
        "--profile-memory",
        action="store_true",
        default=False,
        help="Enable memory profiling"
    )


# ═══════════════════════════════════════════
# BRIEF FIXTURES
# ═══════════════════════════════════════════

@pytest.fixture
def brief_novella() -> ProductionBrief:
    """Novella brief (10k-40k words)."""
    return ProductionBrief(
        production_type=ProductionType.NOVELLA,
        genre=Genre.FANTASY,
        inspiration=(
            "A young alchemist discovers her master's dark secret: "
            "true immortality requires sacrificing the souls of others. "
            "She must choose between exposing him and losing everything, "
            "or becoming complicit in his crimes."
        ),
        target_word_count=25000,
    )


@pytest.fixture
def brief_novel() -> ProductionBrief:
    """Novel brief (40k-120k words)."""
    return ProductionBrief(
        production_type=ProductionType.NOVEL,
        genre=Genre.FANTASY,
        inspiration=(
            "In a world where magic is dying, a street thief discovers "
            "she's the last person born with the old power. Hunted by "
            "the Church that seeks to purge magic forever, and recruited "
            "by rebels who want to use her as a weapon, she must navigate "
            "political intrigue, betrayal, and the terrible cost of wielding "
            "a power that's slowly killing her."
        ),
        target_word_count=80000,
    )


@pytest.fixture
def brief_epic_saga() -> ProductionBrief:
    """Epic saga brief (120k+ words)."""
    return ProductionBrief(
        production_type=ProductionType.EPIC_SAGA,
        genre=Genre.SCIFI,
        inspiration=(
            "A thousand years after Earth's collapse, humanity lives in "
            "generation ships scattered across the void. When a derelict "
            "ship is discovered containing impossible technology, three "
            "rival factions—the Collective, the Free Worlds Alliance, and "
            "the Synthesis—race to claim it. But the technology awakens "
            "something ancient and hostile, forcing humanity's scattered "
            "remnants to either unite or face extinction."
        ),
        target_word_count=150000,
    )


@pytest.fixture
def brief_extreme() -> ProductionBrief:
    """Extreme length brief (500k+ words)."""
    return ProductionBrief(
        production_type=ProductionType.EPIC_SAGA,
        genre=Genre.FANTASY,
        inspiration=(
            "The Five Kingdoms have been at war for generations. "
            "When the ancient seals binding the Demon Lords begin to "
            "fail, seven unlikely heroes from different kingdoms must "
            "embark on an epic quest to find the Shards of Creation—the "
            "only artifacts powerful enough to reseal the demons. "
            "Their journey will take them across continents, through "
            "political machinations, ancient ruins, and moral dilemmas "
            "that challenge everything they believe."
        ),
        target_word_count=500000,
    )


# ═══════════════════════════════════════════
# MOCK RESPONSE FIXTURES
# ═══════════════════════════════════════════

@pytest.fixture
def mock_agent_response() -> Dict:
    """Mock agent response."""
    return {
        "status": "success",
        "output": {
            "world": {
                "name": "Eldoria",
                "description": "A dying world where magic fades",
                "locations": ["Capital City", "Dark Forest", "Ancient Temple"],
                "rules": ["Magic requires life force", "Immortality is forbidden"],
            },
            "characters": [
                {
                    "name": "Lyra",
                    "role": "protagonist",
                    "archetype": "reluctant hero",
                    "motivation": "survival",
                    "arc": "fear → courage → sacrifice",
                }
            ],
            "structure": {
                "act_count": 3,
                "chapter_count": 20,
                "pacing": "steady"
            },
            "segments": [
                {
                    "index": i,
                    "title": f"Chapter {i+1}",
                    "word_count_target": 4000,
                    "summary": f"Summary of chapter {i+1}",
                }
                for i in range(20)
            ],
        },
        "metadata": {
            "tokens_used": 1500,
            "cost_usd": 0.005,
            "duration_seconds": 12.5,
        }
    }


@pytest.fixture
def mock_narrative_segment() -> str:
    """Mock narrative segment (one chapter)."""
    return """
    Chapter 1: The Discovery

    Lyra's fingers trembled as she opened the ancient grimoire. The leather
    binding felt warm against her skin, as if it contained a living heart.
    Her master, Theron, had forbidden her to enter his private chambers,
    but curiosity had won over caution.

    The pages were filled with elaborate diagrams and dense text in the old
    tongue. Most of it was beyond her comprehension, but one phrase stood
    out, written in blood-red ink: "The Price of Eternity."

    She knew she shouldn't read further. Every instinct screamed at her to
    close the book, return it to its shelf, and forget she'd ever been here.
    But her eyes were already scanning the text, her mind already translating
    the forbidden words.

    What she read would change everything.

    [...continues for 4000 words...]
    """


@pytest.fixture
def mock_quality_validation() -> Dict:
    """Mock quality validation results."""
    return {
        "coherence_score": 0.88,
        "logic_score": 0.92,
        "psychology_score": 0.85,
        "temporal_score": 0.90,
        "overall_score": 0.89,
        "issues": [],
        "passed": True,
    }


# ═══════════════════════════════════════════
# OUTPUT DIRECTORY FIXTURES
# ═══════════════════════════════════════════

@pytest.fixture
def longform_output_dir(tmp_path) -> Path:
    """Temporary output directory for long-form tests."""
    output_dir = tmp_path / "longform_output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


@pytest.fixture
def metrics_dir(tmp_path) -> Path:
    """Directory for test metrics."""
    metrics_dir = tmp_path / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    return metrics_dir


# ═══════════════════════════════════════════
# MEMORY PROFILING FIXTURES
# ═══════════════════════════════════════════

@pytest.fixture
def memory_profiler(request):
    """Memory profiler fixture."""
    if not request.config.getoption("--profile-memory"):
        yield None
        return

    try:
        from memory_profiler import profile
    except ImportError:
        pytest.skip("memory_profiler not installed")

    # Simple memory tracker
    import psutil
    import os

    process = psutil.Process(os.getpid())
    start_memory = process.memory_info().rss / 1024 / 1024  # MB

    yield {
        "process": process,
        "start_memory": start_memory,
    }

    end_memory = process.memory_info().rss / 1024 / 1024  # MB
    delta = end_memory - start_memory

    print(f"\n📊 Memory Usage:")
    print(f"   Start: {start_memory:.2f} MB")
    print(f"   End: {end_memory:.2f} MB")
    print(f"   Delta: {delta:.2f} MB")

    # Fail if memory usage exceeds 4GB
    if end_memory > 4096:
        pytest.fail(f"Memory usage exceeded 4GB: {end_memory:.2f} MB")


# ═══════════════════════════════════════════
# COST TRACKING FIXTURES
# ═══════════════════════════════════════════

@pytest.fixture
def cost_tracker(request):
    """Track and limit test costs."""
    max_cost = request.config.getoption("--max-cost")

    tracker = {
        "total_cost": 0.0,
        "max_cost": max_cost,
        "costs": [],
    }

    def add_cost(amount: float, description: str = ""):
        """Add cost and check limit."""
        tracker["total_cost"] += amount
        tracker["costs"].append({
            "amount": amount,
            "description": description,
        })

        if max_cost and tracker["total_cost"] > max_cost:
            pytest.fail(
                f"Cost limit exceeded: ${tracker['total_cost']:.2f} > ${max_cost:.2f}"
            )

    tracker["add_cost"] = add_cost

    yield tracker

    # Print cost summary
    print(f"\n💰 Cost Summary:")
    print(f"   Total: ${tracker['total_cost']:.2f}")
    if max_cost:
        print(f"   Limit: ${max_cost:.2f}")
        print(f"   Remaining: ${max_cost - tracker['total_cost']:.2f}")


# ═══════════════════════════════════════════
# SKIP CONDITIONS
# ═══════════════════════════════════════════

def pytest_collection_modifyitems(config, items):
    """Skip tests based on markers and conditions."""
    import os

    # Skip integration tests if no API key
    if not os.getenv("OPENAI_API_KEY"):
        skip_integration = pytest.mark.skip(reason="OPENAI_API_KEY not set")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)

    # Skip stress tests by default (unless explicitly requested)
    if not config.getoption("-m") or "stress" not in config.getoption("-m"):
        skip_stress = pytest.mark.skip(reason="Stress tests not requested (use -m stress)")
        for item in items:
            if "stress" in item.keywords:
                item.add_marker(skip_stress)
