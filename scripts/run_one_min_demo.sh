#!/usr/bin/env bash
# Precedent — 60-second live demo helper.
# Prints the spoken cue for each beat, waits on Enter, fires the right endpoint.
# Airplane-mode safe. No LLM calls.
#
# Usage:
#   bash scripts/run_one_min_demo.sh                 # run the demo
#   bash scripts/run_one_min_demo.sh --full-reset    # kill+seed+restart sim, then run
#   bash scripts/run_one_min_demo.sh --dry-run       # exercise every endpoint end-to-end, no prompts
#   bash scripts/run_one_min_demo.sh --reset         # soft reset only (state, not sim)

set -u

BASE="${PRECEDENT_CONSOLE_URL:-http://127.0.0.1:8000}"
REPO="/Users/tahakhan/Documents/Work/Projects/AI-Agent-Hackathon"

BOLD='\033[1m'
DIM='\033[2m'
CYAN='\033[36m'
GRN='\033[32m'
AMB='\033[33m'
MAG='\033[35m'
RED='\033[31m'
RST='\033[0m'

MODE="${1:-}"

# --- helpers ---------------------------------------------------------------
say() { printf '%b\n' "$*"; }
wait_key() {
  [[ "$MODE" == "--dry-run" ]] && return 0
  printf "${DIM}    press Enter to fire ▸${RST}"
  read -r _
}

beat() {
  printf "\n${BOLD}${CYAN}▸ Beat %s · %s${RST}\n" "$1" "$2"
  printf "  ${AMB}SAY:${RST}  %s\n" "$3"
  printf "  ${GRN}DO:${RST}   %s\n" "$4"
}

pretty_probes() {
  # Use -c so stdin (curl output) stays connected. Backslash-escape the inner quotes.
  python3 -c "import sys, json; d = json.load(sys.stdin); print(f\"      leaks {d['leaks']}/{d['leak_attempts']} · denied {d['denied']} · permitted {d['permitted']} · P50 {d['p50_us']}µs · P99 {d['p99_us']}µs · n={d['n']}\")"
}

pretty_verify() {
  python3 -c "import sys, json; d = json.load(sys.stdin); tail = d.get('tail_hash') or '—'; print(f\"      verified={d['verified']} · rows={d['rows']} · tail={tail}\")"
}

pretty_drive() {
  python3 -c "import sys, json; d = json.load(sys.stdin); outcome = d.get('outcome') or d.get('status') or '?'; ph = (d.get('plan_hash') or '')[:16]; print(f\"      {outcome} · plan_hash={ph}…\" if ph else f\"      {outcome} · verified={d.get('verified')}\")"
}

# --- full reset (kill + seed + restart sim) --------------------------------
if [[ "$MODE" == "--full-reset" ]]; then
  say "${DIM}killing stale ports…${RST}"
  lsof -ti:8000 2>/dev/null | xargs -r kill -9 2>/dev/null || true
  lsof -ti:8100 2>/dev/null | xargs -r kill -9 2>/dev/null || true
  sleep 1
  ( cd "$REPO" && source .venv/bin/activate && make demo-reset ) 2>&1 | tail -2
  say "${DIM}starting sim + console…${RST}"
  ( cd "$REPO" && source .venv/bin/activate && make sim > /tmp/sim.log 2>&1 & )
  sleep 4
  MODE=""
fi

# --- health check ----------------------------------------------------------
if ! curl -sf "$BASE/health" >/dev/null 2>&1; then
  printf "${RED}Console is not running at %s${RST}\n" "$BASE"
  printf "  Start it with: ${BOLD}make sim${RST}  or re-run with ${BOLD}--full-reset${RST}\n"
  exit 1
fi

# Fingerprint check: kernel matches manifest
kh_json=$(curl -s "$BASE/api/kernel-hash")
kh_ok=$(printf '%s' "$kh_json" | python3 -c 'import sys,json; d=json.load(sys.stdin); print("yes" if d.get("matches_manifest") else "no")')
kh=$(printf '%s' "$kh_json" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("kernel_hash"))')

printf "\n${BOLD}Precedent — 60-second demo${RST}  ${DIM}(console: %s)${RST}\n" "$BASE"
if [[ "$kh_ok" == "yes" ]]; then
  printf "  kernel: %s ${GRN}✓ matches manifest${RST}\n" "$kh"
else
  printf "  kernel: %s ${RED}✗ MISMATCH${RST}  (someone edited the deterministic surface)\n" "$kh"
fi

