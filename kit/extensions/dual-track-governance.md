# Extension: dual-track governance

## The problem it solves

A live agent system eventually changes *itself*: someone adds a skill, tightens a gate, rewrites a
rule. If those changes ride the same delivery pipeline as product work, two bad things happen: the
product backlog fills with meta-changes, and a regression in the kit can land disguised as a feature.

## The pattern

Run **two tracks** with the same four-stage discipline but separate workspaces:

| Track | Changes what | Contract id prefix | Reviewers |
|-------|--------------|--------------------|-----------|
| **product** | your application / features / fixes | `feat-`, `fix-`, … | product owners |
| **kit** | `kit/skills/**`, `kit/scripts/**`, `kit/shared/**`, this repo's rules | `kit-` | whoever owns the agent process |

Each track keeps its own contract log. A change never edits both a product entity and a kit rule in
one contract — if it needs both, split it into a `feat-` contract and a `kit-` contract that
reference each other.

## Why separate, concretely

- **No cross-pollution.** Product reviewers don't have to reason about gate-script internals, and
  kit reviewers don't have to reason about business rules.
- **Clean blast radius.** A `kit-` change that breaks a gate is visible as a kit regression, caught
  by `kit/scripts/tests/`, not buried in a feature diff.
- **Honest history.** "Why did delivery behave differently last week?" is answerable from the `kit-`
  log alone.

## Minimal adoption

1. Add a `track` field to your contract (`product` | `kit`).
2. Route `kit-` contracts to the kit reviewers and require `kit/scripts/tests/test_gates.py` green
   in their `dod_check` evidence.
3. Keep everything else identical — same four stages, same gates.

> This is the de-scoped version of the "two OpenSpec workspaces" idea from the system this kit was
> distilled from: one workspace for business change, one for agent-capability change.
