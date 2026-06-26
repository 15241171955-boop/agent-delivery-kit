# Cookbook

Practical guidance for using and extending the kit. Pair this with the runnable walkthroughs:
[feature](../examples/feature-csv-export/README.md) and
[bug fix](../examples/bugfix-negative-quantity/README.md).

---

## 1. Writing a good contract

A contract is small but every field earns its place.

- **`id`** — kebab-case, action-first: `add-csv-export`, `fix-negative-quantity-checkout`.
- **`intent`** — one paragraph: the *problem* and the *goal*. No solution design, no field dumps.
- **`sources`** — every reference the work must honour (PRD section, ticket, meeting note). Mark the
  non-negotiable ones `must_cover: true`; background reading is `must_cover: false`.
- **`entities`** — the things you create or change, with their key fields. This is what ③ implements
  against; keep it concrete.
- **`acceptance`** — the heart of the contract. Each criterion must be:
  - **testable** (`testable: true`) — phrased so a test could pass or fail on it,
  - **traceable** (`covers: [...]`) — listing the `source` ids it satisfies. `coverage_gate` checks
    that every `must_cover` source is named by at least one criterion, so this is how you prove the
    contract addresses the ask.
  - Add a **regression criterion** for fixes (assert the untouched path still works).
- **`confidence`** — `explicit` when the ask is clear; `suggest` when you inferred it (get the human
  to confirm before ③); `fallback` for a default skeleton.

Anti-patterns the gates will (and should) reject: vague criteria, a `must_cover` source no criterion
covers, placeholder tokens (`TODO`, `TBD`, …), or a thin one-line `intent`.

## 2. The lifecycle in practice

`draft → reviewed → applied → verified`. Who moves it, and when:

| Transition | Who / when | Gate that guards it |
|------------|-----------|---------------------|
| → `draft` | author writes the contract | `validate_contract` (structure, no placeholders) |
| `draft → reviewed` | reviewer confirms coverage & feasibility | `coverage_gate` |
| `reviewed → applied` | implementer builds it; `gate_check` must be green **before** editing code | `gate_check` |
| `applied → verified` | evidence is filled from a real run | `dod_check` |

Keep `status` honest: the gates re-derive structure and coverage on every run, so editing `status`
by hand to skip ahead does not work — `gate_check`/`dod_check` will still fail.

## 3. Extending the schema and a gate

The core stays generic; add your domain fields in *your* fork. Worked example — require a
`db_migrations` list on contracts that touch the database, and gate it.

**a. Document the field** in `kit/shared/contract-schema.md` (single source of truth).

**b. Add the check** to `kit/scripts/validate_contract.py`, inside `check()`:

```python
# db_migrations (optional): when present, must be a list of {id, reversible}
migrations = contract.get("db_migrations")
if migrations is not None:
    if not isinstance(migrations, list):
        reasons.append("db_migrations must be a list")
    else:
        for i, m in enumerate(migrations):
            if not (isinstance(m, dict) and "id" in m and isinstance(m.get("reversible"), bool)):
                reasons.append("db_migrations[%d] needs id and boolean reversible" % i)
```

**c. Add tests** in `kit/scripts/tests/test_gates.py` — one that accepts a valid value and one that
rejects a malformed one:

```python
def test_validate_accepts_db_migrations(self):
    d = copy.deepcopy(self.c); d["db_migrations"] = [{"id": "V1__init", "reversible": True}]
    self.assertTrue(validate_contract.check(d)[0])

def test_validate_rejects_irreversible_flag_type(self):
    d = copy.deepcopy(self.c); d["db_migrations"] = [{"id": "V1__init", "reversible": "yes"}]
    self.assertFalse(validate_contract.check(d)[0])
```

**d. Run** `python3 -m unittest discover -s kit/scripts/tests -p "test_*.py"`.

Rules of thumb: anything the model could fudge belongs in a **script**, not just a `SKILL.md`
sentence; every new rule ships with a passing **and** a failing test; keep `check()` a pure
function so it stays trivially testable and CI-friendly.

## 4. Orchestration and the dashboard

`run_pipeline.py` runs all four gates over a contract and shows where it stands:

```bash
python3 kit/scripts/run_pipeline.py path/to/contract.json
```

For an agent-in-the-loop or a human fixing as they go, retry until green (it re-loads the contract
each attempt, so fixes are picked up) and emit a shareable dashboard:

```bash
python3 kit/scripts/run_pipeline.py path/to/contract.json \
  --max-attempts 5 --retry-delay 10 --report report.html --json run.json
```

`report.html` is self-contained (no external assets): a flow strip of the four stages plus a table
of each gate's result and reasons. `run.json` is the same data, machine-readable.

## 5. Wiring into CI

One command gates a change end-to-end (exit non-zero if any gate is red):

```yaml
- name: spec gates
  run: python3 .delivery/scripts/run_pipeline.py "$CONTRACT"
```

Crucially, have your **test runner** (not the model) write `tests.passed` / `tests.skipped` into the
contract before `dod_check` runs — that is what keeps "done" honest.

## 6. More

- End-to-end feature walkthrough: [`examples/feature-csv-export/`](../examples/feature-csv-export/README.md)
- Bug-fix walkthrough: [`examples/bugfix-negative-quantity/`](../examples/bugfix-negative-quantity/README.md)
- Porting to your stack: [`adapting-to-your-stack.md`](adapting-to-your-stack.md)
- Optional governance / orchestration extensions: [`../kit/extensions/`](../kit/extensions/README.md)
