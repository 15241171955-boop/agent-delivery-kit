#!/usr/bin/env python3
"""Orchestrate the four Spec-Gated Delivery gates over one contract.

Runs validate_contract -> coverage_gate -> gate_check -> dod_check, prints a status
board, optionally retries (re-loading the contract each attempt so external fixes are
picked up), and can emit a JSON result and a self-contained HTML dashboard.

Python 3 standard library only. Exit 0 iff all four gates pass.

usage:
  run_pipeline.py <contract.json> [--max-attempts N] [--retry-delay S]
                  [--json run.json] [--report report.html] [--quiet]
"""
import argparse
import datetime
import html
import json
import sys
import time

import _contract as c
import validate_contract
import coverage_gate
import gate_check
import dod_check

# stage mark, stage name, gate name, check function
STAGES = (
    ("(1)", "specify", "validate_contract", validate_contract.check),
    ("(2)", "review", "coverage_gate", coverage_gate.check),
    ("(3)", "apply", "gate_check", gate_check.check),
    ("(4)", "verify", "dod_check", dod_check.check),
)


def run_once(contract):
    """Run every gate over the contract; return a list of per-stage result dicts."""
    results = []
    for mark, stage, gate, check in STAGES:
        ok, reasons = check(contract)
        results.append({"mark": mark, "stage": stage, "gate": gate,
                        "ok": bool(ok), "reasons": list(reasons)})
    return results


def all_ok(results):
    return all(r["ok"] for r in results)


def render_board(results, contract_id, attempt):
    """Plain-text status board for the terminal."""
    lines = ["",
             "Spec-Gated Delivery - pipeline run  (contract: %s, attempt %d)" % (contract_id, attempt)]
    for r in results:
        lines.append("  %-4s %-8s %-18s %s"
                     % (r["mark"], r["stage"], r["gate"], "PASS" if r["ok"] else "FAIL"))
        if not r["ok"]:
            for reason in r["reasons"]:
                lines.append("         - %s" % reason)
    passed = sum(1 for r in results if r["ok"])
    verdict = "ALL GREEN" if passed == len(results) else "BLOCKED"
    lines.append("Result: %s (%d/%d)" % (verdict, passed, len(results)))
    return "\n".join(lines)


_CSS = """
body{font:14px/1.5 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;margin:2rem;color:#1f2328;background:#fff}
h1{font-size:1.25rem;margin:0 0 .25rem}.sub{color:#656d76;margin:0 0 1.25rem}
.badge{display:inline-block;padding:.2rem .7rem;border-radius:999px;color:#fff;font-weight:600}
.flow{display:flex;align-items:center;flex-wrap:wrap;gap:.25rem;margin:1.25rem 0}
.node{border:2px solid;border-radius:10px;padding:.55rem .8rem;text-align:center;min-width:118px}
.node .mark{font-size:1.05rem}.node small{color:#656d76;display:block;margin:.15rem 0}
.node .status{color:#fff;border-radius:6px;font-size:.72rem;padding:.08rem 0;margin-top:.35rem}
.arrow{color:#8c959f;font-size:1.2rem;padding:0 .15rem}
table{border-collapse:collapse;width:100%;margin-top:.5rem}
th,td{border:1px solid #d0d7de;padding:.5rem .6rem;text-align:left;vertical-align:top}
th{background:#f6f8fa}td.pass{color:#1a7f37;font-weight:600}td.fail{color:#cf222e;font-weight:600}
code{background:#f6f8fa;padding:.05rem .3rem;border-radius:4px}
footer{margin-top:1.5rem;color:#8c959f;font-size:.8rem}
"""


