"""Shared, dependency-free helpers for the Spec-Gated Delivery gate scripts.

Python 3 standard library only. The contract is a JSON document; see
kit/shared/contract-schema.md for the authoritative field reference.
"""
import json
import re

REQUIRED_FIELDS = ("id", "intent", "sources", "entities", "acceptance", "confidence", "status")
CONFIDENCE_VALUES = ("explicit", "suggest", "fallback")
STATUS_ORDER = ("draft", "reviewed", "applied", "verified")
MIN_INTENT_UNITS = 10

# Placeholder detection (invariant: no fake completeness). Matched as substrings;
# these markers do not occur inside normal prose.
FORBIDDEN_SUBSTRINGS = ("TODO", "TBD", "FIXME", "<...>", "???")

_KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def load_contract(path):
    """Load a contract.json from disk (UTF-8). Raises on a missing or invalid file."""
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def read_contract(path):
    """CLI-safe load. Returns (contract, error): on success error is None; on failure
    contract is None and error is a human-readable message (so callers print a clean
    [FAIL] instead of a traceback)."""
    try:
        return (load_contract(path), None)
    except FileNotFoundError:
        return (None, "no such file: %s" % path)
    except OSError as exc:
        return (None, "cannot read %s (%s)" % (path, exc))
    except json.JSONDecodeError as exc:
        return (None, "invalid JSON in %s (%s)" % (path, exc))


def is_kebab(value):
    return bool(isinstance(value, str) and _KEBAB.match(value))


def _is_cjk(ch):
    o = ord(ch)
    return (0x4E00 <= o <= 0x9FFF       # CJK Unified Ideographs
            or 0x3400 <= o <= 0x4DBF    # CJK Extension A
            or 0xF900 <= o <= 0xFAFF    # CJK Compatibility Ideographs
            or 0x3040 <= o <= 0x30FF)   # Hiragana + Katakana


def text_units(text):
    """Length metric that works for space-separated and non-space scripts alike.

    Each CJK character counts as one unit; runs of non-CJK text are counted as
    whitespace-separated words. So a 12-character CJK string scores 12, and
    'add a CSV export' scores 4 — an intent in a non-space-delimited script is
    not rejected as "too short".
    """
    if not isinstance(text, str):
        return 0
    cjk = sum(1 for ch in text if _is_cjk(ch))
    latin = "".join(" " if _is_cjk(ch) else ch for ch in text)
    words = [w for w in latin.split() if any(c.isalnum() for c in w)]
    return cjk + len(words)


def _walk_strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _walk_strings(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from _walk_strings(v)


def find_placeholders(contract):
    """Return the sorted set of forbidden placeholder tokens found in any string value."""
    hits = set()
    for s in _walk_strings(contract):
        for tok in FORBIDDEN_SUBSTRINGS:
            if tok in s:
                hits.add(tok)
    return sorted(hits)


def status_index(contract):
    """Index of the contract's status in STATUS_ORDER, or -1 if unknown."""
    try:
        return STATUS_ORDER.index(contract.get("status"))
    except ValueError:
        return -1


def at_least(contract, status):
    """True if the contract's status is `status` or later in the lifecycle."""
    return status_index(contract) >= STATUS_ORDER.index(status)


def report(name, ok, reasons):
    """Print a PASS/FAIL report; return a process exit code (0 ok, 1 fail)."""
    if ok:
        print("[PASS] %s" % name)
        return 0
    print("[FAIL] %s" % name)
    for r in dict.fromkeys(reasons):  # de-duplicate, preserve order
        print("  - %s" % r)
    return 1
