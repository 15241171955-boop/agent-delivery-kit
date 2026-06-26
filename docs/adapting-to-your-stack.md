# Adapting to your stack / 适配你的技术栈

The kit ships stack-agnostic. Here is the practical path to make it yours. /
本 kit 默认栈无关,以下是把它变成"你的"的实操路径。

## 1. Copy the kit / 拷贝 kit
```bash
cp -r agent-delivery-kit/kit your-repo/.delivery
```
Keep `skills/`, `shared/`, `scripts/`, `commands/`, `context-map.yaml`. /
保留这五样。

## 2. Fill your rules / 填你的规则
Edit [`shared/rule-sources.md`](../kit/shared/rule-sources.md) with your real coding standards,
architecture boundaries, and test policy. This is the **only** place project rules belong. /
把真实规范填进 `rule-sources.md`,这是项目规则**唯一**该待的地方。

## 3. Extend the contract schema / 扩展契约 schema
Add domain fields your work needs (e.g. `api_endpoints`, `db_migrations`, `ui_pages`) to
[`shared/contract-schema.md`](../kit/shared/contract-schema.md), then add matching checks to
`scripts/validate_contract.py` with a test in `scripts/tests/`. Keep the core fields. /
在 schema 加领域字段,并在 `validate_contract.py` 补对应校验 + 测试;核心字段保留。

## 4. Wire the gates into CI / 把闸门接进 CI
| When / 时机 | Run / 跑 |
|-------------|----------|
| planning job / 规划任务 | `validate_contract.py` + `coverage_gate.py` |
| before build / 构建前 | `gate_check.py` |
| before merge / 合并前 | `dod_check.py` |

Example (GitHub Actions step) / 示例:
```yaml
- name: spec gates
  run: |
    python3 .delivery/scripts/validate_contract.py "$CONTRACT"
    python3 .delivery/scripts/coverage_gate.py    "$CONTRACT"
```

## 5. Have CI write the evidence / 让 CI 写证据
The integrity of `dod_check` depends on `tests.passed` / `tests.skipped` being written by your
**test runner**, not the model. Emit them from CI. /
`dod_check` 的可信度取决于 `tests.*` 由**测试运行器**写,而不是模型写。让 CI 输出它们。

## 6. (Optional) language swap / (可选)换语言
Gates are Python 3 stdlib. To port to Node/Go, reimplement the four pure `check()` functions and
their tests — the contract schema and the rules stay identical. /
闸门是 Python 3 标准库。要移到 Node/Go,只需重写四个纯 `check()` 函数和测试,契约 schema 与规则不变。

## 7. (Optional) add governance / (可选)加治理
When more than a couple of people edit the kit itself, adopt
[`extensions/dual-track-governance.md`](../kit/extensions/dual-track-governance.md). /
当不止一两人改 kit 本身时,引入双轨治理。
