#!/usr/bin/env python3
"""Stdlib-only tests proving the four gates accept the sample contract and reject bad input.

Run:  python3 kit/scripts/tests/test_gates.py
"""
import copy
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)            # kit/scripts
ROOT = os.path.dirname(os.path.dirname(SCRIPTS))  # repo root
SAMPLE = os.path.join(ROOT, "examples", "contract.sample.json")
sys.path.insert(0, SCRIPTS)

import validate_contract          # noqa: E402
import coverage_gate              # noqa: E402
import gate_check                 # noqa: E402
import dod_check                  # noqa: E402


class GateTests(unittest.TestCase):
    def setUp(self):
        with open(SAMPLE, "r", encoding="utf-8") as fh:
            self.c = json.load(fh)

    # --- the sample is a fully verified contract: all four gates green ---
    def test_sample_passes_all_gates(self):
        self.assertTrue(validate_contract.check(self.c)[0])
        self.assertTrue(coverage_gate.check(self.c)[0])
        self.assertTrue(gate_check.check(self.c)[0])
        self.assertTrue(dod_check.check(self.c)[0])

    # --- ① validate rejects bad structure ---
    def test_validate_missing_field(self):
        d = copy.deepcopy(self.c); del d["intent"]
        self.assertFalse(validate_contract.check(d)[0])

    def test_validate_placeholder_token(self):
        d = copy.deepcopy(self.c); d["acceptance"][0]["statement"] = "TODO finish this"
        self.assertFalse(validate_contract.check(d)[0])

    def test_validate_bad_id(self):
        d = copy.deepcopy(self.c); d["id"] = "Add_CSV_Export"
        self.assertFalse(validate_contract.check(d)[0])

    def test_validate_thin_intent(self):
        d = copy.deepcopy(self.c); d["intent"] = "too short"
        self.assertFalse(validate_contract.check(d)[0])

    # --- ① non-space-delimited intent length, exercised via code points (no literal CJK) ---
    def test_validate_accepts_non_space_script_intent(self):
        d = copy.deepcopy(self.c)
        d["intent"] = "".join(chr(0x4E00 + i) for i in range(12))  # 12 CJK code points
        self.assertTrue(validate_contract.check(d)[0],
                        msg="a non-space-delimited intent must not be judged too short")

    # --- ① type/consistency hardening ---
    def test_validate_rejects_must_cover_string(self):
        d = copy.deepcopy(self.c); d["sources"][0]["must_cover"] = "true"
        self.assertFalse(validate_contract.check(d)[0])

    def test_validate_rejects_covers_not_list(self):
        d = copy.deepcopy(self.c); d["acceptance"][0]["covers"] = "prd-2.1"
        self.assertFalse(validate_contract.check(d)[0])

    def test_validate_rejects_unknown_covers_id(self):
        d = copy.deepcopy(self.c); d["acceptance"][0]["covers"] = ["does-not-exist"]
        self.assertFalse(validate_contract.check(d)[0])

    def test_validate_rejects_duplicate_source_id(self):
        d = copy.deepcopy(self.c)
        d["sources"].append({"id": d["sources"][0]["id"], "ref": "dup", "must_cover": False})
        self.assertFalse(validate_contract.check(d)[0])

    def test_validate_rejects_string_tasks_open(self):
        d = copy.deepcopy(self.c); d["tasks_open"] = "0"
        self.assertFalse(validate_contract.check(d)[0])

    # a malformed contract must also be stopped by the downstream gates
    def test_gate_and_dod_reject_must_cover_string(self):
        d = copy.deepcopy(self.c); d["sources"][0]["must_cover"] = "true"
        self.assertFalse(gate_check.check(d)[0])
        self.assertFalse(dod_check.check(d)[0])

    # --- ② coverage rejects an uncovered must_cover source ---
    def test_coverage_uncovered_must_cover(self):
        d = copy.deepcopy(self.c)
        d["sources"].append({"id": "new-src", "ref": "x", "must_cover": True})
        self.assertFalse(coverage_gate.check(d)[0])

    # --- ③ gate_check enforces review + testability before code ---
    def test_gate_check_requires_reviewed(self):
        d = copy.deepcopy(self.c); d["status"] = "draft"
        self.assertFalse(gate_check.check(d)[0])

    def test_gate_check_rejects_untestable(self):
        d = copy.deepcopy(self.c); d["acceptance"][0]["testable"] = False
        self.assertFalse(gate_check.check(d)[0])

    def test_gate_check_rejects_faked_review_with_bad_coverage(self):
        # Faking status:reviewed must not bypass coverage.
        d = copy.deepcopy(self.c)
        d["status"] = "reviewed"
        d["sources"].append({"id": "uncovered-src", "ref": "y", "must_cover": True})
        self.assertFalse(gate_check.check(d)[0])

    # --- ④ dod_check enforces real completion AND pipeline progress ---
    def test_dod_rejects_draft_with_green_evidence(self):
        # status:draft with all-green evidence must NOT pass dod_check.
        d = copy.deepcopy(self.c); d["status"] = "draft"
        self.assertFalse(dod_check.check(d)[0])

    def test_dod_rejects_reviewed_status(self):
        d = copy.deepcopy(self.c); d["status"] = "reviewed"
        self.assertFalse(dod_check.check(d)[0])

    def test_dod_unpassed_acceptance(self):
        d = copy.deepcopy(self.c); d["acceptance"][0]["passed"] = False
        self.assertFalse(dod_check.check(d)[0])

    def test_dod_open_tasks(self):
        d = copy.deepcopy(self.c); d["tasks_open"] = 2
        self.assertFalse(dod_check.check(d)[0])

    def test_dod_skipped_tests_not_verified(self):
        d = copy.deepcopy(self.c); d["tests"] = {"passed": True, "skipped": True}
        self.assertFalse(dod_check.check(d)[0])

    def test_dod_failed_tests(self):
        d = copy.deepcopy(self.c); d["tests"] = {"passed": False, "skipped": False}
        self.assertFalse(dod_check.check(d)[0])

    # --- the shipped bad example must be rejected by every gate ---
    def test_bad_example_rejected_by_all_gates(self):
        with open(os.path.join(ROOT, "examples", "contract.bad.json"), encoding="utf-8") as fh:
            bad = json.load(fh)
        self.assertFalse(validate_contract.check(bad)[0])
        self.assertFalse(coverage_gate.check(bad)[0])
        self.assertFalse(gate_check.check(bad)[0])
        self.assertFalse(dod_check.check(bad)[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
