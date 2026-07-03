"""Deterministic conformance-bench topology (BasedAI protocol: 5 levels / 20 roles /
1,000 ACL-tagged docs / 40 principals).  [owner T3, task T3-2]

Spec: Idea/refinement/02-architecture-refinement.md §2.7.

Two layers, on purpose:

  build_manifest(seed) -> Manifest   PURE, deterministic. A manifest is a total function
      of CANONICAL_SEED: the 20 role-constraints, the 40 principals with their granted role
      sets, and the 1,000 docs with their required-role sets + fail-closed flags + lineage.
      It carries NO wall-clock — freshness is expressed as a deterministic offset in seconds
      so two runs produce a byte-identical manifest (see manifest_digest()).  The manifest is
      ALSO the ground-truth corpus: it records each principal's clearance as a plain int set,
      which is exactly the independent oracle's principal input (the oracle never reads the
      grant bitmap).

  realize(conn, manifest, run_now) -> Realization   Writes the manifest into a real memory DB
      through the PRODUCT write API (store.*), so compile_effective_policy populates
      required_bits for every restricted doc exactly as production would.  The ONLY run-varying
      field is acl_source.last_verified_at (= run_now - freshness_offset), because freshness is
      a wall-clock concept; every allow/deny LABEL is nonetheless stable because "fresh" docs are
      milliseconds old and "stale" docs are two hours old — never near the 60 s boundary.

Fail-closed coverage is baked into the 1,000 docs: revoked sources, stale sources, unverified
provenance, and tombstoned records are all represented so the bench exercises every deny path.
"""
from __future__ import annotations

import random
from dataclasses import dataclass

from precedent_memory import db, store
from precedent_memory.bench.seed import CANONICAL_SEED

# --------------------------------------------------------------------------- #
# Protocol dimensions (BasedAI published test protocol, 02 §2.7)
# --------------------------------------------------------------------------- #
N_LEVELS = 5
N_ROLES = 20            # 4 roles per hierarchy level
N_PRINCIPALS = 40
N_DOCS = 1000

STALE_OFFSET_S = 7200   # 2 h in the past — unambiguously outside the 60 s freshness window
FRESH_OFFSET_S = 0      # "now" at realize time — milliseconds old at grade time

# 20 owner-team labels (surfaced as the safe denial disclosure), 4 per level.
_TEAMS = (
    "Rights Ops", "Scheduling Ops", "Publishing Ops", "Catalog Ops",
    "Finance Ops", "Legal Ops", "Security Ops", "Platform Ops",
    "Data Ops", "Content Ops", "Partner Ops", "Compliance Ops",
    "Localization Ops", "Ads Ops", "Trust & Safety", "Billing Ops",
    "Identity Ops", "Network Ops", "Release Ops", "Support Ops",
)

# Doc-category population over the 1,000 docs (sums to N_DOCS). Every category except
# 'public' is restricted, so effective_policy.required_bits is populated for 850 docs.
_CATEGORY_PLAN: tuple[tuple[str, int], ...] = (
    ("public", 150),       # required = {}  -> readable by anyone
    ("single", 320),       # one required role
    ("multi", 180),        # 2-3 required roles (conjunction across a source's constraints)
    ("derived", 150),      # lineage spans 2-3 sources -> required = union (Tier-C derived memory)
    ("revoked", 60),       # a revoked lineage source -> deny all (fail closed)
    ("stale", 50),         # freshness older than the window -> deny all restricted (fail closed)
    ("unverified", 40),    # unknown-provenance lineage -> sentinel constraint -> deny all
    ("tombstoned", 50),    # record status != active -> deny all
)


@dataclass(frozen=True)
class RoleSpec:
    index: int             # 0..19, stable role identity in the manifest
    level: int             # 0..4 hierarchy level
    external_ref: str      # constraint_def.external_ref, e.g. "role:L0-rights-ops"
    owner_team: str        # constraint_def.description == safe denial label


@dataclass(frozen=True)
class PrincipalSpec:
    external_id: str
    role_indices: tuple[int, ...]   # sorted; the principal's granted role set (ground truth)


@dataclass(frozen=True)
class DocSpec:
    index: int
    category: str
    role_indices: tuple[int, ...]        # required roles imposed by this doc's OWN source
    source_ref: str                      # this doc's acl_source external_ref
    lineage_refs: tuple[str, ...]        # sources the derived record cites (>=1)
    revoked: bool
    freshness_offset_s: int              # 0 fresh, STALE_OFFSET_S stale
    initial_status: str                  # 'active' | 'tombstoned'
    class_key: str


