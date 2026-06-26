---
name: review
description: >-
  Stage ② of Spec-Gated Delivery. Review a draft contract for source coverage and
  implementability before any code is written. Use after a contract is drafted and before apply.
  Triggers: review the spec, check coverage, is this contract ready, pre-implementation review.
---

# ② review — coverage & readiness gate

## Goal
Decide whether the draft contract faithfully covers its sources and is implementable — **before**
a single line of code. Catch missing requirements here, where they're cheap.

## Inputs
- The draft `contract.json` from ①.
- The original `sources` (the actual PRD / tickets / notes).
- Team rules: [`../../shared/rule-sources.md`](../../shared/rule-sources.md).

## Output
A structured review with a verdict per source — **Pass / Warn / Block** — and, on success,
the contract advanced to `status: "reviewed"`.

## The gate you must pass
```bash
# $ADK = the kit directory (kit/ in this repo, or your install path, e.g. .delivery/)
python3 "$ADK/scripts/coverage_gate.py" <contract.json>
```
Exit 0 means every `must_cover` source is covered by ≥1 acceptance criterion. A `Block` (uncovered
must-cover source) is non-negotiable: send it back to ①, don't wave it through.

## Steps
1. For each `source`, find the acceptance criteria that claim to cover it (`covers`).
2. Read the *actual* source and judge whether the criteria truly satisfy it — not just name-match.
   Downgrade to **Warn**/**Block** when coverage is nominal but hollow.
3. Check implementability against `rule-sources.md` (architecture boundaries, feasibility).
4. Run the coverage gate. If green and your manual read agrees, set `status: "reviewed"`.

## Self-check (do not skip)
- [ ] Every `must_cover` source is genuinely (not just nominally) covered.
- [ ] Each acceptance criterion is testable and feasible.
- [ ] `coverage_gate.py` exits 0.
- [ ] Any Warn/Block is recorded and routed back, not silently accepted.

→ Next: [`apply`](../apply/SKILL.md). Back: [`specify`](../specify/SKILL.md).
