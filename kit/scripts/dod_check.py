#!/usr/bin/env python3
"""④ gate: machine-judged Definition of Done. Exit 0 => verified.

Re-derives upstream invariants (structure + coverage) and requires the pipeline to have
actually progressed (status >= applied) — a `status: draft` contract with green evidence
cannot pass. Then: all acceptance passed, zero open tasks, tests really passed (not skipped).
See kit/shared/definition-of-done.md.

`--require-measured` (recommended in CI) additionally refuses any contract whose evidence
was not produced by the runner: it demands `evidence.source == "runner"` with a timestamp,
and cross-checks that `tests.passed` still agrees with the recorded `test_returncode` (so a
field hand-edited after recording is caught). Generate that evidence with record_evidence.py.
"""
import sys

import _contract as c
import validate_contract
import coverage_gate


def check(contract, require_measured=False):
    if not isinstance(contract, dict):
        return (False, ["contract must be a JSON object"])

    # Re-derive upstream invariants and require real pipeline progress.
    valid, reasons = validate_contract.check(contract)
    if not valid:
        return (False, reasons)
    reasons += coverage_gate.check(contract)[1]
    if not c.at_least(contract, "applied"):
        reasons.append("status must be 'applied' or later before verification (got %r)"
                       % contract.get("status"))

    acceptance = contract.get("acceptance", []) or []
    if not acceptance:
        reasons.append("no acceptance criteria")
    for a in acceptance:
        if a.get("passed") is not True:
            reasons.append("acceptance %s not passed" % a.get("id"))

    if contract.get("tasks_open", 1) != 0:
        reasons.append("tasks_open must be 0 (got %r)" % contract.get("tasks_open"))

    tests = contract.get("tests") or {}
    if tests.get("passed") is not True:
        reasons.append("tests.passed must be true")
    if tests.get("skipped") is not False:
        reasons.append("tests.skipped must be false (a skipped/absent suite is not verified)")

    if require_measured:
        reasons += _measured_reasons(contract, tests)

    return (len(reasons) == 0, reasons)


def _measured_reasons(contract, tests):
    """Provenance gate: evidence must come from the runner and be internally consistent.

    The two-key half of the kit: the model may write the contract, but it may not
    *self-attest* completion — only record_evidence.py (run by CI) stamps source: runner.
    """
    out = []
    ev = contract.get("evidence")
    if not isinstance(ev, dict) or ev.get("source") != "runner":
        out.append("require-measured: evidence.source must be 'runner' — run record_evidence.py "
                   "in CI; the model may not self-attest completion")
        return out
    if not (isinstance(ev.get("recorded_at"), str) and ev["recorded_at"].strip()):
        out.append("require-measured: evidence.recorded_at is missing")
    rc = ev.get("test_returncode")
    if isinstance(rc, int) and (rc == 0) != (tests.get("passed") is True):
        out.append("require-measured: tests.passed disagrees with evidence.test_returncode "
                   "(evidence was edited after the run)")
    return out


def main(argv):
    flags = argv[1:]
    require_measured = "--require-measured" in flags
    args = [a for a in flags if a != "--require-measured"]
    if len(args) != 1:
        print("usage: dod_check.py [--require-measured] <contract.json>")
        return 2
    contract, err = c.read_contract(args[0])
    if err:
        print("[FAIL] dod_check\n  - %s" % err)
        return 2
    return c.report("dod_check", *check(contract, require_measured=require_measured))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
