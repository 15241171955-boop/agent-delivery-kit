#!/usr/bin/env python3
"""④ gate: machine-judged Definition of Done. Exit 0 => verified.

Re-derives upstream invariants (structure + coverage) and requires the pipeline to have
actually progressed (status >= applied) — a `status: draft` contract with green evidence
cannot pass. Then: all acceptance passed, zero open tasks, tests really passed (not skipped).
See kit/shared/definition-of-done.md.
"""
import sys

import _contract as c
import validate_contract
import coverage_gate


def check(contract):
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

    return (len(reasons) == 0, reasons)


def main(argv):
    if len(argv) != 2:
        print("usage: dod_check.py <contract.json>")
        return 2
    contract, err = c.read_contract(argv[1])
    if err:
        print("[FAIL] dod_check\n  - %s" % err)
        return 2
    return c.report("dod_check", *check(contract))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
