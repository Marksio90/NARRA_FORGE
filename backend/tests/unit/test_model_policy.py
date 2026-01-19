"""Unit tests for model policy."""

from core.config import settings
from services.model_policy import ModelPolicy, PipelineStage


def test_get_model_for_structure_stage() -> None:
    """Test that structure stage uses mini model."""
    model = ModelPolicy.get_model_for_stage(PipelineStage.STRUCTURE)
    assert model == settings.model_mini


def test_get_model_for_prose_stage() -> None:
    """Test that prose stage uses high model."""
    model = ModelPolicy.get_model_for_stage(PipelineStage.PROSE)
    assert model == settings.model_high


def test_get_model_for_all_mini_stages() -> None:
    """Test that all mini stages return mini model."""
    for stage in ModelPolicy.MINI_STAGES:
        model = ModelPolicy.get_model_for_stage(stage)
        assert model == settings.model_mini, f"Stage {stage} should use mini model"


def test_get_model_for_all_high_stages() -> None:
    """Test that all high stages return high model."""
    for stage in ModelPolicy.HIGH_STAGES:
        model = ModelPolicy.get_model_for_stage(stage)
        assert model == settings.model_high, f"Stage {stage} should use high model"


def test_get_token_budget_for_qa_stage() -> None:
    """Test token budget for QA stage."""
    budget = ModelPolicy.get_token_budget_for_stage(PipelineStage.QA)
    assert budget == 1000


def test_get_token_budget_for_prose_stage() -> None:
    """Test token budget for prose stage."""
    budget = ModelPolicy.get_token_budget_for_stage(PipelineStage.PROSE)
    assert budget == 4000


def test_get_token_budget_for_structure_stage() -> None:
    """Test token budget for structure stage."""
    budget = ModelPolicy.get_token_budget_for_stage(PipelineStage.STRUCTURE)
    assert budget == 2000


def test_get_temperature_for_qa_stage() -> None:
    """Test temperature for QA stage (analytical)."""
    temp = ModelPolicy.get_temperature_for_stage(PipelineStage.QA)
    assert temp == 0.3


def test_get_temperature_for_prose_stage() -> None:
    """Test temperature for prose stage (creative)."""
    temp = ModelPolicy.get_temperature_for_stage(PipelineStage.PROSE)
    assert temp == 0.8


def test_get_temperature_for_character_profile() -> None:
    """Test temperature for character profile."""
    temp = ModelPolicy.get_temperature_for_stage(PipelineStage.CHARACTER_PROFILE)
    assert temp == 0.5


def test_get_stage_metadata() -> None:
    """Test getting all metadata for a stage."""
    metadata = ModelPolicy.get_stage_metadata(PipelineStage.PROSE)

    assert "model" in metadata
    assert "token_budget" in metadata
    assert "temperature" in metadata
    assert "stage" in metadata

    assert metadata["model"] == settings.model_high
    assert metadata["token_budget"] == 4000
    assert metadata["temperature"] == 0.8
    assert metadata["stage"] == "prose"


def test_get_stage_metadata_for_qa() -> None:
    """Test getting all metadata for QA stage."""
    metadata = ModelPolicy.get_stage_metadata(PipelineStage.QA)

    assert metadata["model"] == settings.model_mini
    assert metadata["token_budget"] == 1000
    assert metadata["temperature"] == 0.3
    assert metadata["stage"] == "qa"


def test_all_stages_have_consistent_policies() -> None:
    """Test that all stages have consistent policies across methods."""
    for stage in PipelineStage:
        # Should not raise
        model = ModelPolicy.get_model_for_stage(stage)
        budget = ModelPolicy.get_token_budget_for_stage(stage)
        temp = ModelPolicy.get_temperature_for_stage(stage)

        # Verify basic constraints
        assert model in [settings.model_mini, settings.model_high]
        assert budget > 0
        assert 0.0 <= temp <= 2.0


def test_stage_coverage() -> None:
    """Test that all stages are covered in MINI_STAGES or HIGH_STAGES."""
    all_stages = set(PipelineStage)
    covered_stages = ModelPolicy.MINI_STAGES | ModelPolicy.HIGH_STAGES
    assert all_stages == covered_stages, "Not all stages are covered in policy"


def test_no_stage_overlap() -> None:
    """Test that no stage is in both MINI_STAGES and HIGH_STAGES."""
    overlap = ModelPolicy.MINI_STAGES & ModelPolicy.HIGH_STAGES
    assert len(overlap) == 0, f"Stages appear in both mini and high: {overlap}"
