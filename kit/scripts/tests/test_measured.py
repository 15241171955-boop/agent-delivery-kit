#!/usr/bin/env python3
"""Stdlib-only tests for measured mode: record_evidence, dod_check --require-measured,
coverage --strict, and the hardened placeholder detector.

Run:  python3 kit/scripts/tests/test_measured.py
"""
import contextlib
import copy
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)                    # kit/scripts
ROOT = os.path.dirname(os.path.dirname(SCRIPTS))   # repo root
SAMPLE = os.path.join(ROOT, "examples", "contract.sample.json")
MEASURED = os.path.join(ROOT, "examples", "measured", "contract.applied.json")
sys.path.insert(0, SCRIPTS)

import _contract                  # noqa: E402
import validate_contract          # noqa: E402
import coverage_gate              # noqa: E402
import dod_check                  # noqa: E402
import record_evidence           # noqa: E402

PASS_CMD = '%s -c "import sys; sys.exit(0)"' % sys.executable
FAIL_CMD = '%s -c "import sys; sys.exit(1)"' % sys.executable


def _load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


class MeasuredEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.sample = _load(SAMPLE)
        self.measured = _load(MEASURED)

    # --- the measured example ships honestly incomplete ---
    def test_measured_example_is_valid_but_not_yet_done(self):
        self.assertTrue(validate_contract.check(self.measured)[0])      # structurally fine
        self.assertFalse(dod_check.check(self.measured)[0])             # tests skipped, ac not passed
        self.assertFalse(dod_check.check(self.measured, require_measured=True)[0])

    # --- require_measured rejects model-declared evidence (the whole point of #1) ---
    def test_declared_sample_passes_normally_but_fails_require_measured(self):
        self.assertTrue(dod_check.check(self.sample)[0])               # declared mode: green
        ok, reasons = dod_check.check(self.sample, require_measured=True)
        self.assertFalse(ok)                                          # no runner attestation
        self.assertTrue(any("evidence.source must be 'runner'" in r for r in reasons))

    # --- record() writes real evidence from a passing run ---
    def test_record_passing_run_makes_dod_measured_green(self):
        c = copy.deepcopy(self.measured)
        ok, _ = record_evidence.record(c, cli_command=PASS_CMD)
        self.assertTrue(ok)
        self.assertEqual(c["tests"], {"passed": True, "skipped": False})
        self.assertTrue(all(a["passed"] is True for a in c["acceptance"]))
        self.assertEqual(c["evidence"]["source"], "runner")
        self.assertEqual(c["evidence"]["test_returncode"], 0)
        c["status"] = "verified"
        self.assertTrue(dod_check.check(c, require_measured=True)[0])

    # --- a failing suite cannot be rounded up ---
    def test_record_failing_run_blocks_dod(self):
        c = copy.deepcopy(self.measured)
        record_evidence.record(c, cli_command=FAIL_CMD)
        self.assertEqual(c["tests"], {"passed": False, "skipped": False})
        self.assertFalse(all(a["passed"] for a in c["acceptance"]))
        c["status"] = "verified"
        self.assertFalse(dod_check.check(c, require_measured=True)[0])

    # --- tampering after the run is caught by the cross-check ---
    def test_tampered_evidence_is_rejected(self):
        c = copy.deepcopy(self.measured)
        record_evidence.record(c, cli_command=PASS_CMD)
        c["status"] = "verified"
        self.assertTrue(dod_check.check(c, require_measured=True)[0])   # honest -> green
        c["evidence"]["test_returncode"] = 1                          # claim a failing run...
        ok, reasons = dod_check.check(c, require_measured=True)         # ...while tests.passed stays true
        self.assertFalse(ok)
        self.assertTrue(any("disagrees with evidence.test_returncode" in r for r in reasons))

    def test_record_without_command_fails_cleanly(self):
        c = copy.deepcopy(self.measured)
        c.pop("verification", None)
        ok, reasons = record_evidence.record(c, cli_command=None)
        self.assertFalse(ok)
        self.assertTrue(any("no test command" in r for r in reasons))

    # --- the CLI: --verify records, verifies, and stamps status in one shot ---
    def test_cli_verify_sets_status_and_exit_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "c.json")
            shutil.copy(MEASURED, path)
            with contextlib.redirect_stdout(io.StringIO()):
                rc = record_evidence.main(["record_evidence.py", path,
                                           "--test-command", PASS_CMD, "--verify"])
            self.assertEqual(rc, 0)
            out = _load(path)
            self.assertEqual(out["status"], "verified")
            self.assertEqual(out["evidence"]["source"], "runner")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(
                    dod_check.main(["dod_check.py", "--require-measured", path]), 0)

    def test_cli_verify_failing_suite_exits_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "c.json")
            shutil.copy(MEASURED, path)
            with contextlib.redirect_stdout(io.StringIO()):
                rc = record_evidence.main(["record_evidence.py", path,
                                           "--test-command", FAIL_CMD, "--verify"])
            self.assertEqual(rc, 1)
            self.assertNotEqual(_load(path).get("status"), "verified")

    def test_cli_test_command_overrides_contract(self):
        # contract declares a passing command; CLI override forces failure -> precedence honoured
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "c.json")
            shutil.copy(MEASURED, path)
            with contextlib.redirect_stdout(io.StringIO()):
                record_evidence.main(["record_evidence.py", path,
                                      "--test-command", FAIL_CMD, "--quiet"])
            self.assertFalse(_load(path)["tests"]["passed"])


class StrictCoverageTests(unittest.TestCase):
    def setUp(self):
        self.measured = _load(MEASURED)

    def test_strict_passes_with_substantive_coverage_and_signoff(self):
        self.assertTrue(coverage_gate.check(self.measured, strict=True)[0])

    def test_strict_requires_reviewer_two_key(self):
        d = copy.deepcopy(self.measured); d.pop("review", None)
        ok, reasons = coverage_gate.check(d, strict=True)
        self.assertFalse(ok)
        self.assertTrue(any("coverage_substantive" in r for r in reasons))

    def test_strict_model_cannot_selfsign_with_thin_acceptance(self):
        d = copy.deepcopy(self.measured)
        d["acceptance"][0]["statement"] = "ok"        # one unit, not substantive
        self.assertFalse(coverage_gate.check(d, strict=True)[0])

    def test_nonstrict_unchanged(self):
        # the default gate is untouched by all of the above
        d = copy.deepcopy(self.measured); d.pop("review", None)
        self.assertTrue(coverage_gate.check(d)[0])


class PlaceholderTests(unittest.TestCase):
    def test_new_word_tokens_flagged(self):
        for token in ("WIP", "to-do", "XXX", "PLACEHOLDER", "lorem ipsum", "TBD"):
            self.assertTrue(_contract.find_placeholders({"x": "this is %s here" % token}),
                            msg="%r should be flagged" % token)

    def test_case_insensitive(self):
        self.assertTrue(_contract.find_placeholders({"x": "a wip note"}))
        self.assertTrue(_contract.find_placeholders({"x": "a FixMe note"}))

    def test_no_false_positive_inside_words(self):
        # 'wip' inside 'wipe', 'tbd' inside a hash-like token must NOT trip the detector
        self.assertEqual(_contract.find_placeholders({"x": "wipe down the export list"}), [])
        self.assertEqual(_contract.find_placeholders({"x": "commit a1tbd2 is fine"}), [])

    def test_validate_rejects_contract_with_wip(self):
        d = _load(SAMPLE); d["acceptance"][0]["statement"] = "WIP wire up the button"
        self.assertFalse(validate_contract.check(d)[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
