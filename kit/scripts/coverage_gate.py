#!/usr/bin/env python3
"""② gate: every must_cover source is covered by >=1 acceptance criterion.

check(contract) -> (ok, reasons). Exit 0 means coverage is complete.

Defensive about types (so a malformed contract can't slip through by accident):
- a `covers` value is only honoured when it is a list (a stray string would otherwise
  iterate character-by-character);
- a source counts as must_cover only when must_cover is exactly the boolean True.
Structural type errors themselves are reported by validate_contract.py.
"""
import sys

import _contract as c


def check(contract):
    if not isinstance(contract, dict):
        return (False, ["contract must be a JSON object"])
    reasons = []
    sources = contract.get("sources", []) or []
    acceptance = contract.get("acceptance", []) or []

    covered = set()
    for a in acceptance:
        if isinstance(a, dict):
            covers = a.get("covers")
            if isinstance(covers, list):
                covered.update(cid for cid in covers if isinstance(cid, str))

    for s in sources:
        sid = s.get("id") if isinstance(s, dict) else None
        if isinstance(s, dict) and s.get("must_cover") is True:
            if not isinstance(sid, str) or sid not in covered:
                reasons.append("must_cover source not covered by any acceptance: %s" % sid)

    return (len(reasons) == 0, reasons)


def main(argv):
    if len(argv) != 2:
        print("usage: coverage_gate.py <contract.json>")
        return 2
    contract, err = c.read_contract(argv[1])
    if err:
        print("[FAIL] coverage_gate\n  - %s" % err)
        return 2
    return c.report("coverage_gate", *check(contract))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
