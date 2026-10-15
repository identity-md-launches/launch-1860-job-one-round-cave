"""Input-boundary regressions: mock file bytes, never open outside the workspace."""
import contextlib
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import abi_workbench as abi


class InputValidationTests(unittest.TestCase):
    def load_bytes(self, raw, name='symbol'):
        with patch.object(Path, 'open', return_value=io.BytesIO(raw)):
            return abi.load_function('test/scratch/input.json', name)

    def test_container_and_entry_errors(self):
        for value in [{'bad': True}, None, 1, 'ABI', [None], ['function'],
                      [{'type': []}], [{'type': 'function'}],
                      [{'type': 'function', 'name': 123}],
                      [{'type': 'function', 'name': 'bad(name'}]]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.load_bytes(json.dumps(value).encode())

    def test_parameter_shapes(self):
        for field in ['inputs', 'outputs']:
            for params in [None, {}, 'bad', [None], [{}], [{'type': []}],
                           [{'type': ''}], [{'type': 'uint', 'name': 2}]]:
                with self.subTest(field=field, params=params), self.assertRaises(ValueError):
                    self.load_bytes(json.dumps([
                        {'type': 'function', 'name': 'symbol', field: params}
                    ]).encode())

    def test_selected_outputs_are_checked_even_when_encoding(self):
        with self.assertRaisesRegex(ValueError, 'unsupported ABI type'):
            self.load_bytes(b'[{"type":"function","name":"symbol","outputs":[{"type":"uint7"}]}]')

    def test_unrelated_supported_abi_entry_shapes(self):
        # Unsupported composite types on an unrelated function need not block symbol().
        entries = [{'type': 'event', 'name': 'Transfer', 'inputs': []},
                   {'type': 'constructor', 'inputs': []}, {'type': 'receive'},
                   {'type': 'fallback'}, {'type': 'error', 'name': 'Denied'},
                   {'type': 'function', 'name': 'other', 'inputs': [{'type': 'tuple[]'}]},
                   {'type': 'function', 'name': 'symbol', 'outputs': [{'type': 'string'}]}]
        fn, sig = self.load_bytes(json.dumps(entries).encode())
        self.assertEqual(sig, 'symbol()')
        self.assertEqual(fn['outputs'][0]['type'], 'string')

    def test_missing_and_overloaded_functions(self):
        with self.assertRaisesRegex(ValueError, 'found 0'):
            self.load_bytes(b'[]')
        with self.assertRaisesRegex(ValueError, 'found 2'):
            self.load_bytes(b'[{"type":"function","name":"symbol"},{"type":"function","name":"symbol"}]')

    def test_bad_json_encoding_duplicates_and_depth(self):
        for raw in [b'\xff', b'[', b'[{"type":"function","name":"symbol","name":"other"}]',
                    b'[' * 2000 + b']' * 2000]:
            with self.subTest(raw=raw[:30]), self.assertRaises(ValueError):
                self.load_bytes(raw)

    def test_bom_and_input_budget(self):
        self.assertEqual(self.load_bytes(b'\xef\xbb\xbf[{"type":"function","name":"symbol"}]')[1], 'symbol()')
        with self.assertRaisesRegex(ValueError, '1 MiB'):
            self.load_bytes(b' ' * (abi.MAX_ABI_BYTES + 1))

    def test_outside_workspace_rejected_before_open(self):
        # The path is never opened; no outside file is read or created.
        with patch.object(Path, 'open') as opened:
            with self.assertRaisesRegex(ValueError, 'inside the current workspace'):
                abi.load_function(Path.cwd().parent / 'outside.json', 'symbol')
            opened.assert_not_called()

    def test_cli_concise_errors(self):
        for failure in [FileNotFoundError('missing ABI'), PermissionError('unreadable ABI'),
                        IsADirectoryError('ABI is a directory')]:
            err, out = io.StringIO(), io.StringIO()
            with patch.object(Path, 'open', side_effect=failure), \
                 patch('sys.argv', ['abi_workbench', 'encode', '--abi', 'missing.json',
                                    '--function', 'symbol', '--args', '[]']), \
                 contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
                self.assertEqual(abi.main(), 2)
            self.assertTrue(err.getvalue().startswith('error: '))
            self.assertNotIn('Traceback', err.getvalue())
            self.assertEqual(out.getvalue(), '')

    def test_cli_malformed_abi_is_error_two(self):
        err = io.StringIO()
        with patch.object(Path, 'open', return_value=io.BytesIO(b'{"bad":true}')), \
             patch('sys.argv', ['abi_workbench', 'decode', '--abi', 'bad.json',
                                '--function', 'symbol', '--data', '0x']), \
             contextlib.redirect_stderr(err):
            self.assertEqual(abi.main(), 2)
        self.assertEqual(err.getvalue(), 'error: ABI must be a JSON array of entry objects\n')

    def test_direct_parameter_validation(self):
        for param in [None, [], 'uint', {'type': 2}, {'type': None}]:
            with self.subTest(param=param), self.assertRaises(ValueError):
                abi.canonical(param)


if __name__ == '__main__':
    unittest.main()
