# Worked example — a bug fix, same four gates

A one-line-ish fix still earns a contract. It's small, but it goes through the exact same loop —
this is the deliberate "no 'it's just a small fix' bypass" stance.

[`contract.json`](contract.json) is the finished (verified) state. Run from the repo root:

```bash
export ADK="$PWD/kit"
python3 "$ADK/scripts/run_pipeline.py" examples/bugfix-negative-quantity/contract.json
```
```
  (1)  specify  validate_contract  PASS
  (2)  review   coverage_gate      PASS
  (3)  apply    gate_check         PASS
  (4)  verify   dod_check          PASS
Result: ALL GREEN (4/4)
```

What keeps a bug fix honest here:

- **One `must_cover` source** (`bug-1042`) — and `coverage_gate` proves an acceptance criterion
  actually addresses it, so you can't "fix" a bug the ticket didn't ask for and call it done.
- **A regression criterion** (`ac-2`) — the contract forces you to assert the positive path still
  works, not just the bug path.
- **`dod_check`** still demands `tests.passed && !tests.skipped` — a fix "that looks right" but
  whose test was skipped is **not** verified.

A compact contract like this is the right size for most bug fixes: one source, one or two entities,
two acceptance criteria (the fix + the regression guard).
