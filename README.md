# 🪤 tarpit-guard

**A pre-flight guard for AI code-analysis agents.** It scores a file or repository for signs of deliberate *anti-analysis hardening* — the obfuscation and "token-burning" tricks that tools like [BLA](https://github.com/qybaihe/bla) apply to make AI reverse-engineering expensive — and tells an agent, **before it spends a budget**, whether a target is a tarpit and what to do instead.

> One ~1K-token check that prevents a 60K-token mistake.

---

## Table of contents

- [The problem](#the-problem)
- [What this is — and what it is not](#what-this-is--and-what-it-is-not)
- [How it works](#how-it-works)
- [Signals](#signals)
- [Tool fingerprints](#tool-fingerprints)
- [Scoring and thresholds](#scoring-and-thresholds)
- [Install](#install)
- [CLI usage](#cli-usage)
- [MCP usage (for agents)](#mcp-usage-for-agents)
- [Example output](#example-output)
- [Project layout](#project-layout)
- [Limitations and false positives](#limitations-and-false-positives)
- [Roadmap](#roadmap)
- [FAQ](#faq)
- [License](#license)

---

## The problem

Source-hardening tools defend software by making it hostile to static analysis. A tiny, readable source file is transformed into a large, deliberately confusing one that still behaves identically:

| | Original | Hardened |
|---|---|---|
| Size | 418 B | 184 KB (**~440×**) |
| Lines | 15 | 2,998 |
| Secret string in cleartext | yes | no (encrypted) |
| Output when run | identical | identical |

The hardened file pads real logic with decoy functions, wraps branches behind opaque-predicate math, encrypts string literals behind runtime decoder loops, and plants jargon "canaries" written specifically to mislead a reading agent.

For an AI agent, the trap is cost. Read-and-trace the whole thing and you burn input tokens on ingestion and reasoning tokens on dead ends — and often still reach a wrong conclusion. The cheap counter is not to out-analyze the obfuscation; it is to **detect the tarpit first** and switch to dynamic analysis (run it in a sandbox, observe its behavior), which walks past nearly all static obfuscation for almost no tokens.

`tarpit-guard` is that detection step.

---

## What this is — and what it is not

**It is** a detector and triage guard. It answers one question: *does this look deliberately hardened, and if so, what is the cheaper way in?* It emits a score, the signals that fired, and a recommended strategy.

**It is not** a deobfuscator, a cracker, or a secret extractor. It never reverses anyone's protection or recovers hidden values. That is precisely the reverse-engineering these hardening tools exist to stop — building it would make this project the thing it is meant to warn about. The line is deliberate and permanent: `tarpit-guard` reads *shape*, never *meaning*.

---

## How it works

The engine is pure Python standard library — no dependencies, no network, nothing to install for the core. It runs entirely on local text.

1. **Repository sweep** (directory mode): walk the tree, skipping `node_modules`, `.git`, `dist`, `build`, and the like, and look for tool fingerprints.
2. **Per-file analysis**: for each candidate file, compute a set of cheap structural and statistical signals from the raw text — no execution, no parsing of untrusted code.
3. **Weighted score**: combine the signals into a 0–100 score and a confidence derived from how many independent signals fired.
4. **Verdict**: above the threshold, the file is a tarpit; the engine returns the evidence and a recommended strategy instead of a pile of extracted facts.

Because every signal is a count or ratio over text, the check is orders of magnitude cheaper than the analysis it protects.

---

## Signals

Each file is scored on weighted signals. No single one convicts; hardened code lights up several at once, which is what drives confidence.

| Signal | Weight | What it catches |
|---|---:|---|
| `opaque_predicate_density` | 0.20 | `Math.imul` / `>>> 0` tautology chains that guard real branches behind always-true math |
| `decoder_loops` | 0.18 | `fromCharCode` + `charCodeAt` + XOR loops that reconstruct encrypted string literals at runtime |
| `garbled_identifier_ratio` | 0.16 | mangled names such as `encodeFrozenScopeV4ue7`, `runtimeSeedLocalScopeCfg527zm` |
| `max_line_length` | 0.10 | single enormous machine-generated lines |
| `unique_identifier_bloat` | 0.10 | hundreds of junk/decoy functions inflating the surface area |
| `decoy_vocabulary_density` | 0.10 | planted jargon clusters (enclave / attestation / TPM / HSM / canary) meant to mislead a reader |
| `avg_line_length` | 0.08 | overall machine-generated layout |
| `identifier_entropy` | 0.05 | high-entropy name soup |
| `low_comment_ratio` | 0.03 | generated code rarely carries comments (only applied to larger files) |

Each signal is normalized to 0–1 against an empirical cutoff, then weighted. The `evidence` block in the output reports the raw underlying counts (file size, `Math.imul` count, decoder pairs, garbled-identifier count, decoy hits, comment ratio, identifier entropy) so a human or agent can sanity-check *why* a file was flagged.

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

- **Score** — 0–100, the weighted sum of signals.
- **Confidence** — rises with the number of independent signals that cross their own half-way mark; four or more means full confidence.
- **Threshold** — default **55**. At or above it, `hardened` is true. Tunable with `--threshold` (CLI) or the `threshold` argument (MCP).

Calibration against BLA output:

| File | Score | Confidence | Verdict |
|---|---:|---:|---|
| original `app.js` (15 lines) | **4.4** | 0.25 | ok |
| BLA-hardened `app.js` | **62.1** | 1.00 | TARPIT |

---

## Install

```bash
git clone https://github.com/ManiraM-1/tarpit-guard.git
cd tarpit-guard

pip install -e .          # core CLI — standard library only
pip install -e ".[mcp]"   # adds the FastMCP server (fastmcp>=2.0)
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

python -m tarpit_guard.cli path/to/file.js   # run without installing
```

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

## MCP usage (for agents)

Run the server:

```bash
python -m tarpit_guard.mcp_server
```

It exposes three tools:

| Tool | Use |
|---|---|
| `check_file(path)` | score one file before reading it |
| `check_source(text, label)` | score a raw snippet without touching disk |
| `scan_repo(root, threshold)` | sweep a tree for fingerprints and tarpit files |

**The intended agent loop:**

```
encounter unfamiliar file
        │
        ▼
  check_file(path)
        │
  hardened? ──no──▶ analyze normally
        │
       yes
        │
        ▼
  skip the full read →
  run it in a sandbox and observe I/O,
  or escalate to a human
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

[TARPIT] score= 62.1 conf=1.00  ./BLA/.bla-hardened/app.js
         182865B / 2998 lines, Math.imul×246, decoder_pairs=8, garbled_idents=190, decoy_hits=491
         fired: max_line_length, decoder_loops, unique_identifier_bloat, low_comment_ratio, identifier_entropy
         -> Treat as a tarpit. Do NOT read the whole file or trace it statically.
            Prefer dynamic analysis (run in a sandbox and observe I/O) or escalate to a human.
[ok] score=  4.4 conf=0.25  ./BLA/app.js
```

---

## Project layout

```
tarpit-guard/
├── pyproject.toml
├── README.md
├── .gitignore
└── tarpit_guard/
    ├── __init__.py        # public API: analyze_file, analyze_text, repo_fingerprints
    ├── detector.py        # scoring engine (stdlib only)
    ├── cli.py             # command-line entry point
    └── mcp_server.py      # FastMCP wrapper
```

---

## Limitations and false positives

This is a v0.1 heuristic, and honesty about its edges matters more than a clean pitch:

- **Tuned against one hardener.** It is calibrated on BLA output plus a single clean negative control. It has not yet been tested against a broad corpus.
- **Minified ≠ hardened.** A legitimately minified bundle (`vendor.js`, a production React build) shares some signals — long lines, low comments, mangled names — and may trip the score. Decoy vocabulary, opaque-predicate density, and decoder loops are what separate *hostile* obfuscation from *ordinary* minification, but the boundary needs a real test set.
- **Static only.** It reads the file as text. It does not and should not execute anything it scans.
- **Thresholds are empirical.** 55 is a starting point, not a derived constant. Expect to tune it per language and per codebase.

Reducing false positives is the single most important thing between v0.1 and a version you can trust in CI.

---

## Roadmap

- [ ] False-positive corpus: a set of normal + minified + obfuscated samples to calibrate against.
- [ ] More tool fingerprints (`javascript-obfuscator`, webpack/terser signatures, PyArmor, etc.).
- [ ] Per-language signal profiles (JS/TS vs Python vs WASM-glue).
- [ ] Confidence calibration from the corpus rather than a fixed signal count.
- [ ] Optional sandbox-runner helper that an agent can call after a tarpit verdict.

---

## FAQ

**Does this crack or defeat BLA?** No. It detects that hardening is present and recommends a cheaper strategy. It never reverses the protection or extracts secrets.

**Is "burning all the AI's tokens" real?** Partly. Hardening genuinely raises the cost of *static* analysis and genuinely hides string secrets. It does not reliably exhaust a budget — a dynamic approach (run it, watch it) or a budget-aware agent that probes instead of ingesting sidesteps most of it. `tarpit-guard` exists to make that cheaper path the default.

**Why stdlib-only for the core?** Portability and auditability. The thing that inspects untrusted code should itself be tiny, dependency-free, and easy to read.

---

## License

MIT (see `LICENSE`).
