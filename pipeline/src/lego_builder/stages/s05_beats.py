"""Stage 5: detect beats in the music track.

Inputs:  ctx.music
Outputs: 05_beats.json (Beats)
"""

from __future__ import annotations

from lego_builder.jsonio import write_model
from lego_builder.models import Beats
from lego_builder.stages.base import StageContext


def run(ctx: StageContext) -> None:
    if ctx.music is None:
        raise ValueError("s05_beats needs --music")
    import librosa

    y, sr = librosa.load(str(ctx.music))
    tempo, frames = librosa.beat.beat_track(y=y, sr=sr)
    beats = [float(t) for t in librosa.frames_to_time(frames, sr=sr)]
    # Approximate downbeats as every 4th beat (assumes 4/4). TODO: real downbeat detection.
    write_model(
        ctx.paths.ensure().beats,
        Beats(
            music=str(ctx.music),
            tempo_bpm=float(tempo if not hasattr(tempo, "__len__") else tempo[0]),
            duration_s=float(librosa.get_duration(y=y, sr=sr)),
            beats_s=beats,
            downbeats_s=beats[::4],
        ),
    )