def render_html(results, contract_id, attempt):
    """Self-contained HTML dashboard (no external assets)."""
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    passed = sum(1 for r in results if r["ok"])
    total = len(results)
    overall_color = "#1a7f37" if passed == total else "#cf222e"
    overall_text = "ALL GREEN" if passed == total else "BLOCKED"

    nodes = []
    for i, r in enumerate(results):
        color = "#1a7f37" if r["ok"] else "#cf222e"
        if i:
            nodes.append("<span class='arrow'>&rarr;</span>")
        nodes.append(
            "<div class='node' style='border-color:%s;color:%s'>"
            "<div class='mark'>%s</div><div>%s</div><small>%s</small>"
            "<div class='status' style='background:%s'>%s</div></div>"
            % (color, color, r["mark"], html.escape(r["stage"]), html.escape(r["gate"]),
               color, "PASS" if r["ok"] else "FAIL"))

    rows = []
    for r in results:
        cls = "pass" if r["ok"] else "fail"
        reasons = "<br>".join(html.escape(x) for x in r["reasons"]) if r["reasons"] else "&mdash;"
        rows.append("<tr><td>%s&nbsp;%s</td><td><code>%s</code></td>"
                    "<td class='%s'>%s</td><td>%s</td></tr>"
                    % (r["mark"], html.escape(r["stage"]), html.escape(r["gate"]),
                       cls, "PASS" if r["ok"] else "FAIL", reasons))

    return (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>Spec-Gated Delivery - %s</title><style>%s</style></head><body>"
        "<h1>Spec-Gated Delivery - gate dashboard</h1>"
        "<p class='sub'>contract <code>%s</code> &middot; attempt %d &middot; %s</p>"
        "<p><span class='badge' style='background:%s'>%s &nbsp;%d/%d</span></p>"
        "<div class='flow'>%s</div>"
        "<table><thead><tr><th>Stage</th><th>Gate</th><th>Result</th><th>Reasons</th></tr>"
        "</thead><tbody>%s</tbody></table>"
        "<footer>Generated by kit/scripts/run_pipeline.py &middot; self-contained, no external assets.</footer>"
        "</body></html>"
        % (html.escape(contract_id), _CSS, html.escape(contract_id), attempt, html.escape(ts),
           overall_color, overall_text, passed, total, "".join(nodes), "".join(rows)))


def _safe_write(path, text):
    """Write text to path; return None on success, or a clean error message on failure."""
    try:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        return None
    except OSError as exc:
        return "could not write %s (%s)" % (path, exc)


def main(argv):
    parser = argparse.ArgumentParser(
        prog="run_pipeline.py",
        description="Run the four Spec-Gated Delivery gates over a contract.")
    parser.add_argument("contract")
    parser.add_argument("--max-attempts", type=int, default=1,
                        help="re-check up to N times, reloading the contract each time (default 1)")
    parser.add_argument("--retry-delay", type=float, default=2.0,
                        help="seconds to wait between attempts (default 2)")
    parser.add_argument("--json", dest="json_path", help="write machine-readable results here")
    parser.add_argument("--report", dest="report_path", help="write a self-contained HTML dashboard here")
    parser.add_argument("--quiet", action="store_true", help="suppress the terminal board")
    args = parser.parse_args(argv[1:])
    if args.retry_delay < 0:
        parser.error("--retry-delay must be >= 0")
    if args.max_attempts < 1:
        parser.error("--max-attempts must be >= 1")

    attempts_allowed = args.max_attempts
    attempt = 0
    results = []
    contract_id = "?"
    while attempt < attempts_allowed:
        attempt += 1
        contract, err = c.read_contract(args.contract)
        if err:
            print("[FAIL] run_pipeline\n  - %s" % err)
            return 2
        contract_id = contract.get("id", "?") if isinstance(contract, dict) else "?"
        results = run_once(contract)
        if not args.quiet:
            print(render_board(results, contract_id, attempt))
        if all_ok(results) or attempt >= attempts_allowed:
            break
        if not args.quiet:
            print("  not green - retrying in %ss (fix the contract or implementation; gates re-check)"
                  % args.retry_delay)
        time.sleep(args.retry_delay)

    write_err = None
    if args.json_path:
        payload = json.dumps({"contract": contract_id, "attempts": attempt,
                              "all_ok": all_ok(results), "results": results}, indent=2)
        write_err = _safe_write(args.json_path, payload)
    if not write_err and args.report_path:
        write_err = _safe_write(args.report_path, render_html(results, contract_id, attempt))
    if write_err:
        print("[FAIL] run_pipeline\n  - %s" % write_err)
        return 2

    return 0 if all_ok(results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
