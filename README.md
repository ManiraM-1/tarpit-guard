# tarpit-guard

[![CI](https://github.com/ManiraM-1/tarpit-guard/actions/workflows/ci.yml/badge.svg)](https://github.com/ManiraM-1/tarpit-guard/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/tarpit-guard)](https://pypi.org/project/tarpit-guard/)
[![Python](https://img.shields.io/pypi/pyversions/tarpit-guard)](https://pypi.org/project/tarpit-guard/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**A pre-flight guard for AI code-analysis agents.** It scores a file or repository for signs of deliberate *anti-analysis hardening*, the obfuscation and "token-burning" tricks that tools like [BLA](https://github.com/qybaihe/bla) apply to make AI reverse-engineering expensive, and tells an agent, **before it spends a budget**, whether a target is a tarpit and what to do instead.

> One ~1K-token check that prevents a 60K-token mistake.

**Contributions welcome**, especially real-world samples that widen the test corpus. See [Contributing](#contributing), or pick up a [good first issue](https://github.com/ManiraM-1/tarpit-guard/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

---

## Table of contents

- [The problem](#the-problem)
- [What this is, and what it is not](#what-this-is-and-what-it-is-not)
- [How it works](#how-it-works)
- [Signals](#signals)
- [Tool fingerprints](#tool-fingerprints)
- [Scoring and thresholds](#scoring-and-thresholds)
- [Install](#install)
- [CLI usage](#cli-usage)
- [Use it in Claude](#use-it-in-claude)
- [MCP usage (for agents)](#mcp-usage-for-agents)
- [Example output](#example-output)
- [Project layout](#project-layout)
- [Limitations and false positives](#limitations-and-false-positives)
- [Roadmap](#roadmap)
- [FAQ](#faq)
- [Contributing](#contributing)
- [Privacy Policy](#privacy-policy)
- [License](#license)

---

## The problem

Source-hardening tools defend software by making it hostile to static analysis. A tiny, readable source file is transformed into a large, deliberately confusing one that still behaves identically:

| | Original | Hardened |
|---|---|---|
| Size | 418 B | 184 KB (**~440x**) |
| Lines | 15 | 2,998 |
| Secret string in cleartext | yes | no (encrypted) |
| Output when run | identical | identical |

The hardened file pads real logic with decoy functions, wraps branches behind opaque-predicate math, encrypts string literals behind runtime decoder loops, and plants jargon "canaries" written specifically to mislead a reading agent.

For an AI agent, the trap is cost. Read-and-trace the whole thing and you burn input tokens on ingestion and reasoning tokens on dead ends, and often still reach a wrong conclusion. The cheap counter is not to out-analyze the obfuscation. It is to **detect the tarpit first and stop**: don't read it, don't trace it, skip it or hand it to a human. A ~1K-token check replaces a 60K-token dead end.

`tarpit-guard` is that detection step.

---

## What this is, and what it is not

**It is** a detector and triage guard. It answers one question: *does this look deliberately hardened, and if so, what is the cheaper way in?* It emits a score, the signals that fired, and a recommended strategy.

**It is not** a deobfuscator, a cracker, or a secret extractor. It never reverses anyone's protection or recovers hidden values. That is precisely the reverse-engineering these hardening tools exist to stop, and building it would make this project the thing it is meant to warn about. The line is deliberate and permanent: `tarpit-guard` reads *shape*, never *meaning*.

---

## How it works

The engine is pure Python standard library. No dependencies, no network, nothing to install for the core. It runs entirely on local text.

1. **Repository sweep** (directory mode): walk the tree, skipping `node_modules`, `.git`, `dist`, `build`, and the like, and look for tool fingerprints.
2. **Per-file analysis**: for each candidate file, compute a set of cheap structural and statistical signals from the raw text. No execution, no parsing of untrusted code.
3. **Weighted score**: combine the signals into a 0 to 100 score and a confidence derived from how many independent signals fired.
4. **Verdict**: above the threshold, the file is a tarpit. The engine returns the evidence and a recommended strategy instead of a pile of extracted facts.

Because every signal is a count or ratio over text, the check is orders of magnitude cheaper than the analysis it protects.

---

## Signals

Detection keys on signals that benign code, even heavily minified code, essentially never produces. This is deliberate. The hard problem is not spotting that a file is *machine-generated* (minified bundles are too). It is telling *hostile* obfuscation apart from *ordinary* minification. Size and line-length are explicitly **not** primary signals, because that is exactly what minification trips.

| Signal | Weight | What it catches |
|---|---:|---|
| `opaque_predicate_density` | 0.28 | `Math.imul` tautology chains that guard real branches behind always-true math (BLA) |
| `hex_identifier_array` | 0.28 | dense `_0x...` string-array identifiers (javascript-obfuscator family) |
| `decoder_loops` | 0.22 | `fromCharCode` + `charCodeAt` loops that reconstruct encrypted string literals at runtime |
| `obfuscator_control_tricks` | 0.12 | self-defending / control-flow tricks (`!![]`, `.split('\|')` dispatch) |
| `decoy_vocabulary_density` | 0.06 | planted jargon clusters (enclave / attestation / TPM / canary) meant to mislead a reader |
| `garbled_identifier_ratio` | 0.04 | mangled names such as `encodeFrozenScopeV4ue7` |

On top of the weighted score, four **categorical markers** apply a decisive floor, because they are signatures essentially impossible in hand-written or merely-minified code: a dense `_0x` identifier array, three or more runtime decoder loops, `Math.imul` opaque-predicate chains, or repeated `!![]` self-defending tricks. Any one present pushes the file over the line.

Conversely, a file **dominated by 1 to 2 character identifiers** (the minification tell, 60 to 70% in jQuery/Lodash builds versus about 10% in hostile files) with **none** of those markers is recognized as benign minification and capped low, with the strategy "read the original source or a source map, not the bundle."

The `evidence` block reports the raw counts (`Math.imul`, hex identifiers, decoder pairs, decoy hits, short-identifier ratio, and so on) so a human or agent can sanity-check *why* a file scored as it did.

---

## Tool fingerprints

Some artifacts are near-certain evidence of deliberate hardening on their own, independent of file contents. Directory scans report them separately as a strong standalone signal:

| Fingerprint | Tool |
|---|---|
| `.bla-hardened/` directory | BLA |
| `.blarc` | BLA |
| `bla-harden-summary.json` | BLA |

The fingerprint map is a plain table in `detector.py` and is meant to grow as more hardeners are catalogued.

---

## Scoring and thresholds

- **Score**: 0 to 100, the weighted sum of signals.
- **Confidence**: rises with the number of independent signals that cross their own half-way mark. Four or more means full confidence.
- **Threshold**: default **55**. At or above it, `hardened` is true. Tunable with `--threshold` (CLI) or the `threshold` argument (MCP).

### Evaluation

`eval_corpus.py` scores a labelled corpus (`corpus/`) of clean source, real minified bundles, and hostile obfuscation, and reports false positives and false negatives. It doubles as a regression test (non-zero exit on any miss).

v0.2 results (threshold 55):

| Bucket | File | Score | Verdict |
|---|---|---:|---|
| clean | jquery.source.js / lodash.source.js | 0.0 | ok |
| clean | detector.py (contains the decoy word list) | 9.5 | ok |
| minified | jquery.min.js | 0.0 | ok |
| minified | lodash.min.js | 0.0 | ok |
| obfuscated | bla_hardened_app.js | 78.0 | **TARPIT** |
| obfuscated | js-obfuscator_sample.js | 85.0 | **TARPIT** |

**0 false positives, 0 false negatives.** Highest benign score 9.5, lowest hostile score 78.0, a **+68.5** margin, stable across any threshold from about 10 to about 77. (For contrast, v0.1 leaned on file size and scored minified jQuery *above* a real obfuscated file. That regression is what this corpus exists to prevent.)

---

## Install

From PyPI:

```bash
pip install tarpit-guard          # core CLI, standard library only
pip install "tarpit-guard[mcp]"   # adds the FastMCP server (fastmcp>=2.0)
```

Or run it without installing (needs pipx):

```bash
pipx run tarpit-guard path/to/code
```

For development (from a clone):

```bash
git clone https://github.com/ManiraM-1/tarpit-guard.git
cd tarpit-guard
pip install -e ".[mcp]"
```

Requires Python 3.9+.

---

## CLI usage

```bash
tarpit-guard path/to/file.js            # score a single file
tarpit-guard path/to/repo               # scan a tree + report fingerprints
tarpit-guard path/to/repo --quiet       # only show flagged files
tarpit-guard path/to/repo --json        # machine-readable report
tarpit-guard path/to/repo --threshold 45
tarpit-guard --mcp                      # start the MCP server instead (needs the [mcp] extra)

python -m tarpit_guard.cli path/to/file.js   # if the console script is not on PATH
```

See [`SCHEMA.md`](SCHEMA.md) for the frozen `--json` and MCP output schema contract.

**Exit codes** make it a drop-in CI gate:

| Code | Meaning |
|---:|---|
| `0` | nothing flagged |
| `1` | at least one tarpit found |
| `2` | path not found |

```yaml
# e.g. fail a job if a dependency ships hardened artifacts
- run: tarpit-guard ./vendor --quiet
```

---

## Use it in Claude

**Claude Desktop (one click, nothing else to install).** Download `tarpit-guard-<version>.mcpb` from the [latest release](https://github.com/ManiraM-1/tarpit-guard/releases/latest) and double-click it, or drag it into the Claude Desktop window. You can also open **Settings > Extensions > Advanced settings > Install Extension...** and pick the file. Claude Desktop sets up Python and the dependencies for you.

**Claude Code.** Install the plugin from this repository. It adds a `tarpit-check` skill that carries the detector itself, so nothing else is downloaded:

```
/plugin install tarpit-guard --marketplace ManiraM-1/tarpit-guard
```

The extension gives Claude the three MCP tools below; the plugin runs the same checks through its skill. Then ask, for example, "check vendor/app.min.js for a tarpit before you read it". To build the extension yourself, run `mcpb/build.sh` (needs Node.js and Python 3.11+).

---

## MCP usage (for agents)

Install with the MCP extra, then run the server over stdio:

```bash
pip install "tarpit-guard[mcp]"
tarpit-guard-mcp            # or: tarpit-guard --mcp, or: python -m tarpit_guard.mcp_server
```

To add it to an MCP client such as Claude Desktop, Cursor or VS Code, use this config. It needs [uv](https://docs.astral.sh/uv/), and nothing has to be installed first:

```json
{
  "mcpServers": {
    "tarpit-guard": {
      "command": "uvx",
      "args": ["--from", "tarpit-guard[mcp]", "tarpit-guard-mcp"]
    }
  }
}
```

Or run it in Docker, mounting the code to check read-only:

```bash
docker build -t tarpit-guard .
docker run -i --rm -v "$PWD:/work:ro" tarpit-guard
```

It exposes three read-only tools:

| Tool | Use |
|---|---|
| `check_file(path)` | score one file before reading it |
| `check_source(text, label)` | score a raw snippet without touching disk |
| `scan_repo(root, threshold)` | sweep a tree for fingerprints and tarpit files |

**The intended agent loop:**

```
encounter unfamiliar file
        |
        v
  check_file(path)
        |
  hardened? --no--> analyze normally
        |
       yes
        |
        v
  stop: don't read or trace it,
  skip the file, or flag it
  for a human
```

The guard turns "read everything and hope" into a deliberate, budgeted decision.

---

## Example output

```
$ tarpit-guard ./BLA

Tool fingerprints found (strong signal of deliberate hardening):
  [bla] dir: ./BLA/.bla-hardened
  [bla] file: ./BLA/.blarc
  [bla] file: ./BLA/.bla-hardened/bla-harden-summary.json

[TARPIT] score=   78 conf=1.00  ./BLA/.bla-hardened/app.js
         182865B / 2998 lines, Math.imul x246, decoder_pairs=8, garbled_idents=190, decoy_hits=487
         fired: opaque_predicate_density, decoder_loops, decoy_vocabulary_density
         -> Treat as a tarpit. Stop here: do not read, trace, or try to deobfuscate
            this file. Skip it and move on, or flag it for a human.
[ok] score=  0.0 conf=0.00  ./BLA/app.js
```

---

## Project layout

```
tarpit-guard/
|- pyproject.toml
|- README.md
|- LICENSE
|- .gitignore
|- eval_corpus.py         # scores corpus/, reports false positives/negatives
|- corpus/                # labelled samples: clean / minified / obfuscated
|- tarpit_guard/
   |- __init__.py         # public API: analyze_file, analyze_text, repo_fingerprints
   |- detector.py         # scoring engine (stdlib only)
   |- cli.py              # command-line entry point
   |- mcp_server.py       # FastMCP wrapper
|- mcpb/                  # Claude Desktop extension: manifest, icon, build.sh
|- plugin/                # Claude plugin: tarpit-check skill with a copy of the detector
```

---

## Limitations and false positives

This is a v0.2 heuristic, and honesty about its edges matters more than a clean pitch:

- **Small corpus.** It is calibrated on two hardeners (BLA, javascript-obfuscator) against clean source and real minified bundles, nine files in total. The separation is wide and clean, but a larger corpus (more obfuscators, more real-world bundles) is needed before leaning on it blindly.
- **Minified vs hardened is handled, not solved.** v0.2 correctly passes minified jQuery and Lodash while flagging both obfuscators, using short-identifier dominance plus categorical markers. An exotic bundler or a deliberately minification-mimicking obfuscator could still fool it, which is what growing the corpus guards against.
- **Static only.** It reads the file as text. It does not and should not execute anything it scans.
- **Thresholds are empirical.** 55 is the default, with a stable margin from about 10 to about 77 on the current corpus, but it is tuned, not derived. Expect to revisit it per language and per codebase.

---

## Roadmap

- [x] False-positive corpus: normal + minified + obfuscated samples to calibrate against (`corpus/`, `eval_corpus.py`).
- [x] Detect a second hardener family (javascript-obfuscator) alongside BLA.
- [x] Separate hostile obfuscation from ordinary minification.
- [ ] More tool fingerprints (webpack/terser signatures, PyArmor, obfuscator.io variants).
- [ ] Grow the corpus (more real bundles, more obfuscators) and pin thresholds against it.
- [ ] Per-language signal profiles (JS/TS vs Python vs WASM-glue).

---

## FAQ

**Does this crack or defeat BLA?** No. It detects that hardening is present and recommends a cheaper strategy. It never reverses the protection or extracts secrets.

**Is "burning all the AI's tokens" real?** Partly. Hardening genuinely raises the cost of *static* analysis and genuinely hides string secrets. It does not always exhaust a budget, but it reliably wastes one: an agent that reads and traces a hardened file spends heavily and often still reaches the wrong conclusion. `tarpit-guard` exists so the agent notices early and stops instead.

**Why stdlib-only for the core?** Portability and auditability. The thing that inspects untrusted code should itself be tiny, dependency-free, and easy to read.

---

## Contributing

Contributions are very welcome. This is early, and the most valuable help is **data, not just code**. A detector is only as good as the corpus it is tested against. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full guide.

**Good first contributions:**

- **Add a corpus sample.** Drop a real file into `corpus/clean/`, `corpus/minified/`, or `corpus/obfuscated/`, then run `python eval_corpus.py`. If it misclassifies your sample, that is a genuine, useful bug. Open an issue or PR with the file and its correct label.
- **Add a hardener fingerprint.** If you know another obfuscator's tell-tale artifacts (config files, output directories, identifier patterns), add them to `FINGERPRINT_FILES` / `FINGERPRINT_DIRS` or as a new signal in `detector.py`.
- **Report a false positive.** If `tarpit-guard` flags legitimate code (a particular bundler, a language it handles badly), that is exactly what we want to hear: a sample plus the score it got.
- **Per-language profiles.** The signals are JS-centric today. Python, WASM-glue, and others could use their own tuning.

New here? Browse the [good first issues](https://github.com/ManiraM-1/tarpit-guard/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22). Please also read the [Code of Conduct](CODE_OF_CONDUCT.md). To report a security problem privately, see [SECURITY.md](SECURITY.md). Release notes live in [CHANGELOG.md](CHANGELOG.md).

<!-- mcp-name: io.github.ManiraM-1/tarpit-guard -->

**Ground rule:** this is a *detector*, not a deobfuscator. PRs that reverse, strip, or extract secrets from hardened code are out of scope and will not be merged. The tool reads shape, never meaning.

**Workflow:** fork, branch, make sure `python eval_corpus.py` still exits clean (0 false positives / negatives), and open a PR describing what you changed and why. New detection behavior should come with a corpus sample that demonstrates it.

---

## Privacy Policy

tarpit-guard collects no data. It runs locally, makes no network requests while it runs, and stores nothing. Installing it downloads packages from PyPI. Full policy: [PRIVACY.md](PRIVACY.md).

---

## License

MIT (see [`LICENSE`](LICENSE)).
