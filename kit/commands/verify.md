# /verify

Entry point for stage ④ of Spec-Gated Delivery.

**Routes to:** [`../skills/verify/SKILL.md`](../skills/verify/SKILL.md)
**Gate:** `python3 $ADK/scripts/dod_check.py <contract.json>` &nbsp;(`$ADK` = the kit directory)

Use before claiming anything is done. Advances `status: applied → verified` only when the
Definition of Done is machine-true. No success wording while the gate is red.
