#!/usr/bin/env python3
"""③ gate: pre-implementation guardrail. Exit 0 => you may edit implementation code.

Re-derives the upstream invariants (structure + coverage) instead of trusting the
model-written `status` field — a faked `status: reviewed` cannot bypass this gate.
Additionally requires status >= reviewed and every acceptance criterion to be testable.
"""
import sys

import _contract as c
import validate_contract
import coverage_gate


def check(contract):
    if not isinstance(contract, dict):
        return (False, ["contract must be a JSON object"])

    # Re-derive upstream invariants (don't trust `status` alone).
    valid, reasons = validate_contract.check(contract)
    if not valid:
        return (False, reasons)
    reasons += coverage_gate.check(contract)[1]

    # Stage gate.
    if not c.at_least(contract, "reviewed"):
        reasons.append("status must be 'reviewed' or later before editing code (got %r)"
                       % contract.get("status"))

    acceptance = contract.get("acceptance", []) or []
    if not acceptance:
        reasons.append("no acceptance criteria to implement against")
    for a in acceptance:
        if a.get("testable") is not True:
            reasons.append("acceptance %s is not testable" % a.get("id"))

    return (len(reasons) == 0, reasons)


def main(argv):
    if len(argv) != 2:
        print("usage: gate_check.py <contract.json>")
        return 2
    contract, err = c.read_contract(argv[1])
    if err:
        print("[FAIL] gate_check\n  - %s" % err)
        return 2
    return c.report("gate_check", *check(contract))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
