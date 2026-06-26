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

## Forbidden placeholders

To prevent fake completeness, `validate_contract.py` rejects a contract that contains any of these
placeholder markers as a substring of any string value:

`TODO`   `TBD`   `FIXME`   `<...>`   `???`

Intent length is counted in a script-aware way (each CJK character counts as one unit), so an
`intent` written in a non-space-delimited script is not mistaken for "too short".

## Status lifecycle

```
draft ──(② review passes)──▶ reviewed ──(③ apply done)──▶ applied ──(④ verify passes)──▶ verified
```

Each gate script only lets a contract move forward when its checks are green:
`validate_contract` (any) · `coverage_gate` (draft→reviewed) ·
`gate_check` (reviewed→may edit code) · `dod_check` (applied→verified).
