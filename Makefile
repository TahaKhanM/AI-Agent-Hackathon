# Precedent — dev targets. Assumes a uv venv at .venv (see README setup).
PY := .venv/bin/python
PIP := uv pip

.PHONY: help install check-open-weight test lint secrets-scan sim console jira-smoke demo-reset bench bench-extractor bench-uci live-drift dryrun-watcher freeze-check

help:
	@echo "install          install core+dev deps into .venv (add agents extra separately)"
	@echo "check-open-weight BasedAI guard: model names only in precedent/models.py"
	@echo "test             pytest (full suite)"
	@echo "lint             ruff check"
	@echo "secrets-scan     gitleaks full-history scan (must be clean before repo goes public)"
	@echo "sim              run the MediaCo sim (:8100) + judge console (:8000), T1 in-process"
	@echo "console          run the T2 judge console on :8000 (standalone, seeded demo)"
	@echo "demo-reset       reset sim state, memory, ladder in <30s"
	@echo "bench            run the conformance bench -> precedent_memory/bench/RESULTS.md"
	@echo "bench-extractor  score the frozen extractor over the seed-4207 mutation corpus (robustness)"
	@echo "dryrun-watcher   drive the live Watcher chat handler through the full loop, offline"
	@echo "freeze-check     pre-freeze guard: open-weight + tests + secrets + placeholder grep"

install:
	uv venv --python 3.13
	$(PIP) install -e ".[dev]"

check-open-weight:
	./scripts/check_open_weight.sh

test:
	$(PY) -m pytest -q

lint:
	.venv/bin/ruff check .

secrets-scan:
	gitleaks detect --source . --log-opts="--all" --redact -v

# Boot the MediaCo sim (:8100) + the judge console (:8000) sharing the demo dbs.
# T1's driver streams the live trace to the console (see scripts/drive_incident.py).
sim:
	$(PY) scripts/run_demo.py

# T2 judge console — runs standalone on the seeded local-demo state (no T1 needed).
console:
	$(PY) -m uvicorn console.app:app --reload --port 8000

# Optional LIVE Jira smoke — guarded, off by default, never prints secrets.
jira-smoke:
	PRECEDENT_LIVE_JIRA_SMOKE=1 $(PY) scripts/jira_smoke.py

demo-reset:
	$(PY) scripts/demo_reset.py

bench:
	$(PY) -m precedent_memory.bench.conformance_bench

# Extractor robustness: run T1's FROZEN deterministic extractor over the seed-4207 mutation
# corpus and write the ONE robustness number (false-fast-path MUST be 0) to
# precedent_memory/bench/extractor_robustness.json — the source of truth the chip/slide/README/BUIDL cite.
bench-extractor:
	VENICE_BASE_URL="http://127.0.0.1:9/unreachable" $(PY) -m precedent.extractor_robustness

# Drive the live Watcher chat handler through the full loop offline (report->gate->approve->execute).
dryrun-watcher:
	PRECEDENT_AGENTS_OFFLINE=1 $(PY) scripts/dryrun_watcher_chat.py

# Saturday realism run (human): point the bench at the real UCI ~25k-record store.
# Exits non-zero until the CSV is downloaded (see data/raw/SOURCES.md). "25k-record store".
bench-uci:
	$(PY) -m precedent_memory.bench.uci_realism

# Saturday LIVE drift/TTC (human): real Jira flips, TTC anchored to /rest/api/3/auditing/record.
# Guarded + fail-closed: exits non-zero when Jira is unconfigured or the live flag is unset.
live-drift:
	$(PY) scripts/live_drift_ttc.py

# Release guard: everything that must be true before a public cut.
# The placeholder grep matches a COMPLETE ‹…› token on shippable surfaces (README + bench
# results), so self-referential prose ("Ctrl-F for `‹`") never trips it.
freeze-check: check-open-weight test lint secrets-scan
	@! grep -rnE "‹[^›]*›" README.md precedent_memory/bench/RESULTS.md 2>/dev/null || (echo "unfilled ‹…› placeholder on a shippable surface — fill or delete"; exit 1)
	@echo "freeze-check passed"
