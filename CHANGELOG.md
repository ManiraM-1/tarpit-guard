# Changelog

All notable changes to this project are listed here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.2.1] - 2026-11-28

### Added
- `tarpit-guard-mcp` command to start the MCP server, plus a ready-to-paste
  MCP client config in the README.
- `SCHEMA.md`, documenting the `--json` output, and contract tests that keep it
  stable ([#6](https://github.com/ManiraM-1/tarpit-guard/pull/6)).
- CI that runs the corpus evaluation, a CLI smoke test, and the unit tests on
  Python 3.9 to 3.13, and checks that the package builds
  ([#9](https://github.com/ManiraM-1/tarpit-guard/pull/9)).
- Contributor guide, issue templates, code of conduct, security policy, pull
  request template, and this changelog.

### Changed
- A tarpit verdict now tells the agent to stop and skip the file (or flag it
  for a human) instead of suggesting sandboxed dynamic analysis. The README
  and the MCP tool description say the same. The `--json` shape is unchanged.

## [0.2.0] - 2026-11-27

First public release.

### Added
- Stdlib-only detection engine with no dependencies for the core.
- Categorical markers that benign code never produces: `_0x` identifier
  arrays, `Math.imul` opaque-predicate chains, runtime decoder loops, and `!![]`
  self-defending code.
- Ordinary minified bundles (jQuery, Lodash) are recognized as benign.
- Directory fingerprinting for known hardeners (BLA).
- CLI with `--json`, `--quiet`, `--threshold`, and CI-friendly exit codes.
- FastMCP server exposing `check_file`, `check_source`, and `scan_repo`.
- Labelled evaluation corpus and the `eval_corpus.py` regression harness.

[Unreleased]: https://github.com/ManiraM-1/tarpit-guard/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/ManiraM-1/tarpit-guard/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/ManiraM-1/tarpit-guard/releases/tag/v0.2.0
