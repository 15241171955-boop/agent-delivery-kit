# Contract schema (single source of truth)

The **contract** is the machine-readable handoff produced by `① specify` and consumed by
`③ apply`. It is a JSON file (zero-dependency parsing with Python's stdlib `json`).
The gate scripts in `kit/scripts/` encode these rules as constants and enforce them.

> Why JSON, not YAML? To keep the gate scripts **dependency-free** (Python 3 stdlib has no
> YAML parser). If your team prefers YAML, add a YAML lib in your fork and point the loader at it —
> the schema below is format-independent.

## Top-level fields

| Field | Type | Required | Meaning |
|-------|------|----------|---------|
| `id` | string (kebab-case) | ✅ | Unique change id, e.g. `add-export-button`. |
| `intent` | string (≥10 words / CJK chars) | ✅ | One paragraph: the problem and the goal. Length is counted script-aware (each CJK character = one unit), so non-space-delimited scripts aren't rejected. |
| `sources` | list&lt;source&gt; | ✅ | Reference material the contract must faithfully cover. |
| `entities` | list&lt;entity&gt; | ✅ | The things being created or changed. |
| `acceptance` | list&lt;criterion&gt; | ✅ | Testable acceptance criteria. |
| `confidence` | enum | ✅ | `explicit` \| `suggest` \| `fallback` — how sure the spec is. |
| `status` | enum | ✅ | `draft` → `reviewed` → `applied` → `verified`. |
| `tasks_open` | int | for ④ | Count of execution items not yet closed. |
| `tests` | object | for ④ | `{ "passed": bool, "skipped": bool }`. |
| `verification` | object | for measured ④ | How to *measure* done: `{ "test_command": "pytest -q", "acceptance_commands": { "ac-1": "…" } }`. Run by `record_evidence.py`, not the model. |
| `evidence` | object | stamped by runner | Provenance of the evidence: `{ "source": "runner", "recorded_at": "…", "test_command": "…", "test_returncode": 0 }`. Required under `dod_check --require-measured`. |
| `review` | object | for `coverage --strict` | Reviewer two-key: `{ "coverage_substantive": true, "by": "alice" }`. The implementing model may not set this for itself. |

### `source`
```
{ "id": "prd-3.2", "ref": "docs/prd.md#3.2", "must_cover": true }
```

### `entity`
```
{ "name": "Order", "kind": "model", "fields": ["id", "status", "total"] }
```

### `criterion`
```
{ "id": "ac-1", "statement": "User can export the list as CSV",
  "testable": true, "covers": ["prd-3.2"], "passed": false }
```
- `covers` lists the `source.id`s this criterion satisfies — this is how `coverage_gate.py`
  decides whether every `must_cover` source is addressed.
- `passed` is set true only when verified with evidence (used by `dod_check.py`).

## Declared vs. measured evidence

By default the ④ gate reads the evidence fields (`tests`, `acceptance[].passed`) as **declared** —
whoever wrote the contract set them. That is enough for local iteration but trusts the author. In
**measured mode**, `record_evidence.py` (run by CI, not the model) executes `verification.test_command`,
overwrites the evidence fields from the real exit code, and stamps an `evidence` block with
`source: "runner"`. `dod_check.py --require-measured` then refuses any contract that lacks runner
provenance or whose `tests.passed` no longer matches the recorded `test_returncode`. Command
precedence is `--test-command` > `$ADK_TEST_COMMAND` > `verification.test_command`, so CI controls
what executes. See [`../../examples/measured/`](../../examples/measured/).

`coverage_gate.py --strict` applies the same separation to review: each `must_cover` source needs a
substantive, testable criterion, and `review.coverage_substantive` must be set true by a reviewer —
never by the implementing model.

## Forbidden placeholders

To prevent fake completeness, `validate_contract.py` rejects a contract that contains any of these
placeholder markers in any string value (symbols matched literally; words matched
case-insensitively on word boundaries):

`TODO`   `TO-DO`   `TBD`   `FIXME`   `WIP`   `XXX`   `PLACEHOLDER`   `lorem ipsum`   `<...>`   `???`

This is a smoke detector for honest "completeness theatre", not an adversarial defence — judging
whether present content is *real* is the reviewer's / `coverage --strict` job.

Intent length is counted in a script-aware way (each CJK character counts as one unit), so an
`intent` written in a non-space-delimited script is not mistaken for "too short".

## Status lifecycle

```
draft ──(② review passes)──▶ reviewed ──(③ apply done)──▶ applied ──(④ verify passes)──▶ verified
```

Each gate script only lets a contract move forward when its checks are green:
`validate_contract` (any) · `coverage_gate` (draft→reviewed) ·
`gate_check` (reviewed→may edit code) · `dod_check` (applied→verified).
