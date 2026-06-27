# Spec-Gated Delivery: a reusable workflow for shipping with AI agents

*A reusable, stack-agnostic method for shipping work with AI agents through script-gated stages.*

## 1. The problem: agentic delivery drifts

Hand a capable model a task and let it code, and a predictable failure pattern appears. It skips
the boring steps. It changes the requirements quietly when reality gets inconvenient. It rounds
"almost working" up to "done," and you discover the gap two steps later — in review, in QA, or in
production. None of this is malice; it's optimism plus the absence of a forcing function. The model
has no skin in the game on whether a test *actually* ran.

You cannot fix this with a better prompt alone, because the prompt is exactly the surface the model
is free to reinterpret. You fix it by moving the decisions that matter out of prose and into
**gates that a script decides**.

## 2. The idea: a contract-driven, gated loop

Spec-Gated Delivery turns any "intent → shipped" task into four stages, each ending in a gate:

```
intent ─▶ ① SPECIFY ─▶ ② REVIEW ─▶ ③ APPLY ─▶ ④ VERIFY ─▶ ship
              │            │            │            │
         contract.json  coverage    gate-check    dod-check
                          gate                       │
                          └──────── red ◀────────────┘
```

The connective tissue is a **machine-readable contract** produced in stage ① and consumed in stage
③. Everything the downstream needs is in that file; nothing important is left to be re-derived from
chat history. Design and implementation are decoupled the way a mould is decoupled from the casting.

## 3. The four stages

**① Specify.** Convert intent into a structured spec and a `contract.json` (schema:
[`kit/shared/contract-schema.md`](../kit/shared/contract-schema.md)). The contract lists the
`sources` that must be covered, the `entities` being changed, and `acceptance` criteria that are
each *testable* and each mapped back to the sources they satisfy. **Gate:** `validate_contract.py`
— structurally complete, and containing none of the placeholder tokens (`TODO`, `TBD`, `FIXME`, …) that
are how "fake completeness" sneaks in.

**② Review.** Before any code, check that the contract faithfully covers its sources and is
implementable. The cheap place to find a missing requirement is here. **Gate:** `coverage_gate.py`
— every `must_cover` source is referenced by at least one acceptance criterion. Nominal coverage
that is hollow gets downgraded by the human/agent reviewer; an uncovered must-cover source is a hard
block back to ①.

**③ Apply.** Implement against the contract — consuming it, not re-deriving it. **Gate (before
editing any code):** `gate_check.py` — the contract must be `reviewed` and every criterion testable.
If the gate is red, you may not touch implementation code. This is the guardrail against the single
most seductive drift: *"the fix is obvious, I'll just code it."*

**④ Verify.** Decide completion by script, not by narration. **Gate:** `dod_check.py` — every
acceptance criterion `passed`, zero open tasks, and the test suite actually passed and was not
skipped. While the gate is red, no success wording is allowed.

## 4. The five invariants

These are what make the loop hold rather than merely look tidy:

1. **Single source of truth.** Rules live once, under `kit/shared/`. Skills reference them; they
   never restate them. Two copies of a rule become two *different* rules within a month.
2. **Machine-readable contract handoff.** `contract.json` is the one artifact that crosses the
   ①→③ boundary, so the boundary is inspectable and testable.
3. **Deterministic gates.** The model cannot self-certify. A `check()` function exits non-zero or
   it doesn't. This is the load-bearing wall.
4. **Composition over duplication.** Orchestrators *call* skills and tools; they never reimplement
   them. The system grows by wiring, not by copying.
5. **Derived artifacts excluded.** Indexes, caches, runtime state are `.gitignore`d — they're
   reproducible outputs, not source.

## 5. Why the gates must be machine-judged

This is the whole insight, so it's worth stating plainly. An instruction like "make sure all tests
pass before saying you're done" is advice the model can rationalize around ("the failing test looks
unrelated"). A script that reads the contract and exits 1 unless `tests.passed && !tests.skipped`
is a fact you can hang CI on. The difference between advice and a gate is the difference between
hoping and knowing.

Concretely: the kit's `dod_check.py` is ~30 lines and refuses to pass a contract whose suite was
skipped. That one refusal eliminates the most common way agentic work is silently incomplete.

## 6. The optimism problem, and anti-omission

Models default to completeness *theatre*: a section labelled "(omitted for brevity)," an acceptance
criterion marked done because it was *probably* done. Two mechanisms in the kit counter this. First,
**forbidden placeholder tokens** — `validate_contract.py` fails any contract containing `TODO`,
`TBD`, `FIXME`, `<...>`, and friends, so you cannot ship a hollow spec. Second, **machine-judged DoD** —
completion is computed from evidence fields, not asserted. Neither relies on the model's goodwill.

## 7. Governance: the dual-track pattern (optional)

A mature agent system eventually edits *itself* — new skills, changed gates, revised rules. If those
changes flow through the same pipeline as product changes, the two pollute each other. The optional
[dual-track extension](../kit/extensions/dual-track-governance.md) keeps them separate: one track for
"change the product," one for "change the kit." Start without it; add it when you have more than a
couple of people touching the skills.

## 8. Adapting to your stack

The four skills and four gates contain no language or framework specifics by design. To adopt:
copy `kit/` into your repo; fill [`kit/shared/rule-sources.md`](../kit/shared/rule-sources.md) with
your team's real rules; extend the contract schema with your domain fields; wire the four scripts
into CI (validate + coverage in the planning job, `gate_check` before the build job, `dod_check`
before merge). The full checklist is in
[`adapting-to-your-stack.md`](./adapting-to-your-stack.md).

## 9. Limitations and when not to use it

This is overhead. For a one-line throwaway script or a spike you'll delete tomorrow, the ceremony
costs more than it saves — skip it. The kit earns its keep when work is shared across people or
sessions, when "done" has consequences, and when you're delegating real implementation to an agent.

The gate is only as honest as the evidence it reads. By default `dod_check` trusts that
`tests.passed` reflects a real run — fine locally, but the model wrote that field. **Measured mode**
removes the trust: `record_evidence.py` (run by CI) executes the suite, writes the evidence from the
real exit code, and stamps `evidence.source: "runner"`; `dod_check --require-measured` then refuses
anything the runner didn't attest. That converts the headline claim — "the model cannot self-certify"
— from a convention into something a required CI check enforces. The residual limit is the universal
one: a runner pointed at a vacuous suite will faithfully certify vacuity. The script can guarantee a
real run happened; it cannot guarantee the tests were *worth* running — that judgement, like semantic
coverage (`coverage_gate --strict`), stays with a human reviewer by design.

---

*Reference implementation: [`../kit/`](../kit/). Run `python3 kit/scripts/tests/test_gates.py` to
see the gates accept a good contract and reject the many ways one can be malformed.*
