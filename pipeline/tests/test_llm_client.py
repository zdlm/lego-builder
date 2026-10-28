"""Tests for the LLM CLI wrapper, using fake `copilot` / `claude` executables."""

import json
import stat
from pathlib import Path

import pytest
from pydantic import BaseModel

from lego_builder.llm import client


class _Reply(BaseModel):
    ok: bool


def _fake_cli(
    tmp_path: Path, result: str, monkeypatch: pytest.MonkeyPatch, backend: str = "copilot"
) -> Path:
    """Create a fake CLI that records its args/env and prints a reply like the real one."""
    log = tmp_path / "log.json"
    script = tmp_path / backend
    reply = (
        f"print({result!r})\n"
        if backend == "copilot"
        else f"print(json.dumps({{'type': 'result', 'is_error': False, 'result': {result!r}}}))\n"
    )
    script.write_text(
        "#!/usr/bin/env python3\n"
        "import json, os, sys\n"
        f"json.dump({{'argv': sys.argv[1:], 'has_key': 'ANTHROPIC_API_KEY' in os.environ,"
        f" 'stdin': '' if sys.stdin.isatty() else sys.stdin.read()}}, open({str(log)!r}, 'w'))\n"
        + reply
    )
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("LEGO_BUILDER_LLM", backend)
    monkeypatch.setenv(f"LEGO_BUILDER_{backend.upper()}_BIN", str(script))
    monkeypatch.setenv("LEGO_BUILDER_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("ANTHROPIC_API_KEY", "should-not-leak")
    return log


def test_copilot_gets_prompt_images_as_attachments_and_no_repo_instructions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    log = _fake_cli(tmp_path, 'Here you go:\n```json\n{"ok": true}\n```', monkeypatch)
    img = tmp_path / "step.png"
    img.write_bytes(b"x")

    assert client.ask_json("Is it ok?", [img], _Reply).ok is True

    argv = json.loads(log.read_text())["argv"]
    prompt = argv[argv.index("-p") + 1]
    assert "Is it ok?" in prompt and str(img.resolve()) in prompt
    assert argv[argv.index("--attachment") + 1] == str(img.resolve())
    assert "--silent" in argv and "--no-custom-instructions" in argv


def test_claude_backend_uses_cli_without_api_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    log = _fake_cli(tmp_path, '{"ok": true}', monkeypatch, backend="claude")
    img = tmp_path / "step.png"
    img.write_bytes(b"x")

    assert client.ask_json("Is it ok?", [img], _Reply).ok is True

    call = json.loads(log.read_text())
    assert call["has_key"] is False
    assert "-p" in call["argv"] and "Read" in call["argv"]
    assert str(img.resolve()) in call["stdin"]


def test_ask_json_raises_on_bad_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _fake_cli(tmp_path, "not json at all", monkeypatch)
    with pytest.raises(client.LLMCLIError):
        client.ask_json("?", [], _Reply)
    assert not list((tmp_path / "data").rglob("*.txt"))  # invalid replies are not cached


def test_valid_replies_are_cached_per_prompt_and_image(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    log = _fake_cli(tmp_path, '{"ok": true}', monkeypatch)
    img = tmp_path / "step.png"
    img.write_bytes(b"x")
    client.ask_json("Is it ok?", [img], _Reply)

    log.unlink()
    assert client.ask_json("Is it ok?", [img], _Reply).ok is True
    assert not log.exists()  # served from the cache

    img.write_bytes(b"changed")
    client.ask_json("Is it ok?", [img], _Reply)
    assert log.exists()  # new image bytes, new call


def test_transient_cli_failure_is_retried(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    marker = tmp_path / "failed_once"
    script = tmp_path / "copilot"
    script.write_text(
        "#!/usr/bin/env python3\n"
        "import pathlib, sys\n"
        f"m = pathlib.Path({str(marker)!r})\n"
        "if not m.exists():\n"
        "    m.touch(); print('408 Timed out reading request body', file=sys.stderr); sys.exit(1)\n"
        "print('{\"ok\": true}')\n"
    )
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("LEGO_BUILDER_LLM", "copilot")
    monkeypatch.setenv("LEGO_BUILDER_COPILOT_BIN", str(script))
    monkeypatch.setenv("LEGO_BUILDER_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setattr(client, "RETRY_WAIT_S", 0)

    assert client.ask_json("?", [], _Reply).ok is True
    assert marker.exists()
