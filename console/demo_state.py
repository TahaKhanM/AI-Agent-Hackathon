"""Console demo state — the T2 view/control surface's backing store.  [owner T2]

This is NOT the permission authority. Every access decision is delegated to
`precedent_memory` (store/retrieve/sync/audit) against a real SQLite memory db.
The console only renders what the memory layer returns and drives the approval
ladder + the local fake permission source.

Canonical vs display: the ladder DATA token is always "STANDING"; the string
"Standing Approval" is DISPLAY-ONLY (LEVEL_LABELS). T1's precedent/ladder.py reads
the canonical token, so the console must never write display text to class_ladder.

Shared-DB seam for T1: DemoState(db_path=...) or the PRECEDENT_MEMORY_DB env var
points the console at the SAME SQLite file T1 writes to (store/retrieve/audit), so
a T1 execution is reflected in the console's audit/memory view. With no path set,
the console runs a self-contained in-memory demo. Seeding is idempotent, so
pointing at a populated shared DB never duplicates rows.

Integration seam: `push_trace()` (and POST /api/trace) let T1 stream its own
DETECT/EXECUTE/VERIFY steps in without the console importing any T1 logic. All
fake/local affordances are labelled "local-demo".
"""
from __future__ import annotations

import json
import os
import pathlib
import threading

from precedent_memory import audit, db, retrieve, store
from precedent_memory import sync as syncmod

# The committed extractor-robustness headline (the ONE number the chip/slide/README/BUIDL cite,
# P1.7). Read once from the source of truth; the console only DISPLAYS it, never recomputes it.
_ROBUSTNESS_PATH = (pathlib.Path(__file__).resolve().parent.parent
                    / "precedent_memory" / "bench" / "extractor_robustness.json")


def _load_robustness() -> dict | None:
    try:
        d = json.loads(_ROBUSTNESS_PATH.read_text())
    except (OSError, ValueError):
        return None
    return {
        "false_fast_paths": d.get("false_fast_path"),
        "total": d.get("n_mutations"),
        "decoys_resisted": d.get("red_herring_resisted"),
        "decoys_total": d.get("red_herring_total"),
        "headline": d.get("headline"),
    }


_ROBUSTNESS = _load_robustness()

# Baseline: MetricNet business-hours MTTR. Labelled honestly on-screen; NOT a
# measurement of the current live run.
BASELINE_SECONDS = 8 * 3600 + 51 * 60  # 31860 == 8h 51m
BASELINE_LABEL_SHORT = "8h 51m"
BASELINE_SOURCE_LABEL = "MetricNet business-hours MTTR (industry benchmark, labelled)"

RIGHTS = ("jira", "issue-security:rights", "Rights Ops")
SCHED = ("jira", "issue-security:scheduling", "Scheduling Ops")

# INC-2's incident class — pre-promoted to STANDING in the cold-open snapshot so the zero-LLM
# fast-path fires on stage (see console/session.py memory_template + scripts/demo_reset.py).
SCHED_CLASS_STANDING = "scheduler|SCH-DUP-002|schedule_item"

# Canonical ladder DATA token vs DISPLAY text (T1 reads the canonical token).
STANDING = "STANDING"
LEVEL_LABELS = {"L0": "L0", "L1": "L1", "L2": "L2", "STANDING": "Standing Approval",
                "ESCALATE": "Escalate"}


def level_label(level: str) -> str:
    return LEVEL_LABELS.get(level, level)


