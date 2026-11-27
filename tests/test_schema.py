"""Contract tests freezing the --json and analysis output schema."""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import unittest

from tarpit_guard.cli import main as cli_main
from tarpit_guard.detector import analyze_file, analyze_text

REPO_ROOT = Path(__file__).resolve().parents[1]

EXPECTED_RESULT_KEYS = {
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

EXPECTED_SIGNAL_KEYS = {
    "opaque_predicate_density",
    "decoder_loops",
    "hex_identifier_array",
    "obfuscator_control_tricks",
    "decoy_vocabulary_density",
    "garbled_identifier_ratio",
}

EXPECTED_EVIDENCE_KEYS = {
    "size_bytes",
    "line_count",
    "math_imul_count",
    "hex_identifiers",
    "hex_escapes",
    "truthy_tricks",
    "decoder_pairs",
    "decoy_vocab_hits",
    "unique_identifiers",
    "garbled_identifiers",
    "short_identifier_ratio",
    "identifier_entropy",
}

EXPECTED_CLI_REPORT_KEYS = {
    "scanned",
    "flagged",
    "tool_fingerprints",
    "results",
}


class OutputSchemaContractTest(unittest.TestCase):
    def _assert_result_schema(self, result: dict) -> None:
        self.assertEqual(set(result.keys()), EXPECTED_RESULT_KEYS)
        self.assertIsInstance(result["score"], (int, float))
        self.assertIsInstance(result["confidence"], (int, float))
        self.assertIsInstance(result["hardened"], bool)
        self.assertIsInstance(result["markers"], list)
        for marker in result["markers"]:
            self.assertEqual(set(marker.keys()), {"signal", "why"})
            self.assertIsInstance(marker["signal"], str)
            self.assertIsInstance(marker["why"], str)
        self.assertEqual(set(result["signals"].keys()), EXPECTED_SIGNAL_KEYS)
        for val in result["signals"].values():
            self.assertIsInstance(val, (int, float))
            self.assertGreaterEqual(val, 0.0)
            self.assertLessEqual(val, 1.0)
        self.assertIsInstance(result["fired_signals"], list)
        self.assertTrue(all(isinstance(s, str) for s in result["fired_signals"]))
        self.assertIsInstance(result["benign_minification"], bool)
        self.assertEqual(set(result["evidence"].keys()), EXPECTED_EVIDENCE_KEYS)
        self.assertIsInstance(result["recommended_strategy"], str)

    def test_analyze_text_schema_keys(self) -> None:
        result = analyze_text("function add(a, b) { return a + b; }\n", path="snippet.js")
        self._assert_result_schema(result)
        self.assertEqual(result["path"], "snippet.js")

    def test_analyze_file_schema_across_corpus_buckets(self) -> None:
        samples = [
            REPO_ROOT / "corpus" / "clean" / "tiny_app.js",
            REPO_ROOT / "corpus" / "minified" / "jquery.min.js",
            REPO_ROOT / "corpus" / "obfuscated" / "bla_hardened_app.js",
        ]
        for sample in samples:
            result = analyze_file(str(sample))
            self._assert_result_schema(result)

    def test_cli_json_output_schema_keys(self) -> None:
        target = REPO_ROOT / "corpus" / "obfuscated" / "bla_hardened_app.js"
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = cli_main([str(target), "--json"])
        self.assertEqual(exit_code, 0)
        report = json.loads(stdout.getvalue())
        self.assertEqual(set(report.keys()), EXPECTED_CLI_REPORT_KEYS)
        self.assertEqual(report["scanned"], 1)
        self.assertEqual(report["flagged"], 1)
        self.assertIsInstance(report["tool_fingerprints"], list)
        self.assertEqual(len(report["results"]), 1)
        self._assert_result_schema(report["results"][0])


if __name__ == "__main__":
    unittest.main()
