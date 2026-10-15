"""Offline real-process tests. No network, disk fixtures or timing-scale sleeps."""
import contextlib
import io
import json
import subprocess
import sys
import time
import unittest

import deadline_sentry as watchdog


class WatchdogTests(unittest.TestCase):
    def worker(self, source, budget=2):
        return watchdog.supervise([sys.executable, '-I', '-B', '-c', source], budget)

    def test_success(self):
        report, code = self.worker('print(\'{"ok":true,"hops":[]}\')')
        self.assertEqual(code, 0)
        self.assertTrue(report['probe']['ok'])

    def test_failed_probe(self):
        report, code = self.worker('print(\'{"ok":false}\'); raise SystemExit(1)')
        self.assertEqual(code, 1)
        self.assertFalse(report['ok'])

    def test_stalled_worker_killed_and_reaped(self):
        # Simulates an uninterruptible-by-socket-timeout DNS/header call.
        start = time.monotonic()
        report, code = self.worker('import time; time.sleep(30)', .15)
        self.assertEqual(code, 1)
        self.assertEqual(report['error']['kind'], 'deadline')
        self.assertIsInstance(report['worker_returncode'], int)
        self.assertLess(time.monotonic() - start, 2)

    def test_partial_output_is_not_success(self):
        report, code = self.worker('import time; print(\'{"ok":true}\', flush=True); time.sleep(30)', .15)
        self.assertEqual(code, 1)
        self.assertTrue(report['partial_report_discarded'])
        self.assertNotIn('probe', report)

    def test_large_pipe_does_not_deadlock(self):
        report, code = self.worker('print(\'{"ok":true,"data":"\' + "a"*200000 + \'"}\')')
        self.assertEqual(code, 0)
        self.assertEqual(len(report['probe']['data']), 200000)

    def test_bad_protocol(self):
        for source in ['print("invalid")', 'print("[]")',
                       'print(\'{"ok":true}\'); raise SystemExit(1)',
                       'raise SystemExit(3)']:
            report, code = self.worker(source)
            self.assertEqual(code, 1)
            self.assertEqual(report['error']['kind'], 'worker_protocol')

    def test_argument_error(self):
        report, code = self.worker('import sys; print("bad URL",file=sys.stderr); raise SystemExit(2)')
        self.assertEqual(code, 2)
        self.assertEqual(report['error']['kind'], 'arguments')

    def test_no_shell(self):
        report, code = watchdog.supervise(['/no/such/program'], 1)
        self.assertEqual(code, 1)
        self.assertEqual(report['error']['kind'], 'worker_start')

    def test_invalid_deadlines(self):
        for value in ['nan', 'inf', '0', '-1', '121']:
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as e:
                watchdog.main(['--deadline', value, 'https://api.imd.fun'])
            self.assertEqual(e.exception.code, 2)

    def test_real_cli_validation_without_network(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = watchdog.main(['--deadline', '2', 'http://invalid.example'])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(output.getvalue())['error']['kind'], 'arguments')

    def test_real_cli_rejects_zero_port(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = watchdog.main(['--deadline', '2', 'https://example.com:0/'])
        report = json.loads(output.getvalue())
        self.assertEqual(code, 2)
        self.assertFalse(report['ok'])
        self.assertEqual(report['error']['kind'], 'arguments')
        self.assertIn('invalid port', report['error']['message'])
        self.assertNotIn('probe', report)


if __name__ == '__main__':
    unittest.main()