@dataclass(frozen=True)
class Manifest:
    seed: int
    roles: tuple[RoleSpec, ...]
    principals: tuple[PrincipalSpec, ...]
    docs: tuple[DocSpec, ...]

    def restricted_doc_indices(self) -> tuple[int, ...]:
        return tuple(d.index for d in self.docs if d.category != "public")

    def principal_role_ids(self, realization: Realization, ext_id: str) -> frozenset[int]:
        """The principal's granted CONSTRAINT ids (constraint_def.id) as a plain set — the
        oracle's clearance input.  Mapped from role indices via the realization, never from
        the grant bitmap."""
        spec = realization.principal_by_id[ext_id]
        return frozenset(realization.role_constraint_id[i] for i in spec.role_indices)


@dataclass
class Realization:
    run_now_iso: str
    role_constraint_id: dict[int, int]        # role index -> constraint_def.id
    record_id: dict[int, int]                 # doc index -> memory_record.id
    principal_by_id: dict[str, PrincipalSpec]


# --------------------------------------------------------------------------- #
# build_manifest — the deterministic core
# --------------------------------------------------------------------------- #
def build_manifest(seed: int = CANONICAL_SEED) -> Manifest:
    """Total function of `seed`. RNG is consumed in a FIXED order so the manifest is
    byte-identical across runs (proven by manifest_digest())."""
    rng = random.Random(seed)

    roles = tuple(
        RoleSpec(
            index=i,
            level=i // (N_ROLES // N_LEVELS),
            external_ref=f"role:L{i // (N_ROLES // N_LEVELS)}-{_slug(_TEAMS[i])}",
            owner_team=_TEAMS[i],
        )
        for i in range(N_ROLES)
    )

    principals = _build_principals(rng)
    docs = _build_docs(rng)
    return Manifest(seed=seed, roles=roles, principals=principals, docs=docs)


def _slug(team: str) -> str:
    return team.lower().replace(" & ", "-").replace(" ", "-")


def _build_principals(rng: random.Random) -> tuple[PrincipalSpec, ...]:
    """40 principals: 3 admins (all roles), 2 nobody (no roles), 35 regulars (each role held
    with p=0.3). Guarantees a populous allow pool (admins/public) AND a populous deny pool
    (under-privileged principals)."""
    out: list[PrincipalSpec] = []
    for i in range(N_PRINCIPALS):
        if i < 3:
            roles = tuple(range(N_ROLES))                      # admin
        elif i < 5:
            roles = ()                                          # nobody
        else:
            roles = tuple(r for r in range(N_ROLES) if rng.random() < 0.30)
        out.append(PrincipalSpec(external_id=f"prin-{i:03d}", role_indices=roles))
    return tuple(out)


def _build_docs(rng: random.Random) -> tuple[DocSpec, ...]:
    docs: list[DocSpec] = []
    categories: list[str] = []
    for name, count in _CATEGORY_PLAN:
        categories.extend([name] * count)
    assert len(categories) == N_DOCS, (len(categories), N_DOCS)
    # Shuffle category assignment deterministically so categories interleave across doc ids.
    rng.shuffle(categories)

    # First pass fixes each doc's OWN required-role set + source ref, so derived docs (second
    # pass) can cite already-decided source refs.
    own_roles: dict[int, tuple[int, ...]] = {}
    source_ref: dict[int, str] = {}
    for idx in range(N_DOCS):
        cat = categories[idx]
        source_ref[idx] = f"kb:DOC-{idx:04d}"
        if cat == "public":
            own_roles[idx] = ()
        elif cat in ("single", "revoked", "stale", "tombstoned"):
            own_roles[idx] = (rng.randrange(N_ROLES),)
        elif cat == "multi":
            k = rng.choice((2, 3))
            own_roles[idx] = tuple(sorted(rng.sample(range(N_ROLES), k)))
        elif cat == "derived":
            own_roles[idx] = (rng.randrange(N_ROLES),)
        elif cat == "unverified":
            own_roles[idx] = ()           # no own source is created; lineage is an unknown ref
        else:  # pragma: no cover - guarded by the plan
            raise AssertionError(cat)

    for idx in range(N_DOCS):
        cat = categories[idx]
        roles = own_roles[idx]
        if cat == "unverified":
            lineage = (f"unknown:PROVENANCE-{idx:04d}",)          # store -> sentinel -> deny
        elif cat == "derived":
            # cite this doc's own source + 1-2 OTHER docs' sources (union of their roles).
            others = _pick_other_sources(rng, idx, source_ref)
            lineage = (source_ref[idx],) + others
        else:
            lineage = (source_ref[idx],)
        docs.append(
            DocSpec(
                index=idx,
                category=cat,
                role_indices=roles,
                source_ref=source_ref[idx],
                lineage_refs=lineage,
                revoked=(cat == "revoked"),
                freshness_offset_s=STALE_OFFSET_S if cat == "stale" else FRESH_OFFSET_S,
                initial_status="tombstoned" if cat == "tombstoned" else "active",
                class_key=f"svc{idx % 7}|CODE-{idx:04d}|obj{idx % 5}",
            )
        )
    return tuple(docs)


