"""CLI --version flag."""

from __future__ import annotations

import contextlib
import io
import unittest

from tarpit_guard import __version__
from tarpit_guard.cli import main as cli_main


class VersionFlagTest(unittest.TestCase):
    def test_version_prints_and_exits_zero(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit) as ctx:
            cli_main(["--version"])
        self.assertEqual(ctx.exception.code, 0)
        self.assertEqual(out.getvalue().strip(), f"tarpit-guard {__version__}")


if __name__ == "__main__":
    unittest.main()
