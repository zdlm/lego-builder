from lego_builder.models import SCHEMA_VERSION, StepUnderstanding, Timeline, TimelineEvent


def test_timeline_roundtrip() -> None:
    t = Timeline(
        run_id="r",
        set_name="Test",
        length_s=15,
        music="m.mp3",
        total_steps=3,
        events=[TimelineEvent(kind="cta", start_s=13.5, duration_s=1.5, text="Go")],
    )
    again = Timeline.model_validate_json(t.model_dump_json())
    assert again == t
    assert again.schema_version == SCHEMA_VERSION


def test_visual_change_bounds() -> None:
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        StepUnderstanding(step_number=1, visual_change=1.5, is_milestone=False)
