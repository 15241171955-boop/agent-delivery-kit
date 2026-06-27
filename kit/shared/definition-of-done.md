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

## Declared vs. measured (run this in CI)

By default the three conditions are read as **declared** fields — honest enough for local work, but
the model is the one writing them. To remove that trust, run in **measured mode**:

1. `record_evidence.py <contract>` executes `verification.test_command` (CI pins it via
   `--test-command` / `$ADK_TEST_COMMAND`), writes `tests` and `acceptance[].passed` from the real
   exit code, and stamps `evidence.source: "runner"`.
2. `dod_check.py <contract> --require-measured` then passes **only** if that runner provenance is
   present and `tests.passed` still agrees with the recorded return code.

So the model may write the contract, but it may not *self-attest* completion. Make the
`--require-measured` step a required status check and "done" stops being something the model can
assert.

## Why machine-judged

The model is optimistic; it will round "almost" up to "done". By making DoD a script that reads
the contract and exits non-zero on any unmet condition, completion becomes a fact you can gate CI
on — not a vibe. This is the single most important rule in the kit.
