#!/usr/bin/env python3
"""① gate: structural validity of a contract.json. Python 3 stdlib only.

check(contract) -> (ok: bool, reasons: list[str])
Exit 0 means the contract is structurally complete, correctly typed, internally
consistent (covers reference declared sources, ids are unique), and free of
placeholder tokens.
"""
import sys

import _contract as c


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _non_empty_string(v):
    return isinstance(v, str) and bool(v.strip())


def check(contract):
    if not isinstance(contract, dict):
        return (False, ["contract must be a JSON object"])

    reasons = []

    for field in c.REQUIRED_FIELDS:
        if field not in contract:
            reasons.append("missing required field: %s" % field)

    if "id" in contract and not c.is_kebab(contract["id"]):
        reasons.append("id must be kebab-case (got %r)" % contract.get("id"))

    intent = contract.get("intent", "")
    if not isinstance(intent, str) or c.text_units(intent) < c.MIN_INTENT_UNITS:
        reasons.append("intent must be a substantive paragraph (>= %d words / CJK chars)"
                       % c.MIN_INTENT_UNITS)

    if contract.get("confidence") not in c.CONFIDENCE_VALUES:
        reasons.append("confidence must be one of %s" % (c.CONFIDENCE_VALUES,))

    if contract.get("status") not in c.STATUS_ORDER:
        reasons.append("status must be one of %s" % (c.STATUS_ORDER,))

    # --- sources: shape, types, unique ids ---
    source_ids = []
    sources = contract.get("sources")
    if not isinstance(sources, list) or not sources:
        reasons.append("sources must be a non-empty list")
    else:
        for i, s in enumerate(sources):
            if not (isinstance(s, dict) and all(k in s for k in ("id", "ref", "must_cover"))):
                reasons.append("sources[%d] needs id, ref, must_cover" % i)
                continue
            if not _non_empty_string(s["id"]):
                reasons.append("sources[%d].id must be a non-empty string" % i)
            if not _non_empty_string(s["ref"]):
                reasons.append("sources[%d].ref must be a non-empty string" % i)
            if not isinstance(s["must_cover"], bool):
                reasons.append("sources[%d].must_cover must be a boolean (got %r)"
                               % (i, s["must_cover"]))
            sid = s["id"]
            if isinstance(sid, str) and sid in source_ids:
                reasons.append("duplicate source id: %r" % sid)
            if isinstance(sid, str):
                source_ids.append(sid)

    # --- entities: shape ---
    entities = contract.get("entities")
    if not isinstance(entities, list) or not entities:
        reasons.append("entities must be a non-empty list")
    else:
        for i, e in enumerate(entities):
            if not (isinstance(e, dict) and all(k in e for k in ("name", "kind"))):
                reasons.append("entities[%d] needs name, kind" % i)
                continue
            if not _non_empty_string(e["name"]):
                reasons.append("entities[%d].name must be a non-empty string" % i)
            if not _non_empty_string(e["kind"]):
                reasons.append("entities[%d].kind must be a non-empty string" % i)

    # --- acceptance: shape, types, unique ids, covers reference real sources ---
    acc_ids = []
    acceptance = contract.get("acceptance")
    if not isinstance(acceptance, list) or not acceptance:
        reasons.append("acceptance must be a non-empty list")
    else:
        for i, a in enumerate(acceptance):
            if not (isinstance(a, dict) and all(k in a for k in ("id", "statement", "testable", "covers"))):
                reasons.append("acceptance[%d] needs id, statement, testable, covers" % i)
                continue
            if not c.is_kebab(a["id"]):
                reasons.append("acceptance[%d].id must be kebab-case (got %r)" % (i, a["id"]))
            if not _non_empty_string(a["statement"]):
                reasons.append("acceptance[%s].statement must be a non-empty string" % a["id"])
            if not isinstance(a["testable"], bool):
                reasons.append("acceptance[%s].testable must be a boolean" % a["id"])
            aid = a["id"]
            if isinstance(aid, str) and aid in acc_ids:
                reasons.append("duplicate acceptance id: %r" % aid)
            if isinstance(aid, str):
                acc_ids.append(aid)
            covers = a["covers"]
            if not isinstance(covers, list):
                reasons.append("acceptance[%s].covers must be a list (got %r)" % (aid, covers))
            else:
                for cid in covers:
                    if not isinstance(cid, str):
                        reasons.append("acceptance[%s].covers entries must be strings (got %r)"
                                       % (aid, cid))
                    elif cid not in source_ids:
                        reasons.append("acceptance[%s].covers references unknown source id: %r"
                                       % (aid, cid))

    # --- optional fields used by ④: type-check when present ---
    if "tasks_open" in contract and not _is_int(contract["tasks_open"]):
        reasons.append("tasks_open must be an integer")
    if "tests" in contract:
        t = contract["tests"]
        if not isinstance(t, dict):
            reasons.append("tests must be an object")
        else:
            for k in ("passed", "skipped"):
                if k in t and not isinstance(t[k], bool):
                    reasons.append("tests.%s must be a boolean" % k)

    placeholders = c.find_placeholders(contract)
    if placeholders:
        reasons.append("forbidden placeholder tokens present: %s" % placeholders)

    return (len(reasons) == 0, reasons)


def main(argv):
    if len(argv) != 2:
        print("usage: validate_contract.py <contract.json>")
        return 2
    contract, err = c.read_contract(argv[1])
    if err:
        print("[FAIL] validate_contract\n  - %s" % err)
        return 2
    return c.report("validate_contract", *check(contract))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
