---
name: specify
description: >-
  Stage ① of Spec-Gated Delivery. Turn an intent (feature, fix, change) into a structured
  spec plus a machine-readable contract.json that downstream stages consume. Use when starting
  any new piece of work, writing a PRD/spec, or capturing requirements before implementation.
  Triggers: specify, write a spec, draft a contract, start a change, new feature, capture requirements.
---

# ① specify — produce the contract

## Goal
Convert intent into two things: a human-readable spec, and a **machine-readable `contract.json`**
conforming to [`../../shared/contract-schema.md`](../../shared/contract-schema.md). The contract is
the only artifact stage ③ is allowed to consume — get it right here.

## Inputs
- The user's intent / request.
- Any source material (PRD, tickets, meeting notes, old-system docs). List each in `sources`,
  marking the ones that **must** be covered with `must_cover: true`.
- Team rules: [`../../shared/rule-sources.md`](../../shared/rule-sources.md).

## Output
A `contract.json` with: `id`, `intent`, `sources`, `entities`, `acceptance` (each `testable`,
each mapping back to the sources it satisfies via `covers`), `confidence`, `status: "draft"`.

## The gate you must pass
```bash
# $ADK = the kit directory (kit/ in this repo, or your install path, e.g. .delivery/)
python3 "$ADK/scripts/validate_contract.py" <contract.json>
```
Exit 0 means the contract is structurally complete and contains **no placeholder tokens**
(`TODO`, `TBD`, `FIXME`, …). Do not advance until it passes.

## Steps
1. Write `intent` as one tight paragraph (problem + goal). No solutioning yet.
2. Enumerate `sources`; mark `must_cover` on the non-negotiable ones.
3. List `entities` (the things created/changed) with their key fields.
4. Write `acceptance` criteria — each **testable**, each with `covers: [source-id,…]`.
   Every `must_cover` source must appear in at least one criterion's `covers`.
5. Set `confidence`: `explicit` (clear), `suggest` (inferred — ask the user to confirm),
   or `fallback` (default skeleton).
6. Run the validate gate.

## Self-check (do not skip)
- [ ] Every `must_cover` source is referenced by ≥1 acceptance `covers`.
- [ ] No acceptance criterion is vague or untestable.
- [ ] No placeholder tokens anywhere.
- [ ] `validate_contract.py` exits 0.
- [ ] If `confidence: suggest`, the user has confirmed before moving on.

→ Next: [`review`](../review/SKILL.md).
