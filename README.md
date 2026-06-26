# agent-delivery-kit

[![gates](https://github.com/15241171955-boop/agent-delivery-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/15241171955-boop/agent-delivery-kit/actions/workflows/ci.yml) ![license](https://img.shields.io/badge/license-MIT-blue) ![python](https://img.shields.io/badge/python-3.x-blue) ![deps](https://img.shields.io/badge/deps-zero-brightgreen) ![skills](https://img.shields.io/badge/SKILL.md-compatible-blue)

> **Spec-Gated Delivery** — a stack-agnostic, reusable workflow for shipping work with AI agents through four gated stages, where every gate is judged by a deterministic script, not by the model's own say-so.

---

## What it is

Naive "let the agent code" workflows drift: the model skips steps, marks things done that aren't, and you find out late. `agent-delivery-kit` fixes that by turning delivery into a **contract-driven, gated loop**:

```
intent ─▶ ① SPECIFY ─▶ ② REVIEW ─▶ ③ APPLY ─▶ ④ VERIFY ─▶ ship
              │            │            │            │
         contract.json  coverage    gate-check    dod-check
          (machine-      gate       (no code      (evidence
           readable)                 before gate)  before claims)
                          └──────── red ◀──────────┘
```

## The four stages

| Stage | Input | Output | Gate (script-judged) |
|-------|-------|--------|----------------------|
| **① Specify** | intent, sources | structured spec + machine-readable `contract.json` | `validate_contract.py` — schema valid, no placeholders |
| **② Review** | spec + contract + sources | structured review + coverage signal | `coverage_gate.py` — does the contract faithfully cover the sources? |
| **③ Apply** | contract + rule sources | implementation | `gate_check.py` — pre-implementation gates all done before editing code |
| **④ Verify** | implementation + evidence | Definition-of-Done verdict | `dod_check.py` — acceptance green + zero open tasks + tests really passed |

## The five invariants

1. **Single source of truth** — rules live once under `kit/shared/`, referenced not copied.
2. **Machine-readable contract handoff** — stage ① emits the contract that stage ③ consumes; design and implementation stay decoupled.
3. **Deterministic gates** — the model cannot self-certify; the scripts decide.
4. **Composition over duplication** — orchestrators only call skills, never reimplement them.
5. **Derived artifacts excluded** — indexes, caches, runtime state are `.gitignore`d.

## Repo layout

```
agent-delivery-kit/
├── docs/         # methodology article, concepts, architecture, adapting guide
├── kit/          # the runnable scaffold
│   ├── skills/   # specify · review · apply · verify (portable SKILL.md)
│   ├── shared/   # contract schema, rule sources, definition of done
│   ├── commands/ # thin entrypoints
│   ├── scripts/  # the 4 gate scripts + stdlib tests (Python 3, zero deps)
│   ├── extensions/  # optional: dual-track governance, simplified orchestrator
│   └── context-map.yaml
└── examples/     # a minimal sample contract (shape only, stack-free)
```

## Quickstart

```bash
# from this repo — point $ADK at the kit, then run the gate self-tests (no deps)
export ADK="$PWD/kit"
python3 "$ADK/scripts/tests/test_gates.py"

# watch the gates reject a bad contract, then accept a good one
python3 "$ADK/scripts/validate_contract.py" examples/contract.bad.json     # FAIL (with reasons)
python3 "$ADK/scripts/dod_check.py"          examples/contract.sample.json  # PASS

# read the method
open docs/article.en.md
```

## Install into your project

Keep the kit as **one folder** so its internal paths (`scripts/`, `shared/`) stay valid — don't
scatter individual skill files.

```bash
cd your-project
cp -r /path/to/agent-delivery-kit/kit .delivery     # 1. drop the kit in as one unit
export ADK="$PWD/.delivery"                          # 2. kit root; gates are "$ADK/scripts/<gate>.py"

# 3. let your agent discover the skills WITHOUT copying them out (keeps ../../shared valid):
#    Preferred — point your agent's skills path straight at .delivery/skills
#    Fallback (if your agent can't add a skills path) — symlink it in:
#      ln -s ../../.delivery/skills .codex/skills/adk     # Claude Code: .claude/skills/adk

# 4. CI: copy the workflow and adjust paths
cp /path/to/agent-delivery-kit/.github/workflows/ci.yml .github/workflows/
```

The skills are plain `SKILL.md` + `scripts/` — the same shape Codex and Claude/Anthropic skills use.
Each skill calls its gate as `"$ADK/scripts/…"` and reads rules via `../../shared/…`, so **pointing
your agent at the skills folder (or symlinking it) — not flattening it — keeps both valid.** Then fill
`.delivery/shared/rule-sources.md` with your team's rules.

## How this differs

Deliberately a **micro-kit**: four stages, four ~30-line gate scripts, zero dependencies — not a
framework. Versus larger spec-driven tools (e.g. GitHub's Spec Kit), the bet is **smaller + more
auditable + deterministic gates**: the thing that decides "done" is a script you can read in a minute
and run in CI, not a prompt. Use it on its own, or as the gate layer beside a heavier spec tool.

## Adapting to your stack

The 4 skills and 4 gates contain **no language/framework specifics**. To adopt: copy `kit/` into your repo, fill `kit/shared/rule-sources.md` with your team's rules, extend `kit/shared/contract-schema.md` with your domain fields, and wire the gate scripts into your CI. See [`docs/adapting-to-your-stack.md`](docs/adapting-to-your-stack.md).

## License

MIT — see [LICENSE](LICENSE).
