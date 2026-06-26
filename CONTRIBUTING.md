# Contributing

Thanks for your interest. This kit is intentionally small — keep it that way.

## Principles (don't break these)

1. **Stack-agnostic.** No language/framework specifics in `kit/skills/`, `kit/shared/`, or `kit/scripts/`. Domain detail belongs in *your* fork, not here.
2. **Gates stay deterministic.** Every script in `kit/scripts/` must be pure, dependency-free (Python 3 stdlib only), and decide via exit code. Add a test in `kit/scripts/tests/` for any new rule.
3. **Single source of truth.** A rule lives in exactly one file under `kit/shared/`. If two skills need it, both *reference* it.
4. **Skills describe, scripts decide.** A `SKILL.md` may instruct, but anything that can be gamed by the model must be enforced by a script.

## Before opening a PR

```bash
python3 kit/scripts/tests/test_gates.py   # must pass
```

## Adding a stage rule

1. Add the check to the relevant `kit/scripts/*.py` as a pure function.
2. Add a passing + a failing test case in `kit/scripts/tests/`.
3. Document the rule in the matching `kit/skills/*/SKILL.md` self-check list.

## Style

- Docs are bilingual where it matters (EN + ZH). Keep both in sync.
- Prefer prose + one diagram over walls of bullet points.
