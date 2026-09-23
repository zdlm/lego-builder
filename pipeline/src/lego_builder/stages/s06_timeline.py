"""Stage 6: place every selected step on a beat and write the timeline Remotion renders.

Inputs:  03_selection.json, 04_assets.json, 05_beats.json
Outputs: 06_timeline.json (Timeline)

Layout of a video of length L:
  [0, HOOK_S)            hook: flash the most striking step
  [HOOK_S, L-END_S)      snaps: one per beat; "build" steps every 2nd beat, "climax" every beat
  [L-END_S, L-CTA_S)     reveal: finished model
  [L-CTA_S, L)           call to action
"""

from __future__ import annotations

from lego_builder.jsonio import read_model, write_model
from lego_builder.models import Assets, Beats, Selection, Timeline, TimelineEvent
from lego_builder.stages.base import StageContext

HOOK_S = 1.5
END_S = 3.5
CTA_S = 1.5


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
) -> Timeline:
    by_step = {a.step_number: a for a in assets.assets}
    events: list[TimelineEvent] = []

    hook = next((s for s in selection.selected if s.role == "hook"), None)
    if hook:
        events.append(
            TimelineEvent(
                kind="hook",
                start_s=0.0,
                duration_s=HOOK_S,
                step_number=hook.step_number,
                asset=by_step.get(hook.step_number),
            )
        )

    snap_window_end = length_s - END_S
    slots = [b for b in beats.beats_s if HOOK_S <= b < snap_window_end]
    snaps = [s for s in selection.selected if s.role in ("build", "climax")]

    # Build steps use every 2nd beat, climax steps every beat; drop steps if we run out of beats.
    i = 0
    placed: list[tuple[float, int]] = []
    for s in snaps:
        if i >= len(slots):
            break
        placed.append((slots[i], s.step_number))
        i += 2 if s.role == "build" else 1

    for k, (t, n) in enumerate(placed):
        nxt = placed[k + 1][0] if k + 1 < len(placed) else snap_window_end
        events.append(
            TimelineEvent(
                kind="snap",
                start_s=round(t, 3),
                duration_s=round(nxt - t, 3),
                step_number=n,
                asset=by_step.get(n),
                sfx=sfx[k % len(sfx)] if sfx else None,
            )
        )

    reveal = next((s for s in selection.selected if s.role == "reveal"), None)
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
            kind="cta", start_s=length_s - CTA_S, duration_s=CTA_S, text="Ready to build it?"
        )
    )

    return Timeline(
        run_id=run_id,
        set_name=set_name,
        set_number=set_number,
        length_s=length_s,  # type: ignore[arg-type]
        music=beats.music,
        total_steps=total_steps,
        events=events,
    )


def run(ctx: StageContext) -> None:
    from lego_builder.models import StepsRaw

    paths = ctx.paths
    timeline = build_timeline(
        run_id=ctx.run_id,
        set_name=ctx.set_name,
        set_number=ctx.set_number,
        length_s=ctx.length_s,
        selection=read_model(paths.selection, Selection),
        assets=read_model(paths.assets, Assets),
        beats=read_model(paths.beats, Beats),
        sfx=[str(p) for p in ctx.sfx],
        total_steps=len(read_model(paths.steps_raw, StepsRaw).steps),
    )
    write_model(paths.timeline, timeline)
