---
name: apply
description: >-
  Stage ③ of Spec-Gated Delivery. Implement a reviewed contract by consuming it, passing the
  pre-implementation gate before editing any code. Use when building the change after review.
  Triggers: apply the change, implement the contract, build it, start coding the spec.
---

# ③ apply — implement through the gate

## Goal
Turn a **reviewed** contract into working implementation — consuming the contract as the source of
truth, not re-deriving requirements, and not touching code until the gate is green.

## Inputs
- The `contract.json` at `status: "reviewed"`.
- Team rules: [`../../shared/rule-sources.md`](../../shared/rule-sources.md).

## The gate you must pass — BEFORE editing code
```bash
# $ADK = the kit directory (kit/ in this repo, or your install path, e.g. .delivery/)
python3 "$ADK/scripts/gate_check.py" <contract.json>
```
Exit 0 means: the contract is `reviewed` (② passed) and every acceptance criterion is testable.
**If it exits non-zero, you may not edit implementation code.** This is the kit's hard guardrail
against "the fix is obvious, I'll just code it" drift.

## Steps
1. Run `gate_check.py`. If red, stop and go back — do not edit code.
2. Implement strictly against the contract's `entities` and `acceptance`. Follow `rule-sources.md`.
3. Keep the contract authoritative: if reality forces a change to requirements, **return to ①/②**
   and update the contract — don't silently diverge.
4. When implementation is complete, set `status: "applied"`, fill `tasks_open` and the `tests`
   block honestly, and hand to ④.

## Composition (invariant #4)
This skill *orchestrates* implementation; it does not reinvent your build/test tooling. Call your
existing formatters, test runners, and CI — reference them, don't reimplement them here.

## Self-check (do not skip)
- [ ] `gate_check.py` exited 0 **before** any code edit.
- [ ] Every acceptance criterion has corresponding implementation.
- [ ] No requirement was changed without updating the contract.
- [ ] `tasks_open` and `tests` reflect reality, not optimism.

→ Next: [`verify`](../verify/SKILL.md). Back: [`review`](../review/SKILL.md).
