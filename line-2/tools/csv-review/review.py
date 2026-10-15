#!/usr/bin/env python3
"""Render an exact keyed CSV comparison as a self-contained offline HTML review."""
import argparse
import html
import importlib.util
import json
from pathlib import Path
import sys

# Reuse the established comparison contract; never import or execute CSV contents.
ENGINE_PATH = Path(__file__).resolve().parents[1] / 'csv-reconcile' / 'reconcile.py'
spec = importlib.util.spec_from_file_location('csv_review_engine', ENGINE_PATH)
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)


def text(value):
    return html.escape(str(value), quote=True)


def exact(value):
    # JSON notation exposes whitespace, newlines, controls and exact string types.
    return '<pre>' + text(json.dumps(value, ensure_ascii=True, sort_keys=True)) + '</pre>'


def table(headers, rows):
    yield '<table><thead><tr>' + ''.join('<th scope="col">' + text(h) + '</th>' for h in headers) + '</tr></thead><tbody>'
    found = False
    for row in rows:
        found = True
        yield '<tr>' + ''.join('<td>' + exact(cell) + '</td>' for cell in row) + '</tr>'
    yield '</tbody></table>'
    if not found:
        yield '<p>None.</p>'


def iter_html(result):
    """Yield HTML chunks. All data is text, never HTML, script, CSS or URLs."""
    state = 'Equal' if result['equal'] else 'Different'
    yield '''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>CSV reconciliation review</title>
<style>
body{font:16px system-ui,sans-serif;line-height:1.5;margin:2rem;max-width:100rem;color:#242018;background:#faf7f0}
h1,h2,h3{line-height:1.2}table{border-collapse:collapse;width:100%;margin:1rem 0;display:block;overflow:auto}
th,td{border:1px solid #b8afa0;padding:.5rem;text-align:left;vertical-align:top}th{background:#e8e0d0}
pre{white-space:pre-wrap;overflow-wrap:anywhere;margin:0;font-size:.85rem}summary{cursor:pointer;font-weight:bold}
.notice{border-left:5px solid #8a451c;padding:1rem;background:#eee4d4}details{margin:1rem 0}
</style></head><body>'''
    yield '<h1>CSV reconciliation: ' + state + '</h1>'
    yield '<p>Exact strings, stable keys, no automatic normalization or duplicate pairing. Entire comparison shown; nothing truncated.</p>'
    yield '<h2>Comparison settings</h2>'
    yield from table(('Setting', 'Value'), (('Key columns', result['keys']), ('Ignored columns', result['ignored_columns'])))
    if not result['complete']:
        yield '<p class="notice">Incomplete comparison: duplicate keys remain ambiguous. Resolve these groups before treating this as a complete reconciliation.</p>'
    if result['ignored_columns']:
        yield '<p class="notice">Ignore is a comparison option, not redaction. Ambiguous groups below retain every original column, including ignored values.</p>'
    yield '<h2>Counts</h2>'
    yield from table(('Measure', 'Count'), result['summary'].items())
    yield '<h2>Schema changes</h2>'
    yield from table(('Change', 'Columns'), result['schema'].items())
    yield '<p>Unchanged counts compare only common, nonignored columns. A schema change still makes the datasets different.</p>'
    for title, category in (('Added rows', 'added'), ('Removed rows', 'removed')):
        yield '<h2>' + title + '</h2>'
        yield from table(('Key', 'Source record', 'Values'),
                         ((r['key'], r['record'], r['values']) for r in result[category]))
    yield '<h2>Changed fields</h2>'
    yield from table(('Key', 'Before record', 'After record', 'Column', 'Before', 'After'),
                     ((r['key'], r['before_record'], r['after_record'], column, change['before'], change['after'])
                      for r in result['changed'] for column, change in r['fields'].items()))
    yield '<h2>Ambiguous keys</h2>'
    if not result['ambiguous']:
        yield '<p>None.</p>'
    for group in result['ambiguous']:
        yield '<details open><summary>Unresolved key</summary>' + exact(group['key'])
        yield '<p>No automatic pairing. Every original occurrence is listed.</p>'
        for side in ('before', 'after'):
            yield '<h3>' + side.capitalize() + '</h3>'
            yield from table(('Source record', 'Original values'),
                             ((r['record'], r['values']) for r in group[side]))
        yield '</details>'
    yield '<h2>Reading this report</h2><p>Values use JSON notation: quotes identify strings, \\n marks an embedded newline, and Unicode escapes preserve exact characters. Record numbers count CSV records (header is 1), not physical lines. Row order has no effect on equality. Original unchanged row values are not repeated. This document makes no network requests and contains no scripts.</p></body></html>'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('before', help='baseline CSV inside current directory')
    parser.add_argument('after', help='candidate CSV inside current directory')
    parser.add_argument('--key', required=True, action='append', help='stable key column; repeat for composite keys')
    parser.add_argument('--ignore', action='append', default=[], help='non-key comparison exclusion, not redaction')
    args = parser.parse_args(argv)
    try:
        result = engine.reconcile(args.before, args.after, args.key, args.ignore)
    except (OSError, ValueError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=True), file=sys.stderr)
        return 2
    try:
        for chunk in iter_html(result):
            print(chunk)
    except BrokenPipeError:
        return 2
    return 0 if result['equal'] else 1


if __name__ == '__main__':
    sys.exit(main())
