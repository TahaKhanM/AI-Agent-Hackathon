# Policy action-class schema (authoring kit)

*WP-POLICY. Governs `precedent/policy_pack.yaml` and any split-out pack such as
`precedent/policy_pack_actions.yaml`. Enforced by `precedent policy lint`
(`precedent/policy_lint.py`). Authoring is **CLI-only** — the running console executes the
deterministic gate, it never authors it.*

## Why this exists

The deterministic gate (rule 2) decides **what executes** from a per-tenant YAML tree keyed
by the incident fingerprint `class_key = "service|error_code|target_object_type"`. An action
class is only safe to execute if two things are true *before* it runs:

1. it has a **TRUE inverse** — a rollback that is generated *before* the mutation, so a failed
   verify can restore the prior state (§2.5 *rollback-precedes-execution*); and
2. it has a **verification probe** — a deterministic post-state check that says whether the
   fix actually worked (and therefore whether to keep it or roll back).

The lint **rejects** any executable class that is missing either. Password resets and
credential rotations are rejected *permanently* — but **not by an action-name denylist**
(synonyms slip past those). They are rejected *positively*: an executable class must name an
inverse tool that **actually exists in the typed-tool registry and performs a genuine
rollback**, and a state-destroying action cannot — its inverse is necessarily absent, a no-op,
or an invented tool name. So an irreversible action, *by any name*, routes to a human, never to
an executable plan.

## Class entry shape

A class entry keeps its existing required fields and adds three **optional** authoring
fields. Existing fields are unchanged and `policy.assess()` / `rule_for()` still ignore the
new ones — only the lint reads them.

```yaml
"<service>|<error_code>|<target_object_type>":   # the class_key (deterministic fingerprint)
  # --- existing (required) ---
  risk_class: standard_change        # standard_change | restricted_change | escalate | unclassified
  policy_rule_id: PUB-EPG-4223-REPUBLISH   # stable id, audited
  ladder_ceiling: L2                 # L0 | L1 | L2 | STANDING | ESCALATE (max autonomy policy allows)
  action_type: republish_epg         # a typed tool, or `none` for non-executable classes
  lineage_refs: ["kb:KB-0001"]       # acl_source refs a memorised fix must carry

  # --- authoring-kit (optional; required by lint for EXECUTABLE classes) ---
  required_approver_role: publishing-ops   # who may approve (MANDATORY for restricted_change)

  precedent_ref:                     # provenance to the recurring corpus class (colour/lineage)
    corpus: UCI-498                   # anonymised UCI-498 fix class — lineage only
    fix_class: "Category 42|Subcategory 223|code 6"
    # NB: no per-class occurrence count — the corpus is anonymised and individual counts are
    # NOT in docs/numbers.md, so asserting one would present an unverified number as fact.

  inverse:                           # INVERSE GENERATOR — how the mutation is undone
    strategy: restore_snapshot       # restore_snapshot | typed_inverse   (a TRUE inverse)
    reversible: true                 # MUST be true; a class with no real rollback is not executable
    tool: restore                    # the typed call that performs the inverse — MUST resolve to
                                     # a real rollback tool in the typed-tool registry (below)

  verification_probe:                # VERIFICATION PROBE — how "did it work?" is decided
    strategy: object_health          # object_health | field_equals
    expect_healthy: true             # object_health: object must read healthy post-fix
    # field_equals also needs:  field: <name>   expected: <value>
```

### `action_type`

`none` (or empty) marks a **non-executable** class — escalate, stale-runbook, or degrade
routes that never mutate state. These are exempt from the inverse/probe contract. Any other
value is an **executable** class and must satisfy the contract below.

### `inverse` — the inverse generator

| strategy | meaning | true inverse? | `tool` must resolve to |
|---|---|---|---|
| `restore_snapshot` | capture the object's full pre-state before executing; roll back via the `restore` typed call | yes | a real rollback tool — `restore` (sim.core.restore / POST `/sim/restore`) |
| `typed_inverse` | a dedicated typed tool that reverses the action (names the `tool`) | yes | a real forward typed tool the sim's executor recognises |
| `none` / anything else | no genuine rollback | **no — rejected** | — |

`reversible` must be `true`. A class that declares `reversible: false` or a non-true strategy
is rejected — the fix is telling you it cannot be safely undone, so it must not auto-execute.

**The named `tool` must actually exist.** The lint resolves it against the typed-tool registry
(`_ROLLBACK_TOOLS` / `_FORWARD_TYPED_TOOLS` in `precedent/policy_lint.py`, grounded in
`sim.core`): a `tool` that is absent — a no-op or an invented name — is **not** a true inverse
and the class is rejected. This is the positive requirement that keeps irreversible actions
(by any name) out without a brittle name denylist.

### `verification_probe` — the verification probe

| strategy | check |
|---|---|
| `object_health` | the target object reads healthy after the fix (sim `/verify`) |
| `field_equals` | a named `field` equals an `expected` value after the fix |

## Lint rules

`precedent policy lint` reports **every** violation (it does not stop at the first) so a pack
is fixed in one pass. Codes:

| code | when |
|---|---|
| `MISSING_INVERSE` | executable class has no `inverse` block |
| `NO_TRUE_INVERSE` | inverse not `reversible: true`, strategy not a real rollback mechanism, missing its `tool`, or the named `tool` does **not resolve** to a real rollback in the typed-tool registry (fake / no-op / invented name) |
| `MISSING_PROBE` | executable class has no `verification_probe` block |
| `INVALID_PROBE` | probe strategy unknown, or `field_equals` missing `field`/`expected` |
| `MISSING_APPROVER_ROLE` | a `restricted_change` class does not name `required_approver_role` |
| `LOAD_ERROR` / `MALFORMED_CLASS` | the pack (or a class entry) is not valid YAML / a mapping |

### Irreversible actions — rejected positively, not by name

There is **no action-name denylist** (credential-rotation / password-reset *synonyms* would
slip past one). Irreversibility falls out of `NO_TRUE_INVERSE`: an executable class is accepted
only if its declared inverse names a tool that **exists in the typed-tool registry and performs
a genuine rollback**. A state-destroying action — a credential rotation, password reset, wipe,
by *any* name — cannot name such a tool (you cannot un-rotate a live credential or restore a
destroyed hash), so its inverse is necessarily absent, a no-op, or an invented name, and it is
rejected. The registry of real rollback tools is `_ROLLBACK_TOOLS` / `_FORWARD_TYPED_TOOLS` in
`precedent/policy_lint.py`, grounded in `sim.core` and exercised end-to-end by the sim
round-trip test in `tests/test_policy_kit.py`.

## Usage

```bash
precedent policy lint                       # lint the shipped packs (default)
precedent policy lint path/to/pack.yaml ...  # lint specific packs
# exit 0 = clean, 1 = at least one violation (messages on stderr)
```

## The shipped action-class pack

`precedent/policy_pack_actions.yaml` holds sim-executable action classes seeded from the
**head of the 558 recurring UCI fix classes** (`data/analysis/uci-baseline-results.md`: 558
classes recur ≥4 times and cover 94.8% of incident volume — both figures are in
`docs/numbers.md`). Each carries a `precedent_ref` to its anonymised UCI fix class (lineage
only — **no** per-class occurrence count, which is not measured/published), and maps onto one
of the sim's typed tools (`republish_epg`, `dedupe_slot`, `rights_takedown`) with a
`restore_snapshot` inverse and an `object_health` probe — so every class's inverse and probe
are exercisable end-to-end against the sim (see `tests/test_policy_kit.py`).
