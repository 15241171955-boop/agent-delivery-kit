# Concepts — quick reference

## The loop

```
intent ─▶ ① specify ─▶ ② review ─▶ ③ apply ─▶ ④ verify ─▶ ship
```

## Stages & gates

| # | Stage | Output | Gate | Advances status to |
|---|-------|--------|------|--------------------|
| ① | specify | `contract.json` | `validate_contract.py` | `draft` |
| ② | review | coverage verdict | `coverage_gate.py` | `reviewed` |
| ③ | apply | implementation | `gate_check.py` (before code) | `applied` |
| ④ | verify | DoD verdict | `dod_check.py` | `verified` |

## Five invariants

1. Single source of truth — rules live once in `kit/shared/`.
2. Machine-readable contract handoff (① → ③).
3. Deterministic gates — the model can't self-certify.
4. Composition over duplication.
5. Derived artifacts excluded (`.gitignore`).

## Red lines

- No code edit in ③ before `gate_check.py` exits 0.
- No success wording in ④ while `dod_check.py` is red.
- A skipped/absent test suite is **not verified**, never **passed**.
