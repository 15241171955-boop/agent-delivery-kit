# Concepts — quick reference / 速查

## The loop / 闭环

```
intent ─▶ ① specify ─▶ ② review ─▶ ③ apply ─▶ ④ verify ─▶ ship
意图       出契约        评审        落地        验证        上线
```

## Stages & gates / 阶段与闸门

| # | Stage / 阶段 | Output / 产出 | Gate / 闸门 | Advances status to |
|---|--------------|---------------|-------------|--------------------|
| ① | specify 出契约 | `contract.json` | `validate_contract.py` | `draft` |
| ② | review 评审 | coverage verdict | `coverage_gate.py` | `reviewed` |
| ③ | apply 落地 | implementation | `gate_check.py` (before code) | `applied` |
| ④ | verify 验证 | DoD verdict | `dod_check.py` | `verified` |

## Five invariants / 五条不变量

1. Single source of truth — rules live once in `kit/shared/`. / 单一事实源。
2. Machine-readable contract handoff (①→③). / 机器可读契约串联。
3. Deterministic gates — the model can't self-certify. / 确定性闸门,模型不自证。
4. Composition over duplication. / 只编排不复制。
5. Derived artifacts excluded (`.gitignore`). / 派生物不入库。

## Red lines / 红线

- No code edit in ③ before `gate_check.py` exits 0. / ③ 改码前 gate_check 必须绿。
- No success wording in ④ while `dod_check.py` is red. / ④ 红灯时禁用"完成"措辞。
- A skipped/absent test suite is **not verified**, never **passed**. / 跳过/缺失测试 = 未验证。
