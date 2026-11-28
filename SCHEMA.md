# Output Schema

This document defines the stable JSON output contract for `tarpit-guard` across the CLI (`--json`), Python API (`analyze_text`, `analyze_file`), and MCP tools (`check_file`, `check_source`, `scan_repo`).

Automated schema contract tests in `tests/test_schema.py` guard these keys so consumers (such as AI agents) do not break silently on future changes.

---

## 1. File Analysis Result Object

Returned directly by:
- Python API: `analyze_text(text, path=None)` and `analyze_file(path)`
- MCP tools: `check_file(path)` and `check_source(text, label)`
- Array elements of `results` (CLI `--json`) and `flagged_files` / `all_results` (MCP `scan_repo`)

### Top-level fields

| Field | Type | Description |
| :--- | :--- | :--- |
| `path` | `string \| null` | File path or snippet label (`null` when omitted in `analyze_text`). |
| `score` | `number` | Weighted obfuscation/tarpit score from `0.0` to `100.0` (rounded to 1 decimal place). |
| `confidence` | `number` | Confidence score from `0.0` to `1.0` (rounded to 2 decimal places), derived from the number of categorical markers and fired signals. |
| `hardened` | `boolean` | Verdict flag: `true` when `score >= threshold` (default threshold: `55.0`). |
| `markers` | `array<object>` | Categorical signatures that apply a decisive score floor. Each element has `{"signal": string, "why": string}`. |
| `signals` | `object` | Map of normalized `[0.0, 1.0]` signal values (rounded to 3 decimal places). |
| `fired_signals` | `array<string>` | Names of signals whose normalized value is `>= 0.5`. |
| `benign_minification` | `boolean` | `true` when the file matches the ordinary minification profile (high 1–2 char identifier ratio, >300 identifiers) with zero categorical markers. |
| `evidence` | `object` | Raw counts and structural metrics explaining why the file scored as it did. |
| `recommended_strategy` | `string` | Actionable guidance for an agent or human reviewer based on the verdict. |

### `markers[]` item fields

| Field | Type | Description |
| :--- | :--- | :--- |
| `signal` | `string` | Signal key that triggered the categorical floor. |
| `why` | `string` | Human-readable explanation of the detected signature. |

### `signals` fields

| Key | Type | Range |
| :--- | :--- | :--- |
| `opaque_predicate_density` | `number` | `0.0` – `1.0` |
| `decoder_loops` | `number` | `0.0` – `1.0` |
| `hex_identifier_array` | `number` | `0.0` – `1.0` |
| `obfuscator_control_tricks` | `number` | `0.0` – `1.0` |
| `decoy_vocabulary_density` | `number` | `0.0` – `1.0` |
| `garbled_identifier_ratio` | `number` | `0.0` – `1.0` |

### `evidence` fields

| Key | Type | Description |
| :--- | :--- | :--- |
| `size_bytes` | `integer` | Character length of the analyzed source text. |
| `line_count` | `integer` | Number of lines (`>= 1`). |
| `math_imul_count` | `integer` | Occurrences of `Math.imul`. |
| `hex_identifiers` | `integer` | Matches of `_0x[0-9a-fA-F]{3,}`. |
| `hex_escapes` | `integer` | Matches of `\x[0-9a-fA-F]{2}`. |
| `truthy_tricks` | `integer` | Matches of `![]`. |
| `decoder_pairs` | `integer` | `min(count(fromCharCode), count(charCodeAt))`. |
| `decoy_vocab_hits` | `integer` | Total case-insensitive matches of decoy security jargon words. |
| `unique_identifiers` | `integer` | Count of distinct identifier tokens. |
| `garbled_identifiers` | `integer` | Count of distinct mangled mixed-case identifiers ending with digits. |
| `short_identifier_ratio` | `number` | Fraction of identifier occurrences with length `<= 2` (rounded to 3 decimals). |
| `identifier_entropy` | `number` | Shannon entropy over sorted unique identifiers (rounded to 3 decimals). |

### Error response (`analyze_file` / `check_file`)

When a file cannot be read (`OSError` or `UnicodeError`), `analyze_file` returns:

```json
{
  "path": "path/to/missing.js",
  "error": "..."
}
```

---

## 2. CLI `--json` Report Envelope

Emitted to stdout by `tarpit-guard <path> --json`:

| Field | Type | Description |
| :--- | :--- | :--- |
| `scanned` | `integer` | Total number of files successfully analyzed. |
| `flagged` | `integer` | Number of files with `hardened == true`. |
| `tool_fingerprints` | `array<object>` | Standalone hardener artifacts found in directory scans (empty for single-file scans). |
| `results` | `array<object>` | File analysis result objects sorted by `score` descending. |

### `tool_fingerprints[]` item fields

| Field | Type | Description |
| :--- | :--- | :--- |
| `kind` | `string` | `"dir"` or `"file"`. |
| `name` | `string` | Matched artifact filename or directory name. |
| `tool` | `string` | Identified hardener name (for example `"bla"`). |
| `path` | `string` | Path to the matched artifact. |

---

## 3. MCP `scan_repo` Report Envelope

Returned by the MCP `scan_repo(root, threshold)` tool:

| Field | Type | Description |
| :--- | :--- | :--- |
| `root` | `string` | Scanned root directory path. |
| `scanned` | `integer` | Total number of files successfully analyzed. |
| `flagged` | `integer` | Number of files with `hardened == true`. |
| `tool_fingerprints` | `array<object>` | Standalone hardener artifacts discovered under `root`. |
| `flagged_files` | `array<object>` | Subset of `all_results` where `hardened == true`. |
| `all_results` | `array<object>` | All file analysis result objects sorted by `score` descending. |

If `root` is not a directory, `scan_repo` returns `{"error": "not a directory: <root>"}`.

---

## Example CLI `--json` Output

```json
{
  "scanned": 1,
  "flagged": 0,
  "tool_fingerprints": [],
  "results": [
    {
      "path": "corpus/clean/tiny_app.js",
      "score": 0.0,
      "confidence": 0.0,
      "hardened": false,
      "markers": [],
      "signals": {
        "opaque_predicate_density": 0.0,
        "decoder_loops": 0.0,
        "hex_identifier_array": 0.0,
        "obfuscator_control_tricks": 0.0,
        "decoy_vocabulary_density": 0.0,
        "garbled_identifier_ratio": 0.0
      },
      "fired_signals": [],
      "benign_minification": false,
      "evidence": {
        "size_bytes": 120,
        "line_count": 5,
        "math_imul_count": 0,
        "hex_identifiers": 0,
        "hex_escapes": 0,
        "truthy_tricks": 0,
        "decoder_pairs": 0,
        "decoy_vocab_hits": 0,
        "unique_identifiers": 10,
        "garbled_identifiers": 0,
        "short_identifier_ratio": 0.1,
        "identifier_entropy": 3.85
      },
      "recommended_strategy": "Looks like ordinary source. Normal analysis is fine."
    }
  ]
}
```
