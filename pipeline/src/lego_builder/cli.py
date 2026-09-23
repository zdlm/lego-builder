"""Command-line entry point: `lego-builder run ...` / `lego-builder stage ...`."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import typer
from dotenv import load_dotenv

from lego_builder.config import get_settings
from lego_builder.paths import run_paths
from lego_builder.stages import STAGES, StageContext

load_dotenv()
app = typer.Typer(help="LEGO instruction PDF → beat-synced social video", no_args_is_help=True)


def _ctx(
    run_id: str,
    pdf: Path | None,
    music: Path | None,
    set_name: str,
    set_number: str | None,
    length: int,
    sfx_dir: Path,
    no_llm_rank: bool,
) -> StageContext:
    sfx = sorted(sfx_dir.glob("*.wav")) + sorted(sfx_dir.glob("*.mp3")) if sfx_dir.exists() else []
    return StageContext(
        run_id=run_id,
        paths=run_paths(get_settings().data_dir, run_id),
        pdf=pdf,
        music=music,
        set_name=set_name,
        set_number=set_number,
        length_s=length,  # type: ignore[arg-type]
        sfx=sfx,
        use_llm_ranking=not no_llm_rank,
    )


@app.command()
def run(
    pdf: Path = typer.Option(..., exists=True, help="Instruction PDF"),
    music: Path = typer.Option(..., exists=True, help="Music track"),
    set_name: str = typer.Option("LEGO Set"),
    set_number: str | None = typer.Option(None),
    length: int = typer.Option(30, help="15, 30 or 60"),
    run_id: str | None = typer.Option(None, help="Defaults to <pdf-name>-<timestamp>"),
    sfx_dir: Path = typer.Option(Path("assets/sfx")),
    no_llm_rank: bool = typer.Option(False, help="Use heuristic selection only"),
) -> None:
    """Run every stage in order."""
    rid = run_id or f"{pdf.stem}-{datetime.now():%Y%m%d-%H%M%S}"
    ctx = _ctx(rid, pdf, music, set_name, set_number, length, sfx_dir, no_llm_rank)
    for name, fn in STAGES.items():
        typer.echo(f"==> {name}")
        fn(ctx)
    typer.echo(f"Done. Run id: {rid}\nTimeline: {ctx.paths.timeline}")


@app.command()
def stage(
    name: str = typer.Argument(..., help=f"One of: {', '.join(STAGES)}"),
    run: str = typer.Option(..., "--run", help="Existing run id"),
    pdf: Path | None = typer.Option(None),
    music: Path | None = typer.Option(None),
    set_name: str = typer.Option("LEGO Set"),
    set_number: str | None = typer.Option(None),
    length: int = typer.Option(30),
    sfx_dir: Path = typer.Option(Path("assets/sfx")),
    no_llm_rank: bool = typer.Option(False),
) -> None:
    """Re-run a single stage on an existing run."""
    if name not in STAGES:
        raise typer.BadParameter(f"Unknown stage {name}")
    STAGES[name](_ctx(run, pdf, music, set_name, set_number, length, sfx_dir, no_llm_rank))


if __name__ == "__main__":
    app()
