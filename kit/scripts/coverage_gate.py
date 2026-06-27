#!/usr/bin/env python3
"""② gate: every must_cover source is covered by >=1 acceptance criterion.

check(contract, strict=False) -> (ok, reasons). Exit 0 means coverage is complete.

Defensive about types (so a malformed contract can't slip through by accident):
- a `covers` value is only honoured when it is a list (a stray string would otherwise
  iterate character-by-character);
- a source counts as must_cover only when must_cover is exactly the boolean True.
Structural type errors themselves are reported by validate_contract.py.

A script can guarantee *structural* coverage (a source id is referenced) but not *semantic*
faithfulness ("does this criterion really capture the source?") — that needs judgement, and an
LLM judge would re-introduce the non-determinism the kit exists to avoid. `--strict` raises the
floor instead: every must_cover source needs a covering criterion that is testable and
substantive (not a one-word stub), AND a reviewer must sign off `review.coverage_substantive`.
That signoff is a *second key* the implementing model may not turn on itself.
"""
import sys

import _contract as c

_MIN_STATEMENT_UNITS = 4


def check(contract, strict=False):
    if not isinstance(contract, dict):
        return (False, ["contract must be a JSON object"])
    reasons = []
    sources = contract.get("sources", []) or []
    acceptance = contract.get("acceptance", []) or []

    covered = set()
    cover_map = {}
    for a in acceptance:
        if isinstance(a, dict):
            covers = a.get("covers")
            if isinstance(covers, list):
                for cid in covers:
                    if isinstance(cid, str):
                        covered.add(cid)
                        cover_map.setdefault(cid, []).append(a)

    for s in sources:
        sid = s.get("id") if isinstance(s, dict) else None
        if isinstance(s, dict) and s.get("must_cover") is True:
            if not isinstance(sid, str) or sid not in covered:
                reasons.append("must_cover source not covered by any acceptance: %s" % sid)
            elif strict:
                substantive = [a for a in cover_map.get(sid, [])
                               if a.get("testable") is True
                               and c.text_units(a.get("statement", "")) >= _MIN_STATEMENT_UNITS]
                if not substantive:
                    reasons.append("strict: must_cover source %s is covered only by a thin or "
                                   "untestable criterion (need a testable statement >= %d units)"
                                   % (sid, _MIN_STATEMENT_UNITS))

    if strict:
        rev = contract.get("review")
        if not (isinstance(rev, dict) and rev.get("coverage_substantive") is True):
            reasons.append("strict: review.coverage_substantive must be true — a reviewer (not the "
                           "implementing model) signs off that coverage is real, not just nominal")

    return (len(reasons) == 0, reasons)


def main(argv):
    flags = argv[1:]
    strict = "--strict" in flags
    args = [a for a in flags if a != "--strict"]
    if len(args) != 1:
        print("usage: coverage_gate.py [--strict] <contract.json>")
        return 2
    contract, err = c.read_contract(args[0])
    if err:
        print("[FAIL] coverage_gate\n  - %s" % err)
        return 2
    return c.report("coverage_gate", *check(contract, strict=strict))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
