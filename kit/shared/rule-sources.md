# Rule sources (fill this in for your team)

> **Invariant #1 — single source of truth.** Project rules live here, in one place.
> The four skills *reference* this file; they never restate rules inline. When you adopt the
> kit, replace the placeholders below with your real rules and delete this notice.

## 1. Coding standards
<!-- e.g. naming, layering, error handling, logging, i18n. Link to your style guide. -->
- _your rule_

## 2. Architecture boundaries
<!-- e.g. which layers may call which; what must never import what. -->
- _your rule_

## 3. Definition of "covered" (for ② review)
<!-- How a source requirement counts as covered by the contract. Default: at least one
     `acceptance` criterion lists the source id in its `covers`. Tighten if needed. -->
- A `must_cover: true` source is covered iff ≥1 acceptance criterion lists its `id` in `covers`.

## 4. Definition of Done (for ④ verify)
<!-- Authoritative DoD lives in definition-of-done.md; summarize or link here. -->
- See [`definition-of-done.md`](./definition-of-done.md).

## 5. Test policy
<!-- What "tests really passed" means; what may never be skipped. -->
- A skipped or absent test suite counts as **not verified**, never as passed.

## 6. Forbidden in delivered work
<!-- Things that fail review automatically. -->
- Placeholder tokens in the contract (see `contract-schema.md`).
- Claiming completion without gate evidence.
