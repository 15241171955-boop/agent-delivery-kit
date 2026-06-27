---
name: verify
description: >-
  Stage ④ of Spec-Gated Delivery. Verify an applied contract against a machine-judged Definition
  of Done before claiming completion. Use before saying anything is done, fixed, or ready to ship.
  Triggers: verify, is it done, definition of done, check before shipping, final verification.
---

# ④ verify — machine-judged Definition of Done

## Goal
Decide — by script, not by narration — whether the change is actually done. Evidence before
assertions, always.

## Inputs
- The `contract.json` at `status: "applied"`, with `acceptance[].passed`, `tasks_open`, and
  `tests` filled in from real execution.
- The DoD: [`../../shared/definition-of-done.md`](../../shared/definition-of-done.md).

## The gate that decides
```bash
# $ADK = the kit directory (kit/ in this repo, or your install path, e.g. .delivery/)
python3 "$ADK/scripts/dod_check.py" <contract.json>
```
Exit 0 ⟺ all acceptance `passed`, `tasks_open == 0`, and `tests.passed && !tests.skipped`.
On exit 0, set `status: "verified"`. On non-zero, the only terminal states are `needs-review`
or `blocked`.

### Measured mode (do not let the agent write its own evidence)
The check above reads evidence fields the contract author wrote. The honest path is to have a
**runner** produce them and refuse anything it didn't attest — this is what CI should run:
```bash
python3 "$ADK/scripts/record_evidence.py" <contract.json> --test-command "<your suite>" --verify
python3 "$ADK/scripts/dod_check.py"        <contract.json> --require-measured
```
`record_evidence.py` runs the suite, writes `tests`/`acceptance[].passed` from the real exit code,
and stamps `evidence.source: "runner"`; `--require-measured` then rejects self-attested or
tampered evidence. As the implementing agent, **you do not hand-write `tests.passed` or set
`evidence` — the runner does.**

## Hard rule
While `dod_check.py` is red, **do not** emit "done / fixed / shipped / closed the loop". A skipped
or absent test suite counts as **not verified**. This rule exists because optimistic completion
claims are the #1 failure mode of agentic delivery.

## Steps
1. Populate the contract from *real* evidence: which acceptance criteria passed, open task count,
   whether the suite ran and passed (never paper over skips).
2. Run `dod_check.py`.
3. Green → `status: "verified"`, report done with the evidence. Red → report `needs-review` /
   `blocked` with exactly what failed; never round up.

## Self-check (do not skip)
- [ ] Every `passed: true` is backed by real evidence, not assumption.
- [ ] `tests.skipped` is honest.
- [ ] `dod_check.py` exited 0 before any success wording.

Back: [`apply`](../apply/SKILL.md).
