# Ice — Gathering 23

Reviewed 2026-10-15. **84 line tests and 20 shared integration tests passed.**
Sources and tests were read before execution. All six advertised line check
commands used `python3 -B -m unittest discover -s TOOL -v`, with byte-identical
tool folders under `test/scratch/gathering23/line-N/tools/` so fixture creation
could not change line folders. Shared checks ran in their delivered folders.
[Raw commands/output](test-runs23.json) and [integration checks](integration-checks23.json)
record local observations, not independent certification. Previous audit files
with 22 in their text remain historical records, not this round's findings.

## Line 1 — Public HTTP diagnosis

Tried Endpoint Sentry (17 tests), Deadline Sentry (11 tests), and both README
live commands against `https://api.imd.fun/launches`, requiring JSON and
`/launches/0/status`. Both returned HTTP 200 and 128,503 bytes at 15:33 UTC.
The watchdog finished in 663.022 ms with a five-second budget. Body SHA-256:
`27a9cfce13df0f760dc0bfd25ccbf1cbeecd17b0d1ee64c619ecc6bec81e5d5e`.

Works: bounded bodies, transport classification, JSON checks, redirects and
killing/reaping overdue workers. The previous explicit `:0` port defect is
repaired at both initial and redirect validation. A real watchdog invocation
with `https://api.imd.fun:0/` returned structured `arguments`, exit 2, with no
probe. Valid explicit ports retain their value.

Broken: **no new defect found in the exercised contract**. Direct socket
timeouts alone do not bound DNS/header work; use Deadline Sentry. Neither tool
filters private IPs, so retain its documented trusted public-URL scope.

The goal serves ordinary service diagnostics, not this cave, and is distinct
from the other lines. It fits 21 workers as bounded, read-only diagnosis;
keep hosted monitoring and alert delivery out of scope.

## Line 2 — Exact keyed CSV reconciliation

Tried CSV Reconcile (17 tests) and new CSV Review (6 tests). The original
item/location demo returned expected exit 1: one added, removed, changed and
unchanged key, zero ambiguous keys; lamp quantity changed from `1` to `2`.
The HTML renderer reviewed the real historical token CSV against itself:
exit 0, six unchanged keys (`chain_id`, `token_address`, `field`). Its output
matched the shared renderer byte-for-byte.

Works: exact strings, composite keys, duplicate ambiguity, schema changes,
bounded CSV input and HTML explanations. Tests confirm hostile HTML and control
characters remain inert text, all duplicate occurrences remain visible, and
input errors produce no partial HTML.

Broken: **no defect found in the exercised contract**. HTML output has no byte
cap, and whole-table comparison can use substantial memory even under the
16 MiB/100,000-row input limits. Ignored columns are not redacted from ambiguous
groups. These are documented limitations, not hidden successes.

This serves exports, inventories and migrations beyond the cave and is distinct.
Exact comparison plus a review artifact fits 21 workers; avoid spreadsheet
editing and automatic data repair.

## Line 3 — Static Python import mapping

Tried all 10 tests and the original example in strict mode: four modules,
three edges, one cycle, one missing import, expected exit 1. A real scan of
Deadline Sentry found two modules, one edge, two entrypoints, no issues or
cycles, exit 0. The mapper was also exercised through shared snapshots.

Works: the previous UTF-8 BOM failure is repaired by passing source bytes to
Python's AST parser. UTF-8, Latin-1 and eligible second-line Windows-1252
cookies retain imports/line numbers; invalid encodings become visible parse
issues while healthy files still scan. Collision reporting and iterative
5,000-node graph handling remain covered. Inspected source is never executed.

Broken: **no new defect found in the exercised contract**. Scanning has no total
file/byte budget. External dependencies are not checked for installation,
dynamic imports are not resolved, and parser limits follow the running Python.
The shared one-row-per-module adapter deliberately rejects name collisions.

The goal serves unfamiliar Python projects, not cave records, and is distinct.
It fits 21 workers within one explicit import root. Exclude runtime import
hooks, arbitrary execution and full packaging simulation.

## Line 4 — Offline Ethereum ABI bytes

Tried all 23 tests, the built-in demo (selector `0xa9059cbb`), real CLI calls
with an object-shaped ABI and a missing file, and decoding retained Ethereum
observations through Token Read Plan. Both malformed-file cases now exit 2
with one concise error and no traceback or success output.

Works: the previous malformed ABI/I/O defects are repaired. Structural input
validation, a 1 MiB ABI-file bound, workspace containment, canonical scalar
types, integer widths and Keccak boundary vectors pass. ZTO then IMD symbol,
decimals and supply return bytes at historical block 26,198,502 still decode
exactly. No fresh RPC observation or current-value claim is made this round.

Broken: **no new valid-input defect found in the advertised scalar subset**.
Arrays, tuples, events, fixed point and overloaded names remain unsupported.
Dynamic tails need not be uniquely ordered and the generic decoder accepts
some surplus words. Argument/return data has no total resource budget. The
token adapter rejects noncanonical/surplus returns by round-trip checking.

This serves Ethereum workers outside the cave and repeats no other line.
The literal full-ABI goal is too broad to promise in 21 workers: define success
as scalar function calls plus dynamic bytes/strings, then add one composite
family with independent vectors if capacity permits. Wallets, deployment and
a full SDK are unnecessary. The immutable GOAL.md was not changed.

## Shared work

[Import Drift](../shared/import-drift/README.md) now carries Line 3's Step 23
mapper unchanged and Line 2's HTML renderer with only its engine path adapted.
`compare --format html` makes a self-contained review with the same status
contract as JSON/text. Ten tests passed, including encoded Python source,
inert HTML, input-error handling and deep source graphs.

The real retained Endpoint Sentry snapshot versus today's snapshot shows one
changed module: `test_sentry` gained `unittest import mock`; the main module's
import structure is unchanged. [HTML review](../shared/import-drift/observed-review23.html)
and [text delta](import-delta23.md) make this reviewable. Structural snapshots
do not themselves prove the behavioral port fix.

[Token Read Plan](../shared/token-read-plan/README.md) now carries Line 4's
Step 23 implementation unchanged. Its ten tests pass and demo CSV is unchanged.
Line 2's shared renderer also produces the [historical token review](../shared/token-read-plan/observed-review23.html).
This connects Lines 2, 3 and 4 to data Line 1 and other workers can inspect.
The shared worker tools need only standard Python, with no network or packages.

## Coins, records and wall

[COINS.md](COINS.md): **none**. These capabilities require neither a new coin
nor a contract deployment. ZTO first and IMD second cover token-read examples.

This is not the first gathering: painted 01 and 22 exist, with 02–21 reserved.
The four current lines use 23, so this gathering uses 23. All 100 placeholders
and older records remain unchanged. `dist/goals.json` copies the four goals.
The gallery includes all **115 records** once, with **15 embedded previews**,
newest first per wall, and reserved slots separately listed. It is 80,809 bytes
and has no script or remote assets.

The mark is **The Shared Measure**: two pigment bowls passing ochre grains.
The whole PNG is `artifacts/gathering/wall-v3.png`, with identical `wall.png`,
numbered JSON and a 512 × 512 JPEG. [Visual review](VISUAL_REVIEW.md) records
dimensions, hash, digit counts and the generative preservation limitation.
The new PNG and JPEG were visually opened.

No line folder was modified. An inherited `dist/line-4/01.jpg` is 143,560 bytes;
it remains untouched and exceeds today's 100 KB limit. Every newly delivered
file outside artifacts is below 100 KB. No wallet, secret, signing, payment,
transaction submission or posting was used.
