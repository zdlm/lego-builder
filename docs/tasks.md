# Task board

Claim a task by writing your name or model and the date in the **Owner** column before you start (e.g. `claude 2026-09-23`). Move it to Done when finished. Don't take a task someone else owns.

## To do

| # | Task | Area | Needs | Done when | Owner |
|---|---|---|---|---|---|
| 1 | Pick the demo LEGO set and put its PDF in `data/input/` | – | – | PDF chosen (mid-size set with a clear "it comes together" moment), name and source recorded here, shared via team drive | |
| 2 | Add royalty-free music to `assets/music/` and 3–5 click SFX to `assets/sfx/` | assets | – | Files in place; every file logged in `assets/README.md` with source and licence (commercial social use allowed) | |
| 3 | Test `segment_page` prompt on the demo PDF; fix bounding boxes | pipeline/s01 | 1, `claude` CLI | On the demo PDF, ≥ 95% of printed steps are found with correct numbers and boxes that crop the whole panel; cover/parts/ad pages skipped; prompt tweaks committed | |
| 5 | Tune `score_step` weights by watching output | pipeline/s03 | 3 + s02 run | On the demo run, the picked steps look right to two reviewers for 15/30/60 s; weights/rules and reasoning noted in the PR; tests updated | |
| 7 | Hook and Reveal visual polish; brand fonts | video | a run's `06_timeline.json` | Hook and Reveal reviewed in Studio at 1080×1920; fonts from `assets/fonts/` with licence logged | |
| 8 | Export 15 / 30 / 60 s in one command | build | a run | One command (e.g. `make render-all RUN=<id>`) writes all three MP4s; README updated | |
| 9 | (Nice) 3D renderer replacing s04 (Blender + LDraw) | pipeline/s04 | 3D model data for the set; ADR | Contract change (`clip` on `StepAsset`) agreed, `SnapClip` component, ADR written | |
| 10 | (Nice) Web UI to review and edit the selection | web | stable `03_selection.json` | Can load a run, reorder/toggle steps, save `03_selection.json`, and trigger s04–s06 | |
| 11 | (Nice) Generate social caption + hashtags from the timeline | pipeline | 6 | Prompt file + model + test; output written to the run directory | |
| 12 | Commit a tiny sample run (a few steps, 2–3 s of music) as a fixture so people can work on `video/` and s03–s06 without a PDF or Claude | pipeline/tests, video | – | `pipeline/tests/fixtures/sample_run/` loads in Studio and runs s03–s06 in a test | |
| 13 | Real downbeat detection in `s05_beats` (replace the "every 4th beat" TODO) | pipeline/s05 | 2 | Test with a track of known tempo; `downbeats_s` aligns with bar starts | |
| 14 | Fix the existing mypy errors from OpenCV stubs so `make lint` is clean | pipeline | – | `make lint` exits 0 without blanket `ignore`s | |
| 15 | Add CI (GitHub Actions) running `make test` and `make lint` | build | 14 | PR checks run on push; no Claude access needed | |

## In progress

| # | Task | Owner |
|---|---|---|

## Done

| # | Task | Owner |
|---|---|---|
| 0 | Project scaffold, docs and data contracts | claude 2026-09-23 |
| 4 | Align consecutive step images before diffing (ORB + homography) | copilot 2026-09-23 |
| 6 | Scale cutout position to displayed size in `SnapStep` | copilot 2026-09-23 |
