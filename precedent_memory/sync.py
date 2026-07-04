"""ACL sync — versioned polling, fail-closed fallback.  [owner T2, task T2-2]

Spec: Idea/refinement/02-architecture-refinement.md §2.5.

A permission SOURCE (real Jira, or the in-process fake used by tests and the local
demo) is polled for the current ACL state of each runbook/source. Each observed
state is upserted into acl_source; a real change bumps acl_version and fans out an
effective_policy recompile over every derived record (idx_lineage_source). Repeated
identical observations are no-ops (idempotent).

Fail-closed: when the source is UNAVAILABLE, restricted sources have their freshness
marked unknown so restricted memory goes dark until a successful sync restores it —
a stale cache narrows access, never widens it. Public memory keeps serving.

RULE 1/2: no model ids, no LLM imports — deterministic sync only.
"""
from __future__ import annotations

import json
import os

import httpx

from precedent_memory import audit, db, store


class PermissionSourceUnavailable(Exception):
    """Raised by a source's snapshot() when it cannot be reached (Jira down, no
    creds). Triggers the fail-closed path."""


# --------------------------------------------------------------------------- #
# Sources
# --------------------------------------------------------------------------- #
class FakePermissionSource:
    """In-process permission source for tests and the local console demo.

    Constraints are expressed as (source_system, external_ref, description) tuples
    so the sync maps them to constraint_def bit ids exactly like a live source would.
    """

    def __init__(self) -> None:
        self._sources: dict[str, dict] = {}
        self.available = True

    def add(self, ref: str, constraints=(), revoked: int = 0) -> None:
        self._sources[ref] = {"constraints": [tuple(c) for c in constraints],
                              "revoked": int(revoked)}

    def flip_add(self, ref: str, constraint) -> None:
        """Simulate 'a Jira permission was tightened' — add a constraint to a source."""
        c = tuple(constraint)
        cons = self._sources.setdefault(ref, {"constraints": [], "revoked": 0})["constraints"]
        if c not in cons:
            cons.append(c)

    def flip_remove(self, ref: str, constraint) -> None:
        """Simulate 'a Jira permission was relaxed' — remove a constraint."""
        c = tuple(constraint)
        spec = self._sources.get(ref)
        if spec and c in spec["constraints"]:
            spec["constraints"].remove(c)

    def revoke(self, ref: str) -> None:
        self._sources.setdefault(ref, {"constraints": [], "revoked": 0})["revoked"] = 1

    def set_available(self, value: bool) -> None:
        self.available = bool(value)

    def snapshot(self) -> dict:
        if not self.available:
            raise PermissionSourceUnavailable("fake permission source offline")
        now = db.utcnow_iso()
        return {
            ref: {"constraints": spec["constraints"], "last_verified_at": now,
                  "revoked": spec["revoked"]}
            for ref, spec in self._sources.items()
        }


class JiraPermissionSource:
    """Live Jira Service Management ACL source (httpx-backed, guarded, fail-closed).

    Reads the ISSUE-SECURITY level of each tracked runbook issue over the REST API
    and maps it to a constraint the memory layer enforces — the dual-enforcement
    story (Jira hides the issue; Precedent denies the derived memory). Credentials
    come from the environment by NAME only; a token is used solely to build the
    Basic-auth client and is NEVER logged or embedded in an error message.

    Configuration (env):
      JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY   (required)
      JIRA_RUNBOOK_ISSUES = "kb:KB-0004=MEDIA-113,jira:MEDIA-114=MEDIA-114"  (ref=issueKey list)
      JIRA_SECURITY_LEVEL_RIGHTS_OPS / _SCHEDULING_OPS   (level id -> owner-team label)

    Documented response assumption (Jira Cloud v3):
      GET /rest/api/3/issue/{key}?fields=security ->
        {"fields": {"security": {"id": "10000", "name": "Rights Ops Only"} | null}}

    Fail-closed: not configured -> raise; any HTTP/auth/timeout/malformed response ->
    raise PermissionSourceUnavailable (sync then denies restricted memory). A 404 on
    a tracked issue marks that source revoked (it too fails closed). Tests inject an
    httpx.Client(transport=httpx.MockTransport(...)); normal tests never hit network.
    """

    ENV = ("JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN", "JIRA_PROJECT_KEY")

    def __init__(self, env: dict | None = None, *, client: httpx.Client | None = None,
                 runbooks: dict | None = None, level_owner: dict | None = None,
                 timeout: float = 3.0) -> None:
        self._env = env if env is not None else os.environ
        self._client = client                     # injectable for tests (MockTransport)
        self._timeout = timeout
        self._runbooks = runbooks if runbooks is not None else self._parse_runbooks()
        self._level_owner = level_owner if level_owner is not None else self._parse_level_owner()

    @property
    def configured(self) -> bool:
        return all(self._env.get(name) for name in self.ENV)

    def _parse_runbooks(self) -> dict:
        out: dict[str, str] = {}
        for part in (self._env.get("JIRA_RUNBOOK_ISSUES") or "").split(","):
            part = part.strip()
            if "=" in part:
                ref, key = part.split("=", 1)
                out[ref.strip()] = key.strip()
        return out

    def _parse_level_owner(self) -> dict:
        out: dict[str, str] = {}
        if self._env.get("JIRA_SECURITY_LEVEL_RIGHTS_OPS"):
            out[str(self._env["JIRA_SECURITY_LEVEL_RIGHTS_OPS"])] = "Rights Ops"
        if self._env.get("JIRA_SECURITY_LEVEL_SCHEDULING_OPS"):
            out[str(self._env["JIRA_SECURITY_LEVEL_SCHEDULING_OPS"])] = "Scheduling Ops"
        return out

    def _make_client(self) -> tuple[httpx.Client, bool]:
        if self._client is not None:
            return self._client, False
        return httpx.Client(
            base_url=self._env["JIRA_BASE_URL"].rstrip("/"),
            auth=(self._env["JIRA_EMAIL"], self._env["JIRA_API_TOKEN"]),
            timeout=self._timeout, headers={"Accept": "application/json"},
        ), True

    def snapshot(self) -> dict:
        if not self.configured:
            raise PermissionSourceUnavailable(
                "Jira not configured (missing credentials) — failing closed")
        client, owns = self._make_client()
        out: dict[str, dict] = {}
        try:
            for ref, issue_key in self._runbooks.items():
                resp = client.get(f"/rest/api/3/issue/{issue_key}",
                                  params={"fields": "security"})
                if resp.status_code == 404:
                    out[ref] = {"constraints": [], "last_verified_at": db.utcnow_iso(),
                                "revoked": 1}
                    continue
                resp.raise_for_status()
                sec = ((resp.json() or {}).get("fields") or {}).get("security")
                if sec:
                    lvl = str(sec.get("id"))
                    owner = self._level_owner.get(lvl) or sec.get("name") or f"Security {lvl}"
                    constraints = [("jira", f"issue-security:{lvl}", owner)]
                else:
                    constraints = []
                out[ref] = {"constraints": constraints, "last_verified_at": db.utcnow_iso(),
                            "revoked": 0}
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
            # Type name only — never leak the token, URL or response body.
            raise PermissionSourceUnavailable(
                f"Jira read failed — failing closed ({type(exc).__name__})") from None
        finally:
            if owns:
                client.close()
        return out


