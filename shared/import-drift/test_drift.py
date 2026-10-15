import contextlib
import csv
import io
import json
from html.parser import HTMLParser
from pathlib import Path
import tempfile
import unittest

import drift


class DriftTests(unittest.TestCase):
    def setUp(self):
        scratch = Path.cwd() / 'test' / 'scratch'
        scratch.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'src'
        self.root.mkdir()

    def save(self, name, text):
        path = self.base / name
        path.write_text(text, encoding='utf-8')
        return path

    def test_real_change_and_no_execution(self):
        source = self.root / 'main.py'
        source.write_text('raise RuntimeError("must never execute")\nimport os\n')
        before, _ = drift.snapshot(self.root)
        source.write_text('raise RuntimeError("must never execute")\nimport json\n')
        after, _ = drift.snapshot(self.root)
        result = drift.compare(self.save('a.csv', before), self.save('b.csv', after))
        self.assertEqual(result['summary']['changed'], 1)
        self.assertIn('external_imports', result['changed'][0]['fields'])

    def test_import_line_shifts_equal_and_local_links_present(self):
        (self.root / 'helper.py').write_text('')
        source = self.root / 'main.py'
        source.write_text('import helper\n')
        before, _ = drift.snapshot(self.root)
        source.write_text('\n\nimport helper\nimport helper\n')
        after, _ = drift.snapshot(self.root)
        self.assertEqual(before, after)
        rows = list(csv.DictReader(io.StringIO(after)))
        self.assertEqual(rows[1]['local_imports'], '["helper"]')

    def test_parse_error_retained(self):
        (self.root / 'broken.py').write_text('def (\n')
        text, report = drift.snapshot(self.root)
        self.assertEqual(report['summary']['issue_count'], 1)
        self.assertIn('parse_error', text)

    def test_python_encodings_produce_equal_structural_snapshots(self):
        source = self.root / 'main.py'
        source.write_bytes(b'import json\n')
        expected, _ = drift.snapshot(self.root)
        for raw in (b'\xef\xbb\xbfimport json\n',
                    b'# coding: latin-1\nlabel = "caf\xe9"\nimport json\n'):
            source.write_bytes(raw)
            actual, report = drift.snapshot(self.root)
            self.assertEqual(report['issues'], [])
            self.assertEqual(actual, expected)

    def test_html_handoff_status_and_inert_parse_errors(self):
        source = self.root / 'main.py'
        source.write_text('import csv\n')
        before, _ = drift.snapshot(self.root)
        source.write_text('</pre><script>alert(1)</script>\n')
        after, _ = drift.snapshot(self.root)
        a, b = self.save('a.csv', before), self.save('b.csv', after)
        class Tags(HTMLParser):
            def __init__(self):
                super().__init__()
                self.tags = []
            def handle_starttag(self, tag, attrs):
                self.tags.append(tag)
        for candidate, code in ((a, 0), (b, 1)):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(drift.main(['compare', str(a), str(candidate),
                                             '--format', 'html']), code)
            doc = Tags()
            doc.feed(output.getvalue())
            self.assertNotIn('script', doc.tags)
            self.assertNotIn('img', doc.tags)
            self.assertIn('Content-Security-Policy', output.getvalue())
            self.assertIn('CSV reconciliation:', output.getvalue())
        output, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            self.assertEqual(drift.main(['compare', str(a),
                str(self.save('bad.csv', 'module,x\na,b\n')), '--format', 'html']), 2)
        self.assertEqual(output.getvalue(), '')
        self.assertIn('error', json.loads(errors.getvalue()))

    def test_duplicate_keys_ambiguous(self):
        (self.root / 'main.py').write_text('')
        text, _ = drift.snapshot(self.root)
        duplicated = text + text.splitlines(keepends=True)[1]
        result = drift.compare(self.save('a.csv', text), self.save('b.csv', duplicated))
        self.assertFalse(result['complete'])
        self.assertEqual(result['summary']['ambiguous_keys'], 1)

    def test_schema_and_outside_path_rejected(self):
        wrong = self.save('wrong.csv', 'module,x\na,b\n')
        with self.assertRaises(ValueError):
            drift.compare(wrong, wrong)
        with self.assertRaises(ValueError):
            drift.workspace_path(Path.cwd().parent / 'outside')

    def test_module_package_collision_fails_explicitly(self):
        (self.root / 'pkg').mkdir()
        (self.root / 'pkg.py').write_text('import os\n')
        (self.root / 'pkg' / '__init__.py').write_text('import json\n')
        with self.assertRaisesRegex(ValueError, 'module name collision'):
            drift.snapshot(self.root)

    def test_deep_source_chain_and_cycle_do_not_recurse(self):
        count = 5000
        for index in range(count):
            source = f'import n{index + 1:05}\n' if index + 1 < count else ''
            (self.root / f'n{index:05}.py').write_text(source, encoding='utf-8')
        text, report = drift.snapshot(self.root)
        self.assertEqual(report['summary']['module_count'], count)
        self.assertEqual(report['summary']['local_edge_count'], count - 1)
        self.assertEqual(report['cycles'], [])
        self.assertEqual(len(list(csv.DictReader(io.StringIO(text)))), count)
        (self.root / f'n{count - 1:05}.py').write_text('import n00000\n', encoding='utf-8')
        _, report = drift.snapshot(self.root)
        self.assertEqual(report['summary']['cycle_count'], 1)
        self.assertEqual(len(report['cycles'][0]), count)

    def test_text_comparison_preserves_status_and_explains_real_delta(self):
        source = self.root / 'main.py'
        source.write_text('import csv\n', encoding='utf-8')
        before, _ = drift.snapshot(self.root)
        source.write_text('import json\n', encoding='utf-8')
        after, _ = drift.snapshot(self.root)
        before_path = self.save('before.csv', before)
        after_path = self.save('after.csv', after)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = drift.main(['compare', str(before_path), str(after_path),
                               '--format', 'text'])
        self.assertEqual(code, 1)
        self.assertIn('1 changed', output.getvalue())
        self.assertIn('external_imports:', output.getvalue())
        self.assertIn('csv', output.getvalue())
        self.assertIn('json', output.getvalue())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(drift.main(['compare', str(before_path), str(before_path),
                                         '--format', 'text']), 0)


if __name__ == '__main__':
    unittest.main()