def _pick_other_sources(rng: random.Random, idx: int,
                        source_ref: dict[int, str]) -> tuple[str, ...]:
    k = rng.choice((1, 2))
    picks: list[str] = []
    for _ in range(k):
        j = rng.randrange(N_DOCS)
        if j != idx:
            picks.append(source_ref[j])
    return tuple(picks)


# --------------------------------------------------------------------------- #
# Serialization — for the byte-identical reproducibility test
# --------------------------------------------------------------------------- #
def manifest_to_dict(m: Manifest) -> dict:
    return {
        "seed": m.seed,
        "roles": [
            {"index": r.index, "level": r.level, "external_ref": r.external_ref,
             "owner_team": r.owner_team}
            for r in m.roles
        ],
        "principals": [
            {"external_id": p.external_id, "role_indices": list(p.role_indices)}
            for p in m.principals
        ],
        "docs": [
            {"index": d.index, "category": d.category, "role_indices": list(d.role_indices),
             "source_ref": d.source_ref, "lineage_refs": list(d.lineage_refs),
             "revoked": d.revoked, "freshness_offset_s": d.freshness_offset_s,
             "initial_status": d.initial_status, "class_key": d.class_key}
            for d in m.docs
        ],
    }


def manifest_digest(m: Manifest) -> str:
    """Canonical JSON of the manifest — identical across two runs at the same seed."""
    return db.canonical_json(manifest_to_dict(m))


# --------------------------------------------------------------------------- #
# realize — write the manifest into a real memory DB via the product API
# --------------------------------------------------------------------------- #
def realize(conn, manifest: Manifest, run_now=None) -> Realization:
    run_now = run_now or db.utcnow()
    run_now_iso = run_now.isoformat()

    role_constraint_id: dict[int, int] = {}
    for r in manifest.roles:
        role_constraint_id[r.index] = store.ensure_constraint(
            conn, "role", r.external_ref, r.owner_team)

    for p in manifest.principals:
        cids = [role_constraint_id[i] for i in p.role_indices]
        store.put_principal(conn, p.external_id, cids)

    # Pass 1: create every doc's OWN acl_source first, so derived-doc lineage refs resolve to
    # real sources (not to auto-created unverified sentinels).
    from datetime import timedelta
    for d in manifest.docs:
        if d.category == "unverified":
            continue  # intentionally no own source; the unknown lineage ref becomes a sentinel
        cids = [role_constraint_id[i] for i in d.role_indices]
        lv = (run_now - timedelta(seconds=d.freshness_offset_s)).isoformat()
        store.put_source(conn, d.source_ref, cids, last_verified_at=lv,
                         revoked=1 if d.revoked else 0)

    # Pass 2: store every record with its lineage; compile_effective_policy runs inside store().
    record_id: dict[int, int] = {}
    for d in manifest.docs:
        body = {"kind": "executed_fix", "class_key": d.class_key,
                "summary": f"synthetic bench doc {d.index}", "category": d.category}
        rid = store.store(body, list(d.lineage_refs), conn=conn)
        record_id[d.index] = rid
        if d.initial_status != "active":
            conn.execute("UPDATE memory_record SET status = ? WHERE id = ?",
                         (d.initial_status, rid))
    conn.commit()

    return Realization(
        run_now_iso=run_now_iso,
        role_constraint_id=role_constraint_id,
        record_id=record_id,
        principal_by_id={p.external_id: p for p in manifest.principals},
    )
