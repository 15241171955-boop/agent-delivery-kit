---
name: pipeline-driver
description: >-
  Optional orchestrator for Spec-Gated Delivery. Drives one change end-to-end through ①→④ by
  CALLING the specify/review/apply/verify skills in order and enforcing the red lines between them.
  Use when you want a single resumable entry that runs the whole loop. Triggers: drive the pipeline,
  run the full loop end to end, orchestrate delivery, ship this change start to finish.
---

# pipeline-driver — orchestrate ①→④ (optional)

## Principle (read first)
This skill **only calls** the four stage skills; it **never reimplements** their work or bypasses
their gates (invariant #4). It adds sequencing, red-line enforcement, and resumability — nothing else.
If you find yourself writing implementation logic here, stop: it belongs in `③ apply`.

## What it does
Runs one contract through the loop, refusing to advance a stage until that stage's gate is green:

```
P0 intake ─▶ ① specify ─▶ [validate_contract] ─▶ ② review ─▶ [coverage_gate]
       ─▶ ③ apply ─▶ [gate_check BEFORE any code] ─▶ implement ─▶ ④ verify ─▶ [dod_check]
       ─▶ terminal: verified | needs-review | blocked
```

## Red lines (non-negotiable)
1. **Gate before advance.** Never move to the next stage while the current gate is red.
2. **No code before `gate_check`.** In ③, `gate_check.py` must exit 0 before editing implementation
   code. No "small/obvious fix" exception.
3. **No success wording while `dod_check` is red.** Terminal state is then `needs-review` or
   `blocked`, never "done".
4. **Skipped tests = not verified.** Never treat an absent/skipped suite as a pass.
5. **Contract is authoritative.** If reality forces a requirement change, return to ①/② and update
   the contract; do not diverge silently.

## Resumability
Persist the current stage + contract status to a runtime file (e.g. `.agent-state/<id>.json`, which
is `.gitignore`d). On re-entry with the same contract id, resume from the recorded stage. The
contract's own `status` field is the durable source of progress; the runtime file is just a cursor.

## Stage delegation (call, don't copy)
| Step | Calls |
|------|-------|
| ① | [`../../skills/specify/SKILL.md`](../../skills/specify/SKILL.md) → `validate_contract.py` |
| ② | [`../../skills/review/SKILL.md`](../../skills/review/SKILL.md) → `coverage_gate.py` |
| ③ | [`../../skills/apply/SKILL.md`](../../skills/apply/SKILL.md) → `gate_check.py` (pre-code) |
| ④ | [`../../skills/verify/SKILL.md`](../../skills/verify/SKILL.md) → `dod_check.py` |

## Definition of Done (for the driver itself)
The driver may report success **only** when `dod_check.py` exits 0 for the contract. Any other
outcome is reported as `needs-review` or `blocked`, with the exact failing reasons surfaced.

> Kept deliberately tiny: this orchestrator does exactly one job — sequence the four stages
> honestly behind their gates — and adds no logic of its own.
