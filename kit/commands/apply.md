# /apply

Entry point for stage ③ of Spec-Gated Delivery.

**Routes to:** [`../skills/apply/SKILL.md`](../skills/apply/SKILL.md)
**Gate (before editing code):** `python3 $ADK/scripts/gate_check.py <contract.json>` &nbsp;(`$ADK` = the kit directory)

Use to implement a reviewed contract. Advances `status: reviewed → applied`.
**Hard rule:** no implementation-code edit until the gate exits 0.
