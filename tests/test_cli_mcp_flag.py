"""Tests for the CLI's argument handling around --mcp."""

import contextlib
import io
import unittest

from tarpit_guard.cli import main


class TestPathRequired(unittest.TestCase):
    def test_missing_path_without_mcp_is_a_usage_error(self):
        with contextlib.redirect_stderr(io.StringIO()) as err:
            with self.assertRaises(SystemExit) as ctx:
                main([])
        self.assertEqual(ctx.exception.code, 2)
        self.assertIn("path", err.getvalue())


if __name__ == "__main__":
    unittest.main()
