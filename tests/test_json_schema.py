import json
import os
import subprocess
import sys
import unittest

from tarpit_guard.detector import analyze_file, analyze_text

REQUIRED_RESULT_KEYS = {
    "path",
    "score",
    "confidence",
    "hardened",
    "markers",
    "signals",
    "fired_signals",
    "benign_minification",
    "evidence",
    "recommended_strategy",
}

REQUIRED_REPORT_KEYS = {
    "scanned",
    "flagged",
    "tool_fingerprints",
    "results",
}

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestJsonSchema(unittest.TestCase):
    def test_analyze_text_has_frozen_keys(self):
        result = analyze_text("function add(a, b) { return a + b; }\n", path="sample.js")
        self.assertTrue(REQUIRED_RESULT_KEYS.issubset(result.keys()))

    def test_analyze_file_has_frozen_keys(self):
        sample = os.path.join(REPO_ROOT, "corpus", "clean", "sample_src.js")
        result = analyze_file(sample)
        self.assertTrue(REQUIRED_RESULT_KEYS.issubset(result.keys()))

    def test_cli_json_output_has_frozen_keys(self):
        sample = os.path.join(REPO_ROOT, "corpus", "clean", "sample_src.js")
        proc = subprocess.run(
            [sys.executable, "-m", "tarpit_guard.cli", sample, "--json"],
            capture_output=True,
            text=True,
            check=True,
        )
        report = json.loads(proc.stdout)
        self.assertTrue(REQUIRED_REPORT_KEYS.issubset(report.keys()))
        self.assertEqual(len(report["results"]), 1)
        self.assertTrue(REQUIRED_RESULT_KEYS.issubset(report["results"][0].keys()))


if __name__ == "__main__":
    unittest.main()
