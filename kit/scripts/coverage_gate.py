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
    reasons = []
    sources = contract.get("sources", []) or []
    acceptance = contract.get("acceptance", []) or []

    covered = set()
    for a in acceptance:
        if isinstance(a, dict):
            covers = a.get("covers")
            if isinstance(covers, list):
                covered.update(covers)

    for s in sources:
        if isinstance(s, dict) and s.get("must_cover") is True and s.get("id") not in covered:
            reasons.append("must_cover source not covered by any acceptance: %s" % s.get("id"))

    return (len(reasons) == 0, reasons)


def main(argv):
    if len(argv) != 2:
        print("usage: coverage_gate.py <contract.json>")
        return 2
    return c.report("coverage_gate", *check(c.load_contract(argv[1])))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
