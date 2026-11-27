# JSON Output Schema

`tarpit-guard --json` emits a JSON report to stdout, and `analyze_file` / `analyze_text` (as well as the MCP `check_file` / `check_source` tools) return per-file analysis objects with a stable top-level structure.

## Top-level CLI `--json` report

| Field | Type | Description |
|---|---|---|
| `scanned` | `integer` | Total number of files analyzed. |
| `flagged` | `integer` | Number of files with `hardened == true` at the active threshold. |
| `tool_fingerprints` | `array<object>` | Hardening tool artifacts found in directory scans (`tool`, `kind`, `path`). |
| `results` | `array<object>` | Per-file analysis objects sorted by `score` descending. |

## Per-file analysis object

| Field | Type | Description |
|---|---|---|
| `path` | `string` | File path (or label passed to `check_source` / `analyze_text`). |
| `score` | `number` | Weighted tarpit score from `0.0` to `100.0`. |
| `confidence` | `number` | Confidence score from `0.0` to `1.0` derived from fired signals and markers. |
| `hardened` | `boolean` | `true` when `score >= threshold` (default `55`). |
| `markers` | `array<object>` | Categorical hardening markers triggered (`signal`, `why`). |
| `signals` | `object` | Normalized `[0.0, 1.0]` values for each detector signal. |
| `fired_signals` | `array<string>` | Names of signals whose normalized value reached `>= 0.5`. |
| `benign_minification` | `boolean` | `true` when short-identifier dominance indicates ordinary minification with no hostile markers. |
| `evidence` | `object` | Raw structural counts and metrics backing the score. |
| `recommended_strategy` | `string` | Actionable guidance for an agent or reviewer. |

### `evidence` fields

| Field | Type | Description |
|---|---|---|
| `size_bytes` | `integer` | UTF-8 byte length of the analyzed source. |
| `line_count` | `integer` | Number of lines in the source. |
| `math_imul_count` | `integer` | Count of `Math.imul` calls. |
| `hex_identifiers` | `integer` | Count of `_0x...` hex-style identifiers. |
| `hex_escapes` | `integer` | Count of `\xNN` / `\uNNNN` escapes. |
| `truthy_tricks` | `integer` | Count of `!![]` self-defending / control-flow tricks. |
| `decoder_pairs` | `integer` | Count of `fromCharCode` / `charCodeAt` decoder loops. |
| `decoy_vocab_hits` | `integer` | Occurrences of decoy hardening jargon terms. |
| `unique_identifiers` | `integer` | Count of distinct identifiers. |
| `garbled_identifiers` | `integer` | Count of high-entropy / mangled identifiers. |
| `short_identifier_ratio` | `number` | Ratio of 1–2 character identifiers (minification indicator). |
| `identifier_entropy` | `number` | Shannon entropy of sorted unique identifiers. |