# --------------------------------------------------------------------------- #
# sync()  — one poll tick
# --------------------------------------------------------------------------- #
def sync(source, *, conn) -> dict:
    """Poll `source`, apply ACL changes idempotently, fan out recompiles, audit.
    Returns a status dict. On source unavailability, fails closed and returns
    {"available": False, ...}. Never raises for a normal outage."""
    if conn is None:
        raise ValueError("sync() requires a conn")
    try:
        snap = source.snapshot()
    except PermissionSourceUnavailable as exc:
        return _fail_closed(conn, reason=str(exc))

    changed: list[str] = []
    for ref, spec in snap.items():
        cids = [store.ensure_constraint(conn, *c) for c in spec.get("constraints", [])]
        res = store.put_source(conn, ref, cids,
                               last_verified_at=spec.get("last_verified_at"),
                               revoked=int(spec.get("revoked", 0)))
        if res["changed"]:
            affected = store.recompile_for_source(conn, res["id"])
            audit.audit("acl_sync_applied", conn=conn, actor="sync", source=ref,
                        revoked=int(spec.get("revoked", 0)), records=len(affected))
            changed.append(ref)
    return {"available": True, "sources": list(snap), "changed": changed}


def refresh_cached_freshness(conn) -> int:
    """Re-affirm the CURRENTLY-cached ACLs as fresh: re-stamp every non-revoked acl_source's
    last_verified_at to now and recompile its records, so restricted-but-authorised memory stays
    readable in live mode instead of ageing past the freshness window.

    This is the standalone-agent equivalent of the console's periodic sync loop (a write-behind
    cache heartbeat) for the airplane-mode demo, where the local seeded store IS the source of
    truth. It NEVER touches revoked sources (they stay dark — fail-closed preserved) and never
    changes any constraint set — only the freshness stamp. Returns the number of sources refreshed.
    """
    if conn is None:
        raise ValueError("refresh_cached_freshness() requires a conn")
    now = db.utcnow_iso()
    refreshed = 0
    for s in conn.execute("SELECT id FROM acl_source WHERE revoked = 0").fetchall():
        conn.execute("UPDATE acl_source SET last_verified_at = ? WHERE id = ?", (now, s["id"]))
        store.recompile_for_source(conn, s["id"])
        refreshed += 1
    conn.commit()
    return refreshed


def _fail_closed(conn, reason: str) -> dict:
    """Source unreachable: mark every RESTRICTED source's freshness unknown so its
    derived memory is denied in live mode; recompile; audit. Public memory is left
    serving (its records are not freshness-gated)."""
    darkened: list[str] = []
    for s in conn.execute("SELECT id, external_ref, constraint_ids FROM acl_source").fetchall():
        if json.loads(s["constraint_ids"] or "[]"):
            conn.execute("UPDATE acl_source SET last_verified_at = '' WHERE id = ?", (s["id"],))
            store.recompile_for_source(conn, s["id"])
            darkened.append(s["external_ref"])
    audit.audit("sync_unavailable", conn=conn, actor="sync", reason=reason,
                darkened=len(darkened))
    return {"available": False, "reason": reason, "darkened": darkened}
