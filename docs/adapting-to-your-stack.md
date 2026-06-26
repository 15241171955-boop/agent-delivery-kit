# Adapting to your stack

The kit ships stack-agnostic. Here is the practical path to make it yours.

## 1. Copy the kit
```bash
cp -r agent-delivery-kit/kit your-repo/.delivery
```
Keep `skills/`, `shared/`, `scripts/`, `commands/`, and `context-map.yaml` together as one tree.

## 2. Fill your rules
Edit [`shared/rule-sources.md`](../kit/shared/rule-sources.md) with your real coding standards,
architecture boundaries, and test policy. This is the **only** place project rules belong.

## 3. Extend the contract schema
Add the domain fields your work needs (e.g. `api_endpoints`, `db_migrations`, `ui_pages`) to
[`shared/contract-schema.md`](../kit/shared/contract-schema.md), then add matching checks to
`scripts/validate_contract.py` with a test in `scripts/tests/`. Keep the core fields.

## 4. Wire the gates into CI
| When | Run |
|------|-----|
| planning job | `validate_contract.py` + `coverage_gate.py` |
| before build | `gate_check.py` |
| before merge | `dod_check.py` |

```yaml
- name: spec gates
  run: |
    python3 .delivery/scripts/validate_contract.py "$CONTRACT"
    python3 .delivery/scripts/coverage_gate.py    "$CONTRACT"
```

## 5. Have CI write the evidence
The integrity of `dod_check` depends on `tests.passed` / `tests.skipped` being written by your
**test runner**, not the model. Emit them from CI.

## 6. (Optional) language swap
The gates are Python 3 stdlib. To port to Node/Go, reimplement the four pure `check()` functions and
their tests — the contract schema and the rules stay identical.

## 7. (Optional) add governance
When more than a couple of people edit the kit itself, adopt
[`extensions/dual-track-governance.md`](../kit/extensions/dual-track-governance.md).