# Soft reset — clears console state but does NOT re-seed the STANDING class.
if [[ "$MODE" == "--reset" ]]; then
  say "${DIM}soft-resetting console state (keep sim running)…${RST}"
  curl -s -XPOST "$BASE/api/demo/reset" >/dev/null
  sleep 0.3
  say "${AMB}    note:${RST} a soft reset does NOT re-seed the fast-path class."
  say "${AMB}          if INC-2 refuses, re-run with --full-reset instead."
fi

if [[ "$MODE" != "--dry-run" ]]; then
  printf "\n${BOLD}Open the browser at %s and refresh once.${RST}\n" "$BASE"
  printf "Press Enter when you have the console on screen ▸ "
  read -r _
fi

# ---------------------------------------------------------------------------
# Beat 1 — Setup
# ---------------------------------------------------------------------------
beat 1 "0:00–0:07" \
  "\"IT incidents take 8 hours 51 minutes on average. The fix is usually a few clicks — once you find it.\"" \
  "point at the amber banner + Before/After strip"
wait_key

# ---------------------------------------------------------------------------
# Beat 2 — Novel incident + human approval
# ---------------------------------------------------------------------------
beat 2 "0:07–0:25" \
  "\"Messy publisher ticket lands. Extractor pulls the class fingerprint from mangled fields. Deterministic policy says L2. Plan on the left, rollback on the right. One human click.\"" \
  "firing INC-1 with hold now → then click Approve in the browser"
wait_key
say "${MAG}    firing INC-1 with hold:${RST}"
curl -s -XPOST "$BASE/api/drive/1?hold=true" | pretty_drive
if [[ "$MODE" == "--dry-run" ]]; then
  say "${DIM}    (dry-run: auto-approving)${RST}"
  curl -s -XPOST "$BASE/api/drive/1/approve" | pretty_drive
else
  printf "    ${AMB}now click Approve in the browser.${RST}\n"
  wait_key
fi

# ---------------------------------------------------------------------------
# Beat 3 — Promote to Standing Approval
# ---------------------------------------------------------------------------
beat 3 "0:25–0:32" \
  "\"Trust this fix class — Standing Approval. Approval moves earlier in time.\"" \
  "click Promote to Standing Approval on INC-1 in the browser"
if [[ "$MODE" == "--dry-run" ]]; then
  say "${DIM}    (dry-run: promoting via API)${RST}"
  curl -s -XPOST "$BASE/api/promote" -H 'Content-Type: application/json' \
    -d '{"class_key":"publisher|PUB-4012|schedule_item"}' >/dev/null
else
  wait_key
fi

# ---------------------------------------------------------------------------
# Beat 4 — Fast-path + refusal (both memorable lines)
# ---------------------------------------------------------------------------
beat 4 "0:32–0:42" \
  "\"Second time the same fingerprint arrives, no human is asked. Zero LLM. THE SECOND TIME IS FREE. And when a runbook is restricted, the system refuses — fail-closed. IT KNOWS WHAT IT'S NOT ALLOWED TO TOUCH.\"" \
  "firing INC-2 fast-path, then INC-3 refusal"
wait_key
say "${MAG}    INC-2 fast-path:${RST}"
curl -s -XPOST "$BASE/api/drive/2" | pretty_drive
sleep 0.4
say "${MAG}    INC-3 refusal:${RST}"
curl -s -XPOST "$BASE/api/drive/3" | pretty_drive

# ---------------------------------------------------------------------------
# Beat 5 — Proof (probes + chain verify)
# ---------------------------------------------------------------------------
beat 5 "0:42–0:53" \
  "\"No LLM in the permission decision — ever. 100 adversarial probes: zero leaks. Chain verified over on-disk audit rows. Kernel hash matches the committed manifest.\"" \
  "firing 100 adversarial probes + chain verify"
wait_key
say "${MAG}    probes:${RST}"
curl -s -XPOST "$BASE/api/probes/run" | pretty_probes
say "${MAG}    chain verify:${RST}"
curl -s "$BASE/api/audit/verify" | pretty_verify

# ---------------------------------------------------------------------------
# Beat 6 — Fetch strip close
# ---------------------------------------------------------------------------
beat 6 "0:53–1:00" \
  "\"Same loop lives on Agentverse and inside ASI:One. Every fix your org has ever applied, applied again — approval-gated, audited, reversible. That's Precedent.\"" \
  "scroll to Fetch strip (Watcher · Librarian · Operator + ASI:One shot + QR) — no click"
wait_key

printf "\n${BOLD}${GRN}✓ Demo complete.${RST}\n"
printf "${DIM}  re-run with --full-reset to seed a clean state.${RST}\n"
