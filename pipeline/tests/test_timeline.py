from lego_builder.models import Assets, Beats, SelectedStep, Selection
from lego_builder.stages.s06_timeline import build_timeline


def test_snaps_land_on_beats_and_fit_length() -> None:
    beats = Beats(music="m.mp3", tempo_bpm=120, duration_s=40, beats_s=[i * 0.5 for i in range(80)])
    sel = Selection(
        target_length_s=15,
        selected=[SelectedStep(step_number=5, score=1, reason="", role="hook")]
        + [SelectedStep(step_number=i, score=0.5, reason="", role="build") for i in range(1, 8)]
        + [SelectedStep(step_number=i, score=0.5, reason="", role="climax") for i in range(8, 12)]
        + [SelectedStep(step_number=12, score=1, reason="", role="reveal")],
    )
    t = build_timeline("r", "Set", None, 15, sel, Assets(assets=[]), beats, ["c.wav"], 12)
    snaps = [e for e in t.events if e.kind == "snap"]
    assert snaps and all(e.start_s in beats.beats_s for e in snaps)
    assert max(e.start_s + e.duration_s for e in t.events) <= 15 + 1e-6
    assert t.events[0].kind == "hook" and t.events[-1].kind == "cta"
