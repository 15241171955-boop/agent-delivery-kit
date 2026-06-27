# Measured-mode walkthrough

The difference between *declared* and *measured* evidence — i.e. between the model saying
"tests passed" and a runner proving it.

`contract.applied.json` ships at `status: applied` with **no real evidence**:
`tests.skipped` is `true` and `ac-1.passed` is `false`. The model is *not* allowed to flip
those to green — a runner is.

## 1. The model can't self-attest

```bash
export ADK="$(git rev-parse --show-toplevel)/kit"        # kit root
python3 "$ADK/scripts/dod_check.py" examples/measured/contract.applied.json --require-measured
# [FAIL] dod_check — evidence.source must be 'runner', tests not passed, ...
```

Even the shipped *sample* (which hand-writes `tests.passed: true`) fails this gate, because it
carries no runner attestation:

```bash
python3 "$ADK/scripts/dod_check.py" examples/contract.sample.json --require-measured   # FAIL
```

## 2. The runner records real evidence, then verifies

```bash
cp examples/measured/contract.applied.json /tmp/c.json
python3 "$ADK/scripts/record_evidence.py" /tmp/c.json --verify
# runs verification.test_command, stamps evidence.source=runner, sets status=verified
python3 "$ADK/scripts/dod_check.py" /tmp/c.json --require-measured                      # PASS
```

`record_evidence.py` resolves the command as `--test-command` > `$ADK_TEST_COMMAND` >
`verification.test_command`, so **CI can pin what runs** and ignore whatever the contract
declares. It overwrites `tests`/`acceptance[].passed` from the real exit codes and writes an
`evidence` block; `dod_check --require-measured` then cross-checks that nobody edited those
fields after the run.

In real CI you point `--test-command` at your suite (e.g. `pytest -q`, `npm test`,
`go test ./...`) and make the `dod_check --require-measured` step a required status check.
