from lego_builder.models import StepUnderstanding
from lego_builder.stages.s03_select import pick, score_step


def _step(n: int, change: float, milestone: str | None = None) -> StepUnderstanding:
    return StepUnderstanding(
        step_number=n,
        visual_change=change,
        is_milestone=milestone is not None,
        milestone_kind=milestone,  # type: ignore[arg-type]
    )


def test_milestone_scores_higher() -> None:
    assert score_step(_step(1, 0.5, "shape_forms")) > score_step(_step(2, 0.5))


def test_pick_keeps_final_and_order() -> None:
    steps = [_step(i, (i % 5) / 5) for i in range(1, 41)]
    out = pick(steps, 10)
    assert out[0].role == "hook"
    assert out[-1].role == "reveal" and out[-1].step_number == 40
    body = [s.step_number for s in out[1:]]
    assert body == sorted(body)
    assert len(body) == 10


def test_display_stand_after_final_step_is_not_picked() -> None:
    steps = [_step(i, 0.5) for i in range(1, 26)] + [
        _step(26, 0.8, "final"),
        _step(27, 0.9),
    ]
    out = pick(steps, 10)
    assert out[-1].role == "reveal" and out[-1].step_number == 26
    assert all(s.step_number != 27 for s in out)


def test_finished_subassembly_is_not_the_final_step() -> None:
    steps = [_step(i, 0.5) for i in range(1, 11)]
    steps[4] = _step(5, 0.8, "final")  # sub-assembly done...
    steps[5] = _step(6, 0.5, "subassembly_join")  # ...and attached in the next step
    out = pick(steps, 5)
    assert out[-1].role == "reveal" and out[-1].step_number == 10
