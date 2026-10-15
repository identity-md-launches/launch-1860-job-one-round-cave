# CSV Review

Generate a self-contained HTML review of two keyed CSV datasets, suitable for opening offline in a browser or handing to another worker. It shows counts, comparison settings, schema changes, added and removed records, every changed field side by side, and every occurrence of unresolved duplicate keys. No JavaScript, remote resources, network calls, accounts or installation.

Python 3.9+; standard library only. Run from the workspace root. Keep the sibling `../csv-reconcile/reconcile.py` with this folder: CSV Review imports that existing engine rather than maintaining a second comparison algorithm. It reads only the explicitly supplied, workspace-contained CSV inputs and prints HTML to stdout. It does not open a browser or write input files. No signing, transaction submission, wallet, secret or environment access.

## One command to see it working

```sh
python3 -B line-2/tools/csv-review/review.py line-2/tools/csv-reconcile/demo-before.csv line-2/tools/csv-reconcile/demo-after.csv --key item --key location > line-2/tools/csv-review/demo.html
```

Then open `demo.html` in a browser. A generated copy is already included. **Exit 1 is expected**: the synthetic inventory has one added row, one removed row, one changed quantity (`lamp`: `1` to `2`), one unchanged row and no ambiguous keys. These were the results when tried locally. Repeat `--key` for a composite key and `--ignore` for a non-key comparison exclusion.

Exit statuses follow CSV Reconcile: **0** equal; **1** differences or ambiguity; **2** invalid input or I/O error. Invalid CSV produces JSON on stderr and no partial HTML on stdout. Shell redirection opens its destination before Python validates inputs: choose a separate output path and never redirect over either input. A missing sibling engine is an installation error.

## Review contract and limits

- The engine's exact string, UTF-8/BOM, composite key, schema, ignore, path containment, 16 MiB/input and 100,000-record/input rules apply unchanged; see [its README](../csv-reconcile/README.md).
- All untrusted values, keys and column names are HTML escaped. A restrictive Content Security Policy blocks scripts, forms and remote resources. Data never becomes markup or URLs. This is a static document, not a filter/search application.
- Values use JSON notation inside table cells. Quotes and escapes make strings, whitespace, newlines, control characters and Unicode code points explicit. For example `"01"` differs from `"1"`. Unicode is escaped for exact inspection; it is not normalized.
- Ambiguous keys remain unresolved. Every source occurrence, including ignored columns, is shown. **Ignore is not redaction.** Review the report's contents before sharing it.
- Unchanged rows are counted on common, nonignored columns, not repeated in full. Added/removed schema columns are listed separately; the engine does not classify their values as common-field changes. All reported differences are shown without truncation.
- The engine holds both inputs and its result in memory. HTML is emitted incrementally, but a large input, many fields or duplicate groups can produce a very large report and stress a browser. There is no output-size limit. The committed examples are small.
- Reports are comparison artifacts, not state proofs, current balances, approvals or automatic data repair.

## Checks and real-data trial

```sh
python3 -B -m unittest discover -s line-2/tools/csv-review -v
```

Six tests passed: hostile HTML/attributes/control characters remain inert and round-trip exactly; duplicate occurrences and ignored values remain visible; schema/addition/removal/whitespace changes are retained; reordering compares equal; CLI statuses and error output are correct; outside-workspace paths are rejected. Fixtures are transient under `test/scratch/`. The unchanged engine's 17 tests also passed in a scratch copy.

A real-data trial compared the repository's historical `shared/token-read-plan/observed.csv` against its six rows reversed. Result: exit 0, six unchanged records. [observed-review.html](observed-review.html) is that generated report. Its composite key was `chain_id`, `token_address`, `field`. Source provenance is `shared/token-read-plan/observed-provenance.json`: Ethereum RPC observations at block **26,198,502**, ZTO first and IMD second, not current observations. No fresh chain request or transaction was needed for this offline review. This tool does not need a coin or payment.
