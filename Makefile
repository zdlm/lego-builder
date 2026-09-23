# LEGO Builder — common commands. Run `make help` for a list.
PY      := pipeline/.venv/bin/python
CLI     := pipeline/.venv/bin/lego-builder
PDF     ?=
MUSIC   ?=
RUN     ?=
STAGE   ?=
LEN     ?= 30

.PHONY: help setup run stage preview render test lint clean

help: ## Show this help
	@grep -E '^[a-z]+:.*## ' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  %-10s %s\n", $$1, $$2}'

setup: ## Install Python and Node dependencies
	bash scripts/setup.sh

run: ## Run the full pipeline: make run PDF=... MUSIC=...
	$(CLI) run --pdf $(PDF) --music $(MUSIC)

stage: ## Re-run one stage: make stage STAGE=s03_select RUN=<run_id>
	$(CLI) stage $(STAGE) --run $(RUN)

preview: ## Open Remotion Studio on a run: make preview RUN=<run_id>
	cd video && RUN_ID=$(RUN) npm run studio

render: ## Render MP4: make render RUN=<run_id> LEN=30
	cd video && RUN_ID=$(RUN) LEN=$(LEN) npm run render

test: ## Run Python tests
	cd pipeline && .venv/bin/pytest -q

lint: ## Lint and type-check Python and TypeScript
	cd pipeline && .venv/bin/ruff check . && .venv/bin/mypy src
	cd video && npx tsc --noEmit

clean: ## Remove caches and rendered videos (keeps data/)
	rm -rf pipeline/.pytest_cache pipeline/.mypy_cache pipeline/.ruff_cache video/out
