# Definition of Done (DoD)

> Consumed by `④ verify` / `dod_check.py`. A contract reaches `status: verified` **only when
> all of the following are machine-true** — the model may not declare done by narration.

A change is **done** if and only if:

1. **Acceptance all green** — every `acceptance[].passed == true`.
2. **Zero open tasks** — `tasks_open == 0` (or every remaining item explicitly converted to a
   tracked follow-up, not silently dropped).
3. **Tests really passed** — `tests.passed == true` **and** `tests.skipped == false`.
   A skipped/absent suite = not verified.

If any condition is false, the only allowed terminal states are `needs-review` or `blocked`.
**No success wording** ("done", "shipped", "closed the loop") may be emitted while red.

## Why machine-judged

The model is optimistic; it will round "almost" up to "done". By making DoD a script that reads
the contract and exits non-zero on any unmet condition, completion becomes a fact you can gate CI
on — not a vibe. This is the single most important rule in the kit.
