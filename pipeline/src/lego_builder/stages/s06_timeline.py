"""Stage 6: place every selected step on a beat and write the timeline Remotion renders.

Inputs:  01_steps_raw.json, 03_selection.json, 04_assets.json, 05_beats.json
Outputs: 06_timeline.json (Timeline)

Layout of a video of length L:
  [0, HOOK_S)            hook: flash the most striking step
  [HOOK_S, L-END_S)      snaps: the parts of each step land exactly on a beat (`impact_s`);
                         "build" steps every few beats, "climax" steps and the final step every beat
  [L-END_S, L-CTA_S)     reveal: finished model
  [L-CTA_S, L)           call to action

Each snap event starts a little before its beat (`lead`) so the parts can fly in and land on it.
The music is started `music_start_s` into the track so its first downbeat lands where the snaps
begin; beat times below are shifted into video time accordingly.
"""

from __future__ import annotations

from lego_builder.jsonio import read_model, write_model
from lego_builder.models import (
    Assets,
    Beats,
    SelectedStep,
    Selection,
    Timeline,
    TimelineEvent,
)
from lego_builder.stages.base import StageContext

HOOK_S = 1.5
END_S = 3.5
CTA_S = 1.5
LEAD_S = 0.3  # longest fly-in before a beat
MIN_LAST_S = 0.5  # the last snap holds at least this long before the reveal
MAX_BUILD_STRIDE = 4


def music_offset(beats: Beats, length_s: int) -> float:
    """Seconds to skip into the track so its first downbeat falls at HOOK_S."""
    first = (beats.downbeats_s or beats.beats_s or [HOOK_S])[0]
    return round(max(0.0, min(first - HOOK_S, beats.duration_s - length_s)), 3)


def fit_to_beats(snaps: list[SelectedStep], slots: list[float]) -> list[tuple[float, SelectedStep]]:
    """Give each snap a beat, in order, using up the snap window.

    Climax steps get one beat each. Spare beats go to build steps, earliest first, so the pace
    starts slower and speeds up. If there are fewer beats than steps, the lowest-scoring build
    steps are dropped.
    """
    snaps = list(snaps)
    while snaps and len(snaps) > len(slots):
        builds = [s for s in snaps if s.role == "build"]
        snaps.remove(min(builds or snaps[:-1] or snaps, key=lambda s: s.score))
    spare = len(slots) - len(snaps)
    n_builds = sum(1 for s in snaps[:-1] if s.role == "build")

    placed: list[tuple[float, SelectedStep]] = []
    i, j = 0, 0
    for s in snaps:
        placed.append((slots[i], s))
        step = 1
        if s.role == "build" and n_builds:
            extra = spare // n_builds + (1 if j < spare % n_builds else 0)
            step += min(extra, MAX_BUILD_STRIDE - 1)
            j += 1
        i += step
    return placed


def build_timeline(
    run_id: str,
    set_name: str,
    set_number: str | None,
    length_s: int,
    selection: Selection,
    assets: Assets,
    beats: Beats,
    sfx: list[str],
    total_steps: int,
    final_image: str | None = None,
    cta_text: str = "Ready to build it?",
) -> Timeline:
    by_step = {a.step_number: a for a in assets.assets}
    snap_window_end = length_s - END_S
    offset = music_offset(beats, length_s)
    video_beats = [round(b - offset, 3) for b in beats.beats_s]
    slots = [b for b in video_beats if HOOK_S <= b <= snap_window_end - MIN_LAST_S]

    reveal = next((s for s in selection.selected if s.role == "reveal"), None)
    snaps = [s for s in selection.selected if s.role in ("build", "climax")]
    if reveal and all(s.step_number != reveal.step_number for s in snaps):
        # The step that finishes the model is the last, most satisfying click.
        snaps.append(reveal.model_copy(update={"role": "climax"}))
    placed = fit_to_beats(snaps, slots)

    starts: list[float] = []
    prev_impact = 0.0
    for impact, _ in placed:
        starts.append(round(impact - min(LEAD_S, 0.6 * (impact - prev_impact)), 3))
        prev_impact = impact

    events: list[TimelineEvent] = []
    hook = next((s for s in selection.selected if s.role == "hook"), None)
    if hook:
        events.append(
            TimelineEvent(
                kind="hook",
                start_s=0.0,
                duration_s=starts[0] if starts else HOOK_S,
                step_number=hook.step_number,
                asset=by_step.get(hook.step_number),
            )
        )

    for k, (impact, s) in enumerate(placed):
        end = starts[k + 1] if k + 1 < len(placed) else snap_window_end
        events.append(
            TimelineEvent(
                kind="snap",
                start_s=starts[k],
                duration_s=round(end - starts[k], 3),
                impact_s=impact,
                step_number=s.step_number,
                asset=by_step.get(s.step_number),
                sfx=sfx[k % len(sfx)] if sfx else None,
            )
        )

    if reveal:
        events.append(
            TimelineEvent(
                kind="reveal",
                start_s=snap_window_end,
                duration_s=END_S - CTA_S,
                step_number=reveal.step_number,
                asset=by_step.get(reveal.step_number),
            )
        )
    events.append(
        TimelineEvent(
            kind="cta",
            start_s=length_s - CTA_S,
            duration_s=CTA_S,
            text=cta_text,
        )
    )

    return Timeline(
        run_id=run_id,
        set_name=set_name,
        set_number=set_number,
        length_s=length_s,  # type: ignore[arg-type]
        music=beats.music,
        music_start_s=offset,
        # Count up to the step that finishes the model, not extras such as a display stand.
        total_steps=reveal.step_number if reveal else total_steps,
        final_image=final_image,
        final_model=assets.final_model,
        events=events,
    )


def run(ctx: StageContext) -> None:
    from lego_builder.models import StepsRaw

    paths = ctx.paths
    raw = read_model(paths.steps_raw, StepsRaw)
    timeline = build_timeline(
        run_id=ctx.run_id,
        set_name=ctx.set_name,
        set_number=ctx.set_number,
        length_s=ctx.length_s,
        selection=read_model(paths.selection, Selection),
        assets=read_model(paths.assets, Assets),
        beats=read_model(paths.beats, Beats),
        sfx=[str(p) for p in ctx.sfx],
        total_steps=len(raw.steps),
        final_image=raw.final_image,
        cta_text=ctx.cta_text,
    )
    write_model(paths.timeline, timeline)