class DemoState:
    def __init__(self, db_path: str | None = None) -> None:
        self._lock = threading.RLock()
        # resolve once: explicit arg > env > in-memory demo default
        self._db_path = db_path or os.environ.get("PRECEDENT_MEMORY_DB") or ":memory:"
        self.reset()

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #
    def reset(self) -> dict:
        with self._lock:
            # Reconnect: :memory: yields a fresh db (clears); a file path re-opens
            # the SAME file (preserves T1 data) and re-seeds idempotently. Reset
            # never DROPs tables or deletes files.
            old = getattr(self, "conn", None)
            if old is not None:
                old.close()
            self.conn = db.connect(self._db_path, check_same_thread=False)
            self.source = syncmod.FakePermissionSource()
            self.trace: list[dict] = []
            self.principal = "scheduling-ops"   # the identity the judge drives as
            self.retrieval_mode = "live"
            self.sync_available = True
            self.flip_on = False
            self.demo_started_at = db.utcnow_iso()   # live-stopwatch start
            self._seed()
            return self.snapshot()

    def _get_or_store(self, fingerprint: str, record: dict, lineage: list[str]) -> int:
        row = self.conn.execute(
            "SELECT id FROM memory_record WHERE fingerprint = ?", (fingerprint,)).fetchone()
        if row is not None:
            return row["id"]
        return store.store(record, lineage, principal_ctx={"principal": "demo-seed"},
                           conn=self.conn)

    def _seed(self) -> None:
        conn = self.conn
        store.ensure_constraint(conn, *RIGHTS)
        store.ensure_constraint(conn, *SCHED)
        store.put_principal(conn, "scheduling-ops", [store.ensure_constraint(conn, *SCHED)])
        store.put_principal(conn, "rights-ops", [store.ensure_constraint(conn, *RIGHTS)])
        store.put_principal(conn, "ops-lead",
                            [store.ensure_constraint(conn, *RIGHTS),
                             store.ensure_constraint(conn, *SCHED)])

        self.source.add("kb:KB-0001", [])            # public runbook
        self.source.add("kb:KB-0004", [RIGHTS])      # rights-restricted runbook
        self.source.add("jira:MEDIA-113", [SCHED])   # scheduling-restricted ticket
        syncmod.sync(self.source, conn=conn)

        self.records = {
            "fp-epg": self._get_or_store("fp-epg",
                {"kind": "executed_fix", "class_key": "publisher|PUB-4012|schedule_item",
                 "fingerprint": "fp-epg",
                 "body": {"symptom": "EPG publish failed — missing episode metadata",
                          "fix": "correct metadata, republish EPG payload"}}, ["kb:KB-0001"]),
            "fp-rights": self._get_or_store("fp-rights",
                {"kind": "executed_fix", "class_key": "rights|RGT-EXCL-009|vod_item",
                 "fingerprint": "fp-rights",
                 "body": {"symptom": "VOD title live outside licence window",
                          "fix": "RESTRICTED — takedown + republish per rights runbook"}},
                ["kb:KB-0004", "jira:MEDIA-113"]),
            "fp-sched": self._get_or_store("fp-sched",
                {"kind": "executed_fix", "class_key": "scheduler|SCH-DUP-002|schedule_item",
                 "fingerprint": "fp-sched",
                 "body": {"symptom": "duplicate schedule slot", "fix": "dedupe overlapping slot"}},
                ["jira:MEDIA-113"]),
        }

        self.incidents = [
            {"incident_id": "INC-1", "service": "publisher", "fingerprint": "fp-epg",
             "class_key": "publisher|PUB-4012|schedule_item", "status": "detected",
             "current_step": "detected"},
            {"incident_id": "INC-2", "service": "scheduler", "fingerprint": "fp-sched",
             "class_key": "scheduler|SCH-DUP-002|schedule_item", "status": "detected",
             "current_step": "detected"},
            {"incident_id": "INC-3", "service": "rights", "fingerprint": "fp-rights",
             "class_key": "rights|RGT-EXCL-009|vod_item", "status": "detected",
             "current_step": "detected"},
        ]
        # seed ladder levels (L1 Recommend by default; a human Promotes on stage)
        for inc in self.incidents:
            if self.conn.execute("SELECT 1 FROM class_ladder WHERE class_key=?",
                                 (inc["class_key"],)).fetchone() is None:
                self._set_ladder(inc["class_key"], "L1", None)
        self._trace("system", "seeded local-demo state (systems simulated, content real)")

    # ------------------------------------------------------------------ #
    # Internal helpers (callers hold the lock)
    # ------------------------------------------------------------------ #
    def _trace(self, step: str, detail: str, incident_id: str | None = None) -> None:
        self.trace.append({"ts": db.utcnow_iso(), "incident_id": incident_id,
                           "step": step, "detail": detail})

    def _ladder(self, class_key: str) -> str:
        row = self.conn.execute(
            "SELECT level FROM class_ladder WHERE class_key = ?", (class_key,)).fetchone()
        return row["level"] if row else "L1"

    def _set_ladder(self, class_key: str, level: str, principal: str | None) -> None:
        # `level` is ALWAYS the canonical token ("STANDING", "L1", ...), never display text.
        self.conn.execute(
            "INSERT INTO class_ladder(class_key, level, promoted_by, promoted_at) "
            "VALUES(?,?,?,?) ON CONFLICT(class_key) DO UPDATE SET level=excluded.level, "
            "promoted_by=excluded.promoted_by, promoted_at=excluded.promoted_at",
            (class_key, level, principal, db.utcnow_iso()))
        self.conn.commit()

    def _incident(self, incident_id: str) -> dict | None:
        return next((i for i in self.incidents if i["incident_id"] == incident_id), None)

    def _elapsed_seconds(self) -> float:
        start = db.parse_iso(self.demo_started_at)
        if start is None:
            return 0.0
        return max(0.0, (db.utcnow() - start).total_seconds())

    def _ttr_seconds(self, incident_id: str) -> float | None:
        """Per-incident time-to-resolution, measured from the REAL audit rows: from the
        `detected` event to the terminal (`verified`/`memory_stored`/`rolled_back`) event.
        None until the incident has been driven to a terminal state (P1.7 TTR chip)."""
        rows = self.conn.execute(
            "SELECT event_type, ts FROM audit_log WHERE payload LIKE ? ORDER BY seq",
            (f'%"{incident_id}"%',),
        ).fetchall()
        detected = next((r["ts"] for r in rows if r["event_type"] == "detected"), None)
        done = None
        for r in rows:
            if r["event_type"] in ("verified", "memory_stored", "rolled_back"):
                done = r["ts"]
        d0, d1 = db.parse_iso(detected), db.parse_iso(done)
        if d0 is None or d1 is None:
            return None
        return round(max(0.0, (d1 - d0).total_seconds()), 1)

    def _closed_count(self) -> int:
        """Cumulative count of fixes Precedent verified-closed this session (P1.7 close strip)."""
        return self.conn.execute(
            "SELECT COUNT(*) c FROM audit_log WHERE event_type = 'verified'").fetchone()["c"]

    # ------------------------------------------------------------------ #
    # Read surfaces
    # ------------------------------------------------------------------ #
    def snapshot(self) -> dict:
        with self._lock:
            incidents = []
            for inc in self.incidents:
                rid = self.records.get(inc["fingerprint"])
                allowed, owner = (True, None)
                if rid is not None:
                    allowed, owner = retrieve.check_access(
                        self.conn, self.principal, rid, self.retrieval_mode)
                level = self._ladder(inc["class_key"])
                incidents.append({
                    **inc,
                    "ladder_level": level,                       # canonical token
                    "ladder_level_label": level_label(level),    # display only
                    "access": "permitted" if allowed else "denied",
                    "denied_owner_team": owner,
                    "ttr_seconds": self._ttr_seconds(inc["incident_id"]),   # P1.7 TTR chip
                })
            precedents = self.conn.execute(
                "SELECT COUNT(*) c FROM memory_record").fetchone()["c"]
            return {
                "title": "Precedent",
                "principal": self.principal,
                "retrieval_mode": self.retrieval_mode,
                "demo_started_at": self.demo_started_at,
                "elapsed_seconds": round(self._elapsed_seconds(), 1),
                "baseline": {"seconds": BASELINE_SECONDS, "label": BASELINE_LABEL_SHORT,
                             "source_label": BASELINE_SOURCE_LABEL},
                "incidents": incidents,
                "ladder_top_token": STANDING,
                "ladder_top_label": LEVEL_LABELS[STANDING],
                "precedents_count": precedents,
                "robustness": _ROBUSTNESS,          # P1.7 robustness chip (committed source)
                "closed_count": self._closed_count(),   # P1.7 cumulative close strip
                "status": {
                    "memory": "ready",
                    "sync": ("Local Jira-shaped source (offline demo)"
                             if self.sync_available else "degraded — fail-closed"),
                    "console": "ready",
                    "jira_mode": "local-fake",
                    "audit_chain": "intact" if audit.verify_chain(conn=self.conn) else "BROKEN",
                    "permission_flip": "on" if self.flip_on else "off",
                },
            }

    def events(self, limit: int = 50) -> dict:
        with self._lock:
            rows = self.conn.execute(
                "SELECT seq, ts, actor, event_type, payload FROM audit_log "
                "ORDER BY seq DESC LIMIT ?", (limit,)).fetchall()
            auditlog = [{"seq": r["seq"], "ts": r["ts"], "actor": r["actor"],
                         "event_type": r["event_type"], "payload": r["payload"],
                         "seed": r["actor"] in ("demo-seed", "sync")} for r in rows]
            return {"trace": self.trace[-limit:], "audit": auditlog,
                    "audit_chain": "intact" if audit.verify_chain(conn=self.conn) else "BROKEN"}

    # ------------------------------------------------------------------ #
    # Control surfaces (all delegate access decisions to precedent_memory)
    # ------------------------------------------------------------------ #
    def triage(self, incident_id: str) -> dict:
        with self._lock:
            inc = self._incident(incident_id)
            if inc is None:
                return {"error": "unknown incident"}
            self._trace("detect", f"{inc['service']} incident detected", incident_id)
            self._trace("permission_check", f"retrieving as {self.principal}", incident_id)
            bundle = retrieve.retrieve(self.principal, {"incident_id": incident_id,
                                                        "fingerprint": inc["fingerprint"]},
                                       mode=self.retrieval_mode, conn=self.conn)
            self.conn.commit()
            if bundle.hits:
                inc["status"], inc["current_step"] = "fix_found", "retrieve"
                self._trace("retrieve", f"documented fix retrieved ({len(bundle.hits)} hit)",
                            incident_id)
                return {"result": "permitted", "hits": [h.record_id for h in bundle.hits],
                        "denied_count": bundle.denied_count}
            inc["status"], inc["current_step"] = "refused", "refused"
            self._trace("refused",
                        f"restricted — {bundle.denied_count} remediation hidden; "
                        f"owner: {bundle.denied_owner_team or 'restricted team'}", incident_id)
            return {"result": "refused", "denied_count": bundle.denied_count,
                    "denied_owner_team": bundle.denied_owner_team, "hits": []}

    def approve(self, incident_id: str, principal: str | None = None) -> dict:
        with self._lock:
            principal = principal or self.principal
            inc = self._incident(incident_id)
            if inc is None:
                return {"error": "unknown incident"}
            audit.audit("approval_recorded", conn=self.conn, actor=principal,
                        incident_id=incident_id, decision="approve", class_key=inc["class_key"])
            self.conn.commit()
            inc["status"], inc["current_step"] = "approved", "approved"
            self._trace("approval", f"approved by {principal}", incident_id)
            return {"ok": True, "approver": principal}

    def promote(self, class_key: str, principal: str | None = None) -> dict:
        with self._lock:
            principal = principal or self.principal
            self._set_ladder(class_key, STANDING, principal)   # canonical token in DB
            audit.audit("promoted_standing_approval", conn=self.conn, actor=principal,
                        class_key=class_key, level=STANDING)
            self.conn.commit()
            self._trace("promote", f"{class_key} → {LEVEL_LABELS[STANDING]} (by {principal})")
            return {"ok": True, "class_key": class_key, "level": STANDING,
                    "level_label": LEVEL_LABELS[STANDING]}

    def revoke(self, class_key: str, principal: str | None = None) -> dict:
        with self._lock:
            principal = principal or self.principal
            self._set_ladder(class_key, "L1", principal)
            audit.audit("revoked_standing_approval", conn=self.conn, actor=principal,
                        class_key=class_key, level="L1")
            self.conn.commit()
            self._trace("revoke", f"{class_key} → L1 (revoked by {principal})")
            return {"ok": True, "class_key": class_key, "level": "L1", "level_label": "L1"}

    def permission_flip(self, on: bool | None = None) -> dict:
        """LOCAL-DEMO ONLY: simulate a Jira permission change by tightening the
        scheduling ticket to ALSO require Rights Ops, then sync. A record readable
        by the scheduling principal goes dark (conjunction). Reversible."""
        with self._lock:
            on = (not self.flip_on) if on is None else bool(on)
            if on:
                self.source.flip_add("jira:MEDIA-113", RIGHTS)
            else:
                self.source.flip_remove("jira:MEDIA-113", RIGHTS)
            result = syncmod.sync(self.source, conn=self.conn)
            self.conn.commit()
            self.flip_on = on
            self.sync_available = result.get("available", True)
            rid = self.records["fp-sched"]
            allowed, owner = retrieve.check_access(self.conn, self.principal, rid,
                                                   self.retrieval_mode)
            self._trace("permission_flip",
                        f"local-demo Jira flip {'ON' if on else 'OFF'} → "
                        f"scheduler fix now {'DENIED' if not allowed else 'permitted'}")
            return {"ok": True, "flip_on": on,
                    "scheduler_fix_access": "permitted" if allowed else "denied",
                    "denied_owner_team": owner}

    def push_trace(self, event: dict) -> dict:
        """T1 integration seam: append an execution-loop trace event."""
        with self._lock:
            self._trace(str(event.get("step", "step")), str(event.get("detail", "")),
                        event.get("incident_id"))
            return {"ok": True}


# WP-HOST-SESSION: the process-wide ``STATE = DemoState()`` singleton was RETIRED. It made every
# hosted visitor share one memory db (ladder + audit chain), so visitor A's promote/drive leaked
# into B. The served app now builds one DemoState PER browser session (console/session.py); the
# only remaining module-level ``STATE`` names live in console/app.py and scripts/demo_server.py
# as an OPT-IN test pin (default None) — production never shares a mutable DemoState across
# sessions. Non-served callers construct ``DemoState(db_path=...)`` explicitly.
