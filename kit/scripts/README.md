# Gate scripts

Four deterministic gates, **Python 3 standard library only — zero dependencies**. Each script
exposes a pure `check(contract) -> (ok, reasons)` and a CLI that exits 0 (pass) or 1 (fail).

| Script | Stage | Decides |
|--------|-------|---------|
| `validate_contract.py` | ① specify | contract is structurally complete, no placeholder tokens |
| `coverage_gate.py` | ② review | every `must_cover` source is covered by an acceptance criterion |
| `gate_check.py` | ③ apply | contract is reviewed + testable → **may edit code** |
| `dod_check.py` | ④ verify | acceptance green + zero open tasks + tests really passed → **done** |

`_contract.py` holds shared constants and the JSON loader (the single source of the schema rules).

## Run

```bash
python3 kit/scripts/tests/test_gates.py                       # self-tests (23 cases)

# good contract — every gate PASSes:
python3 kit/scripts/validate_contract.py examples/contract.sample.json
python3 kit/scripts/coverage_gate.py    examples/contract.sample.json
python3 kit/scripts/gate_check.py       examples/contract.sample.json
python3 kit/scripts/dod_check.py        examples/contract.sample.json

# bad contract — every gate FAILs (exit 1) with reasons:
python3 kit/scripts/validate_contract.py examples/contract.bad.json
python3 kit/scripts/dod_check.py        examples/contract.bad.json
```

> Defense in depth: `gate_check` and `dod_check` re-derive the upstream invariants (structure +
> coverage) instead of trusting the contract's `status` field, so a hand-edited `status` cannot
> bypass a gate.

## Wire into CI

```bash
python3 kit/scripts/validate_contract.py "$CONTRACT" || exit 1
python3 kit/scripts/coverage_gate.py    "$CONTRACT" || exit 1
# ... gate_check before the implementation job, dod_check before merge.
```
