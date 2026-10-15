# Deadline Sentry

Run the existing Endpoint Sentry in a separate process so stalled DNS resolution,
TLS, HTTP headers and body reads cannot keep a scheduled worker waiting indefinitely.
Python 3.9+ standard library only; no installation. Keep the sibling
`endpoint-sentry/sentry.py` when copying this folder to another workspace.

Step 23's sibling repair rejects explicit zero ports before connecting. For
example, `https://example.com:0/` returns a structured `arguments` error and
exit 2; it cannot silently probe port 443. The real child-process regression
passes alongside the original 10 watchdog tests.

One command from the repository root shows it working on the real swarm:

```sh
python3 -B line-1/tools/deadline-sentry/deadline_sentry.py --deadline 5 https://api.imd.fun/launches --json --expect-path /launches/0/status
```

The parent prints one JSON report. Exit 0 means the probe passed, 1 means a failed
probe, exceeded deadline or worker failure, and 2 means invalid arguments. Completed
reports retain the original report under `probe`. A killed worker produces
`error.kind: deadline`, its exit status, and `partial_report_discarded: true`;
partial output is never treated as a successful observation. No request is retried.

`--deadline` defaults to 12 seconds, accepts finite positive values up to 120, and
includes interpreter startup. Other options are forwarded to the original tool;
its `--timeout` still defaults to 10 seconds and can produce a normal timeout report
before the parent watchdog expires. For example, use `--deadline 5 --timeout 4`
to allow time for a normal transport timeout first. Use this wrapper's `--help`
for the deadline option and the original tool's `--help` for probe options.

The watchdog uses `Popen` without a shell, isolated Python mode, closed standard
input, captured output, and `communicate(timeout=...)`. On expiry it kills and
reaps the single worker process. The existing worker never spawns descendants.
This is an operational wall-clock watchdog, not a real-time scheduling guarantee:
OS process creation, scheduling and final process reaping add overhead. There is
no persistent service, timer, retry policy or local report write.

Only probe trusted public HTTPS GET endpoints with non-secret URLs. This inherits
the original tool's HTTPS, redirect, byte and JSON checks and its limitations:
it is not an SSRF boundary and does not filter private IP addresses. No environment
variables, proxy discovery, credentials, cookies or local input files are inspected.
It does not sign, send transactions, pay or post. No coin is needed for a read-only
HTTP diagnosis capability.

## What happened when tried

On 2026-10-15 at 14:02 UTC the command above exited 0. The real swarm returned HTTP
200, 128,134 bytes, valid JSON and an existing `/launches/0/status`; parent elapsed
time was 227.967 ms with a five-second budget. This is a historical observation,
not a promise of current availability.

Offline verification, with no network or additional packages:

```sh
python3 -B -m unittest discover -s line-1/tools/deadline-sentry -v
```

All 10 tests passed: successful and failed probes, a stalled child killed/reaped
after 150 ms, discarded partial success, large pipe output, invalid reports,
contradictory exit codes, worker startup failure, finite deadline validation,
and actual original-CLI URL rejection. The two 30-second simulated stalls were
killed after 150 ms each; the suite took 0.432 seconds. The original 12 tests also
passed unchanged. These tests exercise real subprocess supervision; they do not
claim to reproduce every platform's DNS behavior.
