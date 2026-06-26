#!/usr/bin/env python3
"""Stdlib-only tests for the run_pipeline orchestrator.

Run:  python3 kit/scripts/tests/test_pipeline.py
"""
import copy
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(SCRIPTS))
SAMPLE = os.path.join(ROOT, "examples", "contract.sample.json")
BAD = os.path.join(ROOT, "examples", "contract.bad.json")
sys.path.insert(0, SCRIPTS)

import run_pipeline  # noqa: E402


def _load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


class PipelineTests(unittest.TestCase):
    def test_sample_all_green(self):
        results = run_pipeline.run_once(_load(SAMPLE))
        self.assertEqual(len(results), 4)
        self.assertTrue(run_pipeline.all_ok(results))

    def test_draft_blocks_apply_and_verify(self):
        d = _load(SAMPLE); d["status"] = "draft"
        by_gate = {r["gate"]: r["ok"] for r in run_pipeline.run_once(d)}
        self.assertTrue(by_gate["validate_contract"])
        self.assertTrue(by_gate["coverage_gate"])
        self.assertFalse(by_gate["gate_check"])   # not reviewed yet
        self.assertFalse(by_gate["dod_check"])     # not applied yet

    def test_main_exit_zero_on_sample(self):
        self.assertEqual(run_pipeline.main(["run_pipeline.py", SAMPLE, "--quiet"]), 0)

    def test_main_exit_one_on_bad(self):
        self.assertEqual(run_pipeline.main(["run_pipeline.py", BAD, "--quiet"]), 1)

    def test_report_and_json_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            rep = os.path.join(tmp, "report.html")
            js = os.path.join(tmp, "run.json")
            rc = run_pipeline.main(["run_pipeline.py", SAMPLE, "--quiet",
                                    "--report", rep, "--json", js])
            self.assertEqual(rc, 0)
            self.assertTrue(os.path.exists(rep) and os.path.exists(js))
            with open(rep, encoding="utf-8") as fh:
                self.assertIn("gate dashboard", fh.read())
            data = _load(js)
            self.assertTrue(data["all_ok"])
            self.assertEqual(data["attempts"], 1)

    def test_retry_loops_then_reports_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            draft = _load(SAMPLE); draft["status"] = "draft"
            cpath = os.path.join(tmp, "c.json")
            js = os.path.join(tmp, "run.json")
            with open(cpath, "w", encoding="utf-8") as fh:
                json.dump(draft, fh)
            rc = run_pipeline.main(["run_pipeline.py", cpath, "--quiet",
                                    "--max-attempts", "2", "--retry-delay", "0", "--json", js])
            self.assertEqual(rc, 1)
            self.assertEqual(_load(js)["attempts"], 2)  # retried because still blocked

    def test_non_object_contract_does_not_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "c.json")
            with open(p, "w", encoding="utf-8") as fh:
                json.dump([], fh)
            self.assertEqual(run_pipeline.main(["run_pipeline.py", p, "--quiet"]), 1)

    def test_negative_retry_delay_rejected(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                run_pipeline.main(["run_pipeline.py", SAMPLE, "--retry-delay", "-1", "--quiet"])

    def test_main_handles_malformed_and_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()):
            p = os.path.join(tmp, "bad.json")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write("{bad json")
            self.assertEqual(run_pipeline.main(["run_pipeline.py", p, "--quiet"]), 2)
            self.assertEqual(
                run_pipeline.main(["run_pipeline.py", os.path.join(tmp, "nope.json"), "--quiet"]), 2)

    def test_main_handles_unwritable_report_path(self):
        # a report/json path in a non-existent directory must fail cleanly (2), not traceback
        with contextlib.redirect_stdout(io.StringIO()):
            rc = run_pipeline.main(["run_pipeline.py", SAMPLE, "--quiet",
                                    "--report", "/no/such/dir/r.html"])
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
