"""Tests for the Claude Code CLI wrapper, using a fake `claude` executable."""

import json
import stat
from pathlib import Path

import pytest
from pydantic import BaseModel

from lego_builder.llm import client


class _Reply(BaseModel):
    ok: bool


def _fake_cli(tmp_path: Path, result: str, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a fake `claude` that records its args/env and prints a CLI-style JSON envelope."""
    log = tmp_path / "log.json"
    script = tmp_path / "claude"
    script.write_text(
        "#!/usr/bin/env python3\n"
        "import json, os, sys\n"
        f"json.dump({{'argv': sys.argv[1:], 'has_key': 'ANTHROPIC_API_KEY' in os.environ,"
        f" 'stdin': sys.stdin.read()}}, open({str(log)!r}, 'w'))\n"
        f"print(json.dumps({{'type': 'result', 'is_error': False, 'result': {result!r}}}))\n"
    )
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("LEGO_BUILDER_CLAUDE_BIN", str(script))
    monkeypatch.setenv("ANTHROPIC_API_KEY", "should-not-leak")
    return log


def test_ask_json_uses_cli_without_api_key(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    log = _fake_cli(tmp_path, 'Here you go:\n```json\n{"ok": true}\n```', monkeypatch)
    img = tmp_path / "step.png"
    img.write_bytes(b"x")

    reply = client.ask_json("Is it ok?", [img], _Reply)

    assert reply.ok is True
    call = json.loads(log.read_text())
    assert call["has_key"] is False
    assert "-p" in call["argv"] and "Read" in call["argv"]
    assert str(img.resolve()) in call["stdin"]


def test_ask_json_raises_on_bad_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _fake_cli(tmp_path, "not json at all", monkeypatch)
    with pytest.raises(client.ClaudeCLIError):
        client.ask_json("?", [], _Reply)
