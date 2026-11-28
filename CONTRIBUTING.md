# Contributing to tarpit-guard

Thanks for considering a contribution. This project is early, and the single
most valuable thing you can add is **data**: real files that make the detector
smarter. Code is welcome too, but a good corpus sample is often worth more than
a clever heuristic.

## The one hard rule

`tarpit-guard` is a **detector**, not a deobfuscator. It reads the *shape* of
code to decide whether it is deliberately hardened. It must never reverse,
strip, or extract secrets from hardened code. Pull requests that do any of that
are out of scope and will not be merged, whatever the stated purpose. This line
is permanent.

## Ways to help

1. **Add a corpus sample.** The corpus under `corpus/` is the project's test
   set. Each file lives in one of three folders by its correct label:
   - `corpus/clean/`: ordinary, human-readable source.
   - `corpus/minified/`: legitimately minified or bundled code (benign).
   - `corpus/obfuscated/`: deliberately hardened or anti-analysis output.
   Add a file to the right folder, then run the evaluation (below). If the
   detector gets it wrong, you have found a real bug worth reporting.

2. **Add a hardener fingerprint.** If an obfuscator leaves tell-tale artifacts
   (a config file, an output directory, a signature identifier pattern), add it
   to `FINGERPRINT_FILES` / `FINGERPRINT_DIRS`, or add a new signal in
   `detector.py`. Include a sample that demonstrates it.

3. **Report a false positive or a missed tarpit.** Open an issue using the
   templates. A sample file plus the score it got is exactly what is needed.

4. **Improve per-language coverage.** The signals are JavaScript-centric today.
   Python, WASM glue code, and others could each use their own tuning.

## Development setup

```bash
git clone https://github.com/ManiraM-1/tarpit-guard.git
cd tarpit-guard
pip install -e ".[mcp]"
```

The core engine (`tarpit_guard/detector.py`) uses only the Python standard
library. Please keep it dependency-free. Optional extras (such as the MCP
server) may add dependencies behind an extra in `pyproject.toml`.

## Running the evaluation

The evaluation harness scores the whole corpus against its known labels and
reports false positives and false negatives. It exits non-zero on any miss, so
it works as a regression test:

```bash
python eval_corpus.py            # default threshold 55
python eval_corpus.py 45         # custom threshold
```

Any change to detection behavior should leave this exiting clean (0 false
positives, 0 false negatives), and new behavior should come with a corpus
sample that demonstrates it.

## Pull request checklist

- [ ] `python eval_corpus.py` exits clean.
- [ ] New detection behavior includes a corpus sample.
- [ ] The core engine stays standard-library only.
- [ ] No code that reverses, strips, or extracts from hardened files.
- [ ] The PR description says what changed and why.

## Code style

Keep the detector readable: it is a tool for inspecting untrusted code, so it
should itself be easy to audit. Prefer clear names and small functions over
cleverness.

## Releasing (maintainers)

Bump the version in every place below, or `tests/test_release_versions.py`
fails: `pyproject.toml`, `server.json`, `mcpb/manifest.json`,
`mcpb/pyproject.toml`, and `plugin/.claude-plugin/plugin.json` plus the
`tarpit-guard[mcp]==` pin in `plugin/.mcp.json`. Publishing a GitHub release
then uploads to PyPI, updates the MCP Registry, and attaches the Claude
Desktop extension (`.mcpb`) to the release.
