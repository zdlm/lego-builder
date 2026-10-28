from lego_builder.models import Assets, Beats, SelectedStep, Selection
from lego_builder.stages.s06_timeline import build_timeline


def test_snaps_land_on_beats_and_fit_length() -> None:
    beats = Beats(
        music="m.mp3",
        tempo_bpm=120,
        duration_s=40,
        beats_s=[i * 0.5 for i in range(80)],
    )
    sel = Selection(
        target_length_s=15,
        selected=[SelectedStep(step_number=5, score=1, reason="", role="hook")]
        + [SelectedStep(step_number=i, score=0.5, reason="", role="build") for i in range(1, 8)]
        + [SelectedStep(step_number=i, score=0.5, reason="", role="climax") for i in range(8, 12)]
        + [SelectedStep(step_number=12, score=1, reason="", role="reveal")],
    )
    t = build_timeline("r", "Set", None, 15, sel, Assets(assets=[]), beats, ["c.wav"], 12)
    snaps = [e for e in t.events if e.kind == "snap"]
    assert snaps and all(e.impact_s in beats.beats_s for e in snaps)
    assert all(e.start_s < (e.impact_s or 0) for e in snaps)
    assert snaps[-1].step_number == 12
    assert max(e.start_s + e.duration_s for e in t.events) <= 15 + 1e-6
    assert t.events[0].kind == "hook" and t.events[-1].kind == "cta"


def test_events_are_contiguous_and_last_snap_is_not_tiny() -> None:
    beats = Beats(
        music="m.mp3",
        tempo_bpm=84,
        duration_s=60,
        beats_s=[i * 0.714 for i in range(80)],
    )
    sel = Selection(
        target_length_s=30,
        selected=[SelectedStep(step_number=26, score=1, reason="", role="hook")]
        + [SelectedStep(step_number=i, score=i / 30, reason="", role="build") for i in range(1, 21)]
        + [SelectedStep(step_number=i, score=0.5, reason="", role="climax") for i in range(21, 26)]
        + [SelectedStep(step_number=26, score=1, reason="", role="reveal")],
    )
    t = build_timeline("r", "Set", None, 30, sel, Assets(assets=[]), beats, [], 26)
    for a, b in zip(t.events, t.events[1:], strict=False):
        assert abs(a.start_s + a.duration_s - b.start_s) < 1e-6
    snaps = [e for e in t.events if e.kind == "snap"]
    assert snaps[-1].step_number == 26
    assert snaps[-1].duration_s >= 0.5
    assert [e.step_number for e in snaps] == sorted(e.step_number for e in snaps)


def test_fit_drops_lowest_scoring_builds_when_beats_run_out() -> None:
    from lego_builder.stages.s06_timeline import fit_to_beats

    snaps = [
        SelectedStep(step_number=i, score=i / 10, reason="", role="build") for i in range(1, 9)
    ]
    placed = fit_to_beats(snaps, [1.0, 2.0, 3.0, 4.0, 5.0])
    assert [s.step_number for _, s in placed] == [4, 5, 6, 7, 8]
    assert [t for t, _ in placed] == [1.0, 2.0, 3.0, 4.0, 5.0]


def test_music_skips_beatless_intro() -> None:
    beats_s = [22.9 + i * 0.714 for i in range(200)]
    beats = Beats(
        music="m.mp3",
        tempo_bpm=84,
        duration_s=183,
        beats_s=beats_s,
        downbeats_s=beats_s[::4],
    )
    sel = Selection(
        target_length_s=30,
        selected=[
            SelectedStep(step_number=i, score=0.5, reason="", role="build") for i in range(20)
        ],
    )
    t = build_timeline("r", "Set", None, 30, sel, Assets(assets=[]), beats, [], 20, "final.png")
    snaps = [e for e in t.events if e.kind == "snap"]
    assert t.music_start_s == round(22.9 - 1.5, 3)
    assert snaps[0].impact_s == 1.5
    assert len(snaps) >= 10
    assert t.final_image == "final.png"


def test_music_offset_never_runs_past_track_end() -> None:
    beats = Beats(music="m.mp3", tempo_bpm=120, duration_s=40, beats_s=[20.0, 20.5])
    sel = Selection(target_length_s=30, selected=[])
    t = build_timeline("r", "Set", None, 30, sel, Assets(assets=[]), beats, [], 0)
    assert t.music_start_s == 10.0
