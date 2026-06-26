# Gate scripts + orchestrator

**Python 3 standard library only — zero dependencies.** Four deterministic gates, each exposing a
pure `check(contract) -> (ok, reasons)` and a CLI that exits 0 (pass) / 1 (fail), plus an optional
orchestrator that runs all four and renders a dashboard.

| Script | Stage | Decides |
|--------|-------|---------|
| `validate_contract.py` | ① specify | contract is structurally complete, correctly typed, no placeholder tokens |
| `coverage_gate.py` | ② review | every `must_cover` source is covered by an acceptance criterion |
| `gate_check.py` | ③ apply | contract is reviewed + testable → **may edit code** |
| `dod_check.py` | ④ verify | acceptance green + zero open tasks + tests really passed → **done** |
| `run_pipeline.py` | all | runs the four gates in order, prints a status board, retries, writes JSON + HTML dashboard |

`_contract.py` holds shared constants and the JSON loader (the single source of the schema rules).

## Run

```bash
# self-tests (gate + pipeline suites)
python3 -m unittest discover -s kit/scripts/tests -p "test_*.py"

# individual gates — good contract PASSes, bad contract FAILs (exit 1) with reasons:
python3 kit/scripts/validate_contract.py examples/contract.sample.json
python3 kit/scripts/dod_check.py        examples/contract.bad.json
```

## Orchestrate + visualize

```bash
# run all four gates, print a status board (exit 0 iff all green)
python3 kit/scripts/run_pipeline.py examples/contract.sample.json

# auto-retry while you (or an agent) fix the contract, and emit a dashboard + machine-readable result
python3 kit/scripts/run_pipeline.py path/to/contract.json \
  --max-attempts 5 --retry-delay 10 \
  --report report.html --json run.json
```

- `report.html` is a **self-contained** gate dashboard (no external assets) — open it in any browser.
- `--max-attempts N` re-loads the contract each attempt, so an agent or human fixing it between
  attempts is picked up; the run stops early as soon as all gates are green.

> Defense in depth: `gate_check` and `dod_check` re-derive the upstream invariants (structure +
> coverage) instead of trusting the contract's `status` field, so a hand-edited `status` cannot
> bypass a gate.

## Wire into CI

```bash
python3 kit/scripts/run_pipeline.py "$CONTRACT"   # one command, exits non-zero if any gate is red
```
