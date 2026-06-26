# agent-delivery-kit

[![gates](https://github.com/15241171955-boop/agent-delivery-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/15241171955-boop/agent-delivery-kit/actions/workflows/ci.yml) ![license](https://img.shields.io/badge/license-MIT-blue) ![python](https://img.shields.io/badge/python-3.x-blue) ![deps](https://img.shields.io/badge/deps-zero-brightgreen) ![skills](https://img.shields.io/badge/SKILL.md-compatible-blue)

> **Spec-Gated Delivery** — a stack-agnostic, reusable workflow for shipping work with AI agents through four gated stages, where every gate is judged by a deterministic script, not by the model's own say-so.
>
> 一套**技术栈无关**、可复用的 AI agent 交付流程:任何"意图 → 上线"都强制走**出契约 → 评审 → 落地 → 验证**四道闸,每道闸由确定性脚本机判,而非模型自述。

**English** · [中文](#中文)

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

The kit is distilled from a 69-skill production agent system, stripped of any language/framework specifics, down to its portable core: **4 skills + shared rule sources + a routing map + 4 deterministic gate scripts (Python 3 stdlib, zero deps).**

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
├── docs/         # methodology article (EN + ZH), concepts, architecture, adapting guide
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
open docs/article.en.md   # or docs/article.zh.md
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

---

<a name="中文"></a>

## 中文

### 这是什么

放任式"让 agent 直接写代码"会漂移:模型跳步、把没做完的标成完成,你很晚才发现。`agent-delivery-kit` 把交付变成**契约驱动 + 闸门治理的闭环**:

```
意图 ─▶ ① 出契约 ─▶ ② 评审 ─▶ ③ 落地 ─▶ ④ 验证 ─▶ 上线
            │           │          │          │
       contract.json  覆盖闸    gate-check   dod-check
        (机器可读)              (过门才       (证据先于
                                能改码)        结论)
                       └─────── 红灯 ◀─────────┘
```

本 kit 从一套 69-skill 的生产级 agent 系统中提炼,去掉一切语言/框架细节,只留可移植内核:**4 个 skill + 共享规则源 + 路由表 + 4 个确定性闸门脚本(Python 3 标准库,零依赖)。**

### 四个阶段

| 阶段 | 输入 | 输出 | 闸门(脚本机判) |
|------|------|------|----------------|
| **① 出契约** | 意图、源资料 | 结构化 spec + 机器可读 `contract.json` | `validate_contract.py` — schema 合法、无占位 |
| **② 评审** | spec + 契约 + 源 | 结构化评审 + 覆盖信号 | `coverage_gate.py` — 契约是否忠实覆盖源需求 |
| **③ 落地** | 契约 + 规则源 | 实现产物 | `gate_check.py` — 改码前前置门全 done |
| **④ 验证** | 实现 + 证据 | DoD 判定 | `dod_check.py` — 验收全绿 + 任务零未关闭 + 测试真过 |

### 五条不变量

1. **单一事实源** — 规则只写在 `kit/shared/` 一处,引用不复制。
2. **机器可读契约串联** — ① 产出契约、③ 消费契约,设计与实现解耦。
3. **确定性闸门** — 模型不能自证,脚本说了算。
4. **只编排不复制** — 上层只调用 skill,不重造执行环节。
5. **派生物不入库** — 索引/缓存/运行态一律 `.gitignore`。

### 快速开始

```bash
# 本仓库内——把 $ADK 指向 kit,再跑闸门自测(零依赖)
export ADK="$PWD/kit"
python3 "$ADK/scripts/tests/test_gates.py"

# 看四道闸如何拒绝坏契约、放行好契约
python3 "$ADK/scripts/validate_contract.py" examples/contract.bad.json     # FAIL(带原因)
python3 "$ADK/scripts/dod_check.py"          examples/contract.sample.json  # PASS

open docs/article.zh.md                                        # 读方法论
```

### 装进你的项目

把 kit 当作**一个整体目录**安装,内部路径(`scripts/`、`shared/`)才不会失效——不要拆散单个文件。

```bash
cd 你的项目
cp -r /path/to/agent-delivery-kit/kit .delivery     # 1. 整体放入
export ADK="$PWD/.delivery"                          # 2. kit 根;闸门即 "$ADK/scripts/<gate>.py"

# 3. 让 agent 发现 skill,但别把文件拷出来(保持 ../../shared 有效):
#    首选——直接把 agent 的 skills 路径指向 .delivery/skills
#    备用(agent 不支持额外 skills 路径时)——符号链接:
#      ln -s ../../.delivery/skills .codex/skills/adk     # Claude Code 用 .claude/skills/adk

# 4. CI:拷工作流并按需改路径
cp /path/to/agent-delivery-kit/.github/workflows/ci.yml .github/workflows/
```

skill 就是普通的 `SKILL.md` + `scripts/`,与 Codex、Claude/Anthropic skills 同一种结构。每个 skill
用 `"$ADK/scripts/…"` 调闸门、用 `../../shared/…` 读规则,所以**把 agent 指向 skills 目录(或符号链接)、而非拆平,才能两者都有效。**
再把团队规则填进 `.delivery/shared/rule-sources.md` 即可。

### 差异点

刻意做成**微 kit**:四阶段、四个约 30 行的闸门脚本、零依赖——不是框架。相比更大的 spec 驱动工具
(如 GitHub 的 Spec Kit),押的是**更小、更可审计、确定性闸门**:判定"完成"的是一段一分钟读完、
能进 CI 的脚本,而不是一句提示词。可单独用,也可作为重型 spec 工具旁边的闸门层。

### 适配你自己的技术栈

4 个 skill 与 4 个闸门**不含任何语言/框架专有内容**。落地方式:把 `kit/` 拷进你的仓库,在 `kit/shared/rule-sources.md` 填你团队的规则,在 `kit/shared/contract-schema.md` 扩你的领域字段,把闸门脚本接进 CI。详见 [`docs/adapting-to-your-stack.md`](docs/adapting-to-your-stack.md)。

### 许可

MIT,见 [LICENSE](LICENSE)。
