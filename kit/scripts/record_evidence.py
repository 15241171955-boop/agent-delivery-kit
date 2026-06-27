#!/usr/bin/env python3
"""Produce Definition-of-Done evidence from real command runs — not model self-report.

This is the trusted half of the ④ gate. **CI (not the model) runs it.** It executes the
contract's declared verification command(s), captures the real exit code(s), and
*overwrites* the evidence fields (`tests`, `acceptance[].passed`) plus an `evidence`
attestation `{ "source": "runner", ... }`. `dod_check.py --require-measured` then trusts
only runner-stamped, internally-consistent evidence — closing the gap where a model could
write `tests.passed: true` without a real run.

Command resolution (first wins), so the model's contract can't dictate what executes:

    --test-command CLI  >  $ADK_TEST_COMMAND  >  contract.verification.test_command

Commands are split with shlex and run WITHOUT a shell (no `&&`, no globbing). Pin the
command in CI (env or flag) for the strongest provenance.

Python 3 standard library only.

usage:
  record_evidence.py <contract.json> [--test-command CMD] [--cwd DIR]
                     [--out PATH] [--timeout S] [--verify] [--quiet]
"""
import argparse
import datetime
import json
import os
import shlex
import subprocess
import sys

import _contract as c

DEFAULT_TIMEOUT = 600


def _now_utc():
    return (datetime.datetime.now(datetime.timezone.utc)
            .replace(microsecond=0).isoformat())


def _as_argv(command):
    """A string is shlex-split (no shell); an already-split list is used as-is."""
    if isinstance(command, list):
        return [str(x) for x in command]
    return shlex.split(command)


def _run(command, cwd=None, timeout=DEFAULT_TIMEOUT):
    """Run a command; return (returncode, combined_output). Never raises on failure."""
    try:
        proc = subprocess.run(_as_argv(command), cwd=cwd, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True, timeout=timeout)
        return proc.returncode, proc.stdout
    except subprocess.TimeoutExpired:
        return 124, "timed out after %ss" % timeout
    except FileNotFoundError as exc:
        return 127, "command not found: %s" % exc
    except (OSError, ValueError) as exc:
        return 126, "could not run command: %s" % exc


def resolve_test_command(contract, cli_command):
    """First of: CLI override, $ADK_TEST_COMMAND, contract.verification.test_command."""
    if cli_command:
        return cli_command
    env = os.environ.get("ADK_TEST_COMMAND")
    if env:
        return env
    ver = contract.get("verification")
    if isinstance(ver, dict) and ver.get("test_command"):
        return ver["test_command"]
    return None


def record(contract, cli_command=None, cwd=None, timeout=DEFAULT_TIMEOUT):
    """Mutate `contract` in place with measured evidence. Return (ok, summary_lines)."""
    if not isinstance(contract, dict):
        return (False, ["contract must be a JSON object"])

    test_command = resolve_test_command(contract, cli_command)
    if not test_command:
        return (False, ["no test command — set --test-command, $ADK_TEST_COMMAND, "
                        "or verification.test_command"])

    lines = []
    rc, _out = _run(test_command, cwd=cwd, timeout=timeout)
    suite_passed = (rc == 0)
    contract["tests"] = {"passed": suite_passed, "skipped": False}
    shown = test_command if isinstance(test_command, str) else " ".join(map(str, test_command))
    lines.append("tests: ran %r -> exit %d (%s)"
                 % (shown, rc, "passed" if suite_passed else "FAILED"))

    # Per-criterion commands when declared; otherwise a criterion rides on the suite.
    ver = contract.get("verification") if isinstance(contract.get("verification"), dict) else {}
    acc_cmds = ver.get("acceptance_commands")
    acc_cmds = acc_cmds if isinstance(acc_cmds, dict) else {}
    measured = {}
    for a in contract.get("acceptance") or []:
        if not isinstance(a, dict):
            continue
        aid = a.get("id")
        cmd = acc_cmds.get(aid) if isinstance(aid, str) else None
        if cmd:
            arc, _ = _run(cmd, cwd=cwd, timeout=timeout)
            a["passed"] = (arc == 0)
            measured[aid] = "cmd:exit=%d" % arc
        else:
            a["passed"] = suite_passed
            measured[aid] = "suite"
    if measured:
        lines.append("acceptance: " + ", ".join("%s=%s" % kv for kv in measured.items()))

    contract["evidence"] = {
        "source": "runner",
        "runner": "agent-delivery-kit/record_evidence.py",
        "recorded_at": _now_utc(),
        "test_command": shown,
        "test_returncode": rc,
    }
    return (True, lines)


def main(argv):
    parser = argparse.ArgumentParser(
        prog="record_evidence.py",
        description="Run the contract's verification commands and stamp real DoD evidence.")
    parser.add_argument("contract")
    parser.add_argument("--test-command", dest="test_command",
                        help="override the suite command (highest precedence)")
    parser.add_argument("--cwd", dest="cwd",
                        help="working directory for commands (default: the contract's directory)")
    parser.add_argument("--out", dest="out_path",
                        help="write the updated contract here (default: in place)")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT,
                        help="per-command timeout in seconds (default %d)" % DEFAULT_TIMEOUT)
    parser.add_argument("--verify", action="store_true",
                        help="after recording, run dod_check --require-measured; on pass set "
                             "status=verified; the exit code reflects the verdict")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv[1:])

    contract, err = c.read_contract(args.contract)
    if err:
        print("[FAIL] record_evidence\n  - %s" % err)
        return 2

    cwd = args.cwd or os.path.dirname(os.path.abspath(args.contract)) or None
    ok, lines = record(contract, cli_command=args.test_command, cwd=cwd, timeout=args.timeout)
    if not ok:
        print("[FAIL] record_evidence")
        for ln in lines:
            print("  - %s" % ln)
        return 2

    verdict_rc = 0
    if args.verify:
        import dod_check
        passed, reasons = dod_check.check(contract, require_measured=True)
        if passed:
            contract["status"] = "verified"
            lines.append("dod_check --require-measured: PASS -> status=verified")
        else:
            verdict_rc = 1
            lines.append("dod_check --require-measured: FAIL")
            lines.extend("  ! %s" % r for r in reasons)

    out_path = args.out_path or args.contract
    payload = json.dumps(contract, indent=2, ensure_ascii=False) + "\n"
    try:
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(payload)
    except OSError as exc:
        print("[FAIL] record_evidence\n  - could not write %s (%s)" % (out_path, exc))
        return 2

    if not args.quiet:
        print("[%s] record_evidence -> %s" % ("PASS" if verdict_rc == 0 else "FAIL", out_path))
        for ln in lines:
            print("  - %s" % ln)
    return verdict_rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
