# Precedent — dev targets. Assumes a uv venv at .venv (see README setup).
PY := .venv/bin/python
PIP := uv pip

.PHONY: help install check-open-weight test lint secrets-scan sim console jira-smoke demo-reset bench freeze-check

help:
	@echo "install          install core+dev deps into .venv (add agents extra separately)"
	@echo "check-open-weight BasedAI guard: model names only in precedent/models.py"
	@echo "test             pytest (spec skeletons skip until implemented)"
	@echo "lint             ruff check"
	@echo "secrets-scan     gitleaks full-history scan (must be clean before repo goes public)"
	@echo "sim              run the MediaCo sim + console (TODO: T1/T2)"
	@echo "console          run the T2 judge console on :8000 (standalone, seeded demo)"
	@echo "demo-reset       reset sim state, memory, ladder in <30s (TODO: T1)"
	@echo "bench            run the conformance bench -> precedent_memory/bench/RESULTS.md (TODO: T3)"
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

# --- TODO targets: wired by the build teams (see Plan/BUILD-PLAN.md §4) ---
sim:
	@echo "TODO (T1/T2): uvicorn sim.app:app --reload  +  console"; exit 1

# T2 judge console — runs standalone on the seeded local-demo state (no T1 needed).
console:
	$(PY) -m uvicorn console.app:app --reload --port 8000

# Optional LIVE Jira smoke — guarded, off by default, never prints secrets.
jira-smoke:
	PRECEDENT_LIVE_JIRA_SMOKE=1 $(PY) scripts/jira_smoke.py

demo-reset:
	@echo "TODO (T1): reset sim SQLite from fixture snapshot, zero memory counters, reset ladder"; exit 1

bench:
	$(PY) -m precedent_memory.bench.conformance_bench

# Pre-freeze guard (Fri 21:00): everything that must be true before recording.
freeze-check: check-open-weight test secrets-scan
	@! grep -rn "‹" Plan Idea docs 2>/dev/null | grep -v "BUILD-PLAN\|working-notes\|pitch-deck\|03-pitch" || (echo "placeholder ‹ still present — fill or delete"; exit 1)
	@echo "freeze-check passed"
