"""Behavioral checks for offline HTML rendering; transient fixtures in test/scratch."""
import contextlib
import csv
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import tempfile
import unittest

import review


class Document(HTMLParser):
    def __init__(self, content):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.attrs = []
        self.pres = []
        self.current = None
        self.feed(content)

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        self.attrs.extend(attrs)
        if tag == 'pre':
            self.current = ''

    def handle_data(self, value):
        if self.current is not None:
            self.current += value

    def handle_endtag(self, tag):
        if tag == 'pre':
            self.pres.append(json.loads(self.current))
            self.current = None


class ReviewTests(unittest.TestCase):
    def setUp(self):
        scratch = Path.cwd() / 'test/scratch'
        scratch.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.before, self.after = (Path(self.temp.name) / name for name in ('before.csv', 'after.csv'))

    def write(self, path, rows):
        with path.open('w', encoding='utf-8', newline='') as stream:
            csv.writer(stream).writerows(rows)

    def render(self, before, after, ignore=()):
        self.write(self.before, before)
        self.write(self.after, after)
        result = review.engine.reconcile(self.before, self.after, ['id'], ignore)
        content = '\n'.join(review.iter_html(result))
        return result, content, Document(content)

    def test_hostile_fields_remain_exact_inert_text(self):
        payload = '</pre><script>alert(1)</script><img src="https://example.org" onerror="x"> & \u202e\n\t'
        result, content, doc = self.render([['id', payload], ['x', 'old']], [['id', payload], ['x', payload]])
        self.assertEqual(result['summary']['changed'], 1)
        self.assertIn(payload, doc.pres)
        self.assertNotIn('script', doc.tags)
        self.assertNotIn('img', doc.tags)
        self.assertFalse(any(k in ('src', 'href', 'onerror', 'onclick') for k, _ in doc.attrs))
        self.assertIn('Content-Security-Policy', content)
        self.assertNotIn('\u202e', content)

    def test_duplicates_show_all_occurrences_and_ignored_values(self):
        result, content, doc = self.render([['id', 'v', 'private'], ['x', 'one', 'first'], ['x', 'two', 'second']],
                                          [['id', 'v', 'private'], ['x', 'three', 'third']], ['private'])
        self.assertFalse(result['complete'])
        self.assertIn('Incomplete comparison', content)
        self.assertIn('not redaction', content)
        self.assertIn({'id': 'x', 'v': 'one', 'private': 'first'}, doc.pres)
        self.assertIn({'id': 'x', 'v': 'two', 'private': 'second'}, doc.pres)
        self.assertIn({'id': 'x', 'v': 'three', 'private': 'third'}, doc.pres)
        self.assertIn('details', doc.tags)

    def test_add_remove_schema_and_exact_whitespace(self):
        result, content, doc = self.render([['id', 'v', 'old'], ['gone', 'a', 'b'], ['same', '01', 'c']],
                                          [['id', 'v', 'new'], ['added', ' a\n', 'z'], ['same', '1', 'd']])
        self.assertIn({'id': 'added', 'v': ' a\n', 'new': 'z'}, doc.pres)
        self.assertIn({'id': 'gone', 'v': 'a', 'old': 'b'}, doc.pres)
        self.assertIn('01', doc.pres)
        self.assertIn('1', doc.pres)
        self.assertIn(['old'], doc.pres)
        self.assertIn(['new'], doc.pres)
        self.assertIn('common, nonignored', content)

    def test_equal_reordered_records(self):
        result, content, _ = self.render([['id', 'v'], ['a', '1'], ['b', '2']], [['v', 'id'], ['2', 'b'], ['1', 'a']])
        self.assertTrue(result['equal'])
        self.assertIn('CSV reconciliation: Equal', content)

    def test_cli_statuses_and_no_partial_html_on_input_error(self):
        self.write(self.before, [['id', 'v'], ['x', '1']])
        for rows, expected in [([['id', 'v'], ['x', '1']], 0),
                               ([['id', 'v'], ['x', '2']], 1),
                               ([['id', 'v'], ['x']], 2)]:
            self.write(self.after, rows)
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = review.main([str(self.before), str(self.after), '--key', 'id'])
            self.assertEqual(code, expected)
            if expected == 2:
                self.assertEqual(out.getvalue(), '')
                self.assertIn('error', json.loads(err.getvalue()))
            else:
                self.assertIn('<!doctype html>', out.getvalue())
                self.assertEqual(err.getvalue(), '')

    def test_outside_workspace_rejected(self):
        self.write(self.before, [['id']])
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = review.main([str(self.before), str(Path.cwd().parent / 'not-read.csv'), '--key', 'id'])
        self.assertEqual(code, 2)
        self.assertEqual(out.getvalue(), '')
        self.assertIn('inside the current working directory', err.getvalue())


if __name__ == '__main__':
    unittest.main()
