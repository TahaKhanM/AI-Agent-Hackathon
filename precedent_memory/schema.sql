-- precedent_memory schema — from Idea/refinement/02-architecture-refinement.md §2.3.
-- Starter file written during planning so T2 begins from a fixed schema, not a blank file.
-- Every field earns its place; the compiled effective_policy table is the P99 fast path.

-- Principals & grants (synced from Jira project roles + issue-security levels + KB restrictions)
CREATE TABLE IF NOT EXISTS principal (
  id INTEGER PRIMARY KEY,
  external_id TEXT UNIQUE,                              -- Jira accountId / agent identity / ASI:One sender address
  kind TEXT CHECK(kind IN ('human','agent','service')),
  grant_bits BLOB NOT NULL                              -- precomputed bitmap of constraint-ids this principal satisfies (B fast path)
);

-- One row per access constraint discovered in a source system
CREATE TABLE IF NOT EXISTS constraint_def (
  id INTEGER PRIMARY KEY,                               -- bit position in bitmaps
  source_system TEXT, external_ref TEXT,                -- e.g. 'jira','RIGHTS project role=rights-ops','issue-security:10000'
  description TEXT, UNIQUE(source_system, external_ref)
);

-- Source artifacts (KB articles, tickets, runbook issues) and their current ACL state
CREATE TABLE IF NOT EXISTS acl_source (
  id INTEGER PRIMARY KEY, external_ref TEXT UNIQUE,     -- e.g. 'kb:KB-0042', 'jira:MEDIA-113'
  constraint_ids JSON NOT NULL,                         -- constraints this source imposes ([] = public)
  acl_version INTEGER NOT NULL DEFAULT 0,               -- bumped by sync on every observed change
  last_verified_at TEXT NOT NULL,                       -- freshness input to the fail-closed rule
  revoked INTEGER NOT NULL DEFAULT 0
);

-- Memory records: executed-fix-with-provenance + KB summaries + dossiers
CREATE TABLE IF NOT EXISTS memory_record (
  id INTEGER PRIMARY KEY, kind TEXT,                    -- 'executed_fix','kb_summary','dossier'
  class_key TEXT, fingerprint TEXT,
  body JSON NOT NULL,                                   -- symptom, fix steps, approver, risk class, rollback, outcome
  status TEXT NOT NULL DEFAULT 'active'
    CHECK(status IN ('active','quarantined','tombstoned'))
);
CREATE TABLE IF NOT EXISTS lineage (
  record_id INT, source_id INT, source_content_hash TEXT,
  PRIMARY KEY(record_id, source_id)
);

-- B: the compiled effective policy — retrieval touches ONLY this table
CREATE TABLE IF NOT EXISTS effective_policy (
  record_id INTEGER PRIMARY KEY REFERENCES memory_record(id),
  required_bits BLOB NOT NULL,       -- union of constraint-ids across ALL lineage sources (conjunction, A)
  is_restricted INTEGER NOT NULL,    -- 0 iff required_bits is empty
  policy_version INTEGER NOT NULL,   -- monotonic; bumped on every recompile
  min_source_freshness TEXT NOT NULL,-- oldest last_verified_at across lineage (fail-closed input)
  compiled_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_lineage_source ON lineage(source_id);  -- revocation fan-out = one indexed scan

-- Embedding index rows carry NO independent access; joined to effective_policy at query time
CREATE TABLE IF NOT EXISTS embedding_index (
  record_id INTEGER PRIMARY KEY, vector BLOB, model TEXT
);

-- Hash-chained audit log (retrievals, denials, sync events, executions, promotions/demotions, redactions)
CREATE TABLE IF NOT EXISTS audit_log (
  seq INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, actor TEXT, event_type TEXT,
  payload JSON,                       -- the SOC 2 five elements live here
  prev_hash TEXT NOT NULL, hash TEXT NOT NULL           -- sha256(prev_hash || canonical_json(row))
);

-- C: governed redacted derivatives (stub — full design in 02 §2.6)
CREATE TABLE IF NOT EXISTS redaction_derivative (
  id INTEGER PRIMARY KEY, derived_record_id INT, original_record_id INT,
  included_source_hashes JSON, excluded_source_hashes JSON,
  attestation JSON, approved_by INT REFERENCES principal(id),
  audit_seq INT REFERENCES audit_log(seq)
);

-- Per-class autonomy ladder state (graduation counters; bootstrapped from UCI history)
CREATE TABLE IF NOT EXISTS class_ladder (
  class_key TEXT PRIMARY KEY,
  level TEXT NOT NULL DEFAULT 'L0',                     -- L0/L1/L2/STANDING
  consecutive_verified INTEGER NOT NULL DEFAULT 0,
  promoted_by TEXT, promoted_at TEXT
);
