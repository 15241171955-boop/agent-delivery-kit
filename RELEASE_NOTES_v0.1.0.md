# v0.1.0 — first release

**Spec-Gated Delivery** — a stack-agnostic, zero-dependency way to ship work with AI agents through
four script-judged gates, so "done" is a fact a script checks, not a claim the model makes.

## Highlights

- **Four-stage gated loop** — specify → review → apply → verify, each ending in a deterministic gate
  (`validate_contract`, `coverage_gate`, `gate_check`, `dod_check`).
- **Zero dependencies** — Python 3 standard library only; the whole kit is a handful of ~30-line
  scripts you can read in one sitting.
- **A machine-readable contract** carries the work from spec to implementation. Gates re-derive their
  own invariants, so a hand-edited `status` can't skip a gate.
- **Orchestrator + dashboard** — `run_pipeline.py` runs all four gates, prints a status board,
  retries on demand, and writes a self-contained HTML dashboard + JSON result.
- **Portable skills** — plain `SKILL.md` + `scripts/`, the same shape Codex and Claude/Anthropic
  skills already use. Drop them in or point your agent at them.
- **Learn by doing** — end-to-end worked examples (a feature across all four states, and a bug fix),
  plus a cookbook on writing good contracts and extending the gates.
- **Robust** — malformed JSON, missing files, non-object contracts, and unwritable output paths all
  fail with a clean message, never a traceback.

## Quickstart

```bash
git clone https://github.com/15241171955-boop/agent-delivery-kit
cd agent-delivery-kit
export ADK="$PWD/kit"
python3 -m unittest discover -s "$ADK/scripts/tests" -p "test_*.py"    # 41 tests, zero deps
python3 "$ADK/scripts/run_pipeline.py" examples/contract.sample.json   # ALL GREEN (4/4)
```

To use it in your own project, see **Install into your project** in the README and
[`docs/cookbook.md`](docs/cookbook.md).

## Under the hood

- **41 stdlib tests**, run in CI (GitHub Actions) on every push and PR — gates accept a good
  contract, reject a bad one, and the orchestrator is exercised too.
- `kit/` — 4 skills, shared contract schema / rule sources / definition-of-done, 4 gates +
  orchestrator, a context-map, and optional extensions (dual-track governance, pipeline-driver).
- `docs/` — methodology article, concepts, architecture, cookbook, and an adapting guide.
- `examples/` — a runnable feature walkthrough (draft → reviewed → applied → verified) and a bug fix.

## How it differs

Deliberately a **micro-kit**, not a framework. Versus larger spec-driven tools (e.g. GitHub's Spec
Kit), the bet is **smaller + more auditable + deterministic gates**: the thing that decides "done" is
a ~30-line script you can read in a minute and run in CI, not a prompt.

## Notes

This is `v0.1.0`. The core is stable and tested, but the contract schema and CLI flags may evolve
before `1.0`. Issues and feedback welcome.

## License

MIT.
