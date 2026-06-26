# Worked example — a feature, end to end

This walks one feature ("add CSV export to a list view") through all four stages. One snapshot of
the contract is included **per stage**, so each command below runs against the state that stage
actually produces:

| Stage | Snapshot | Status |
|-------|----------|--------|
| ① specify | [`contract.draft.json`](contract.draft.json) | `draft` |
| ② review | (advance to) [`contract.reviewed.json`](contract.reviewed.json) | `reviewed` |
| ③ apply | (implement →) [`contract.applied.json`](contract.applied.json) | `applied` |
| ④ verify | [`contract.verified.json`](contract.verified.json) | `verified` |

Run everything from the repo root with `export ADK="$PWD/kit"`.

---

## ① Specify — write the contract

Capture intent as a structured contract: the `sources` that must be covered, the `entities` you'll
change, and `acceptance` criteria that are each *testable* and mapped back to a source via `covers`.
Status starts at `draft`.

```bash
python3 "$ADK/scripts/validate_contract.py" examples/feature-csv-export/contract.draft.json
# [PASS] validate_contract
```

Run the whole pipeline on the draft — the later gates are correctly **blocked**, nothing is built yet:

```bash
python3 "$ADK/scripts/run_pipeline.py" examples/feature-csv-export/contract.draft.json
```
```
  (1)  specify  validate_contract  PASS
  (2)  review   coverage_gate      PASS
  (3)  apply    gate_check         FAIL
         - status must be 'reviewed' or later before editing code (got 'draft')
  (4)  verify   dod_check          FAIL  ...
Result: BLOCKED (2/4)
```

## ② Review — check coverage, then advance

The reviewer confirms every `must_cover` source is genuinely covered, then advances the contract to
`status: reviewed` (that's `contract.reviewed.json`).

```bash
python3 "$ADK/scripts/coverage_gate.py" examples/feature-csv-export/contract.reviewed.json
# [PASS] coverage_gate
```

## ③ Apply — the pre-code gate opens

With `status: reviewed`, the pre-code gate passes, so implementation may begin:

```bash
python3 "$ADK/scripts/gate_check.py" examples/feature-csv-export/contract.reviewed.json
# [PASS] gate_check   →  you may now edit implementation code
```

Build the feature against the contract. As each criterion is met set its `passed: true`, close out
`tasks_open`, and let your **test runner** write the real `tests` result. That yields
`contract.applied.json` (`status: applied`).

## ④ Verify — let the script decide "done"

Run the pipeline on the applied contract. `dod_check` now passes, which is what authorizes the final
flip to `status: verified`:

```bash
python3 "$ADK/scripts/run_pipeline.py" examples/feature-csv-export/contract.applied.json
```
```
  (1)  specify  validate_contract  PASS
  (2)  review   coverage_gate      PASS
  (3)  apply    gate_check         PASS
  (4)  verify   dod_check          PASS
Result: ALL GREEN (4/4)
```

`contract.verified.json` is the same contract with `status: verified` — the done state, all green.
Want a shareable view? add `--report report.html`.

---

**Takeaway:** the contract is the single artifact that carries the work forward, and "done" is a
script result, not a claim. See [`../../docs/cookbook.md`](../../docs/cookbook.md) for best practices.
