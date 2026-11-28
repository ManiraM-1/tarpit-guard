import argparse
import json
import os
import sys

from .detector import analyze_file, repo_fingerprints

SCAN_EXTS = {".js", ".mjs", ".cjs", ".ts", ".jsx", ".tsx", ".py", ".wasm.js"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", "__pycache__", ".venv"}


def _iter_files(root):
    if os.path.isfile(root):
        yield root
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            if os.path.splitext(f)[1] in SCAN_EXTS:
                yield os.path.join(dirpath, f)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="tarpit-guard",
        description="Flag AI-reverse-engineering tarpits (obfuscated / token-burning code) before you waste a budget analyzing them.")
    parser.add_argument("path", nargs="?", help="File or directory to scan.")
    parser.add_argument("--json", action="store_true", help="Emit raw JSON.")
    parser.add_argument("--threshold", type=float, default=55.0,
                        help="Score at/above which a file is called a tarpit.")
    parser.add_argument("--quiet", action="store_true",
                        help="Only print files at/above the threshold.")
    parser.add_argument("--mcp", action="store_true",
                        help="Start the MCP server over stdio instead of scanning "
                             "(needs the [mcp] extra).")
    args = parser.parse_args(argv)

    if args.mcp:
        from .mcp_server import run
        run()
        return 0
    if args.path is None:
        parser.error("the following arguments are required: path")

    if not os.path.exists(args.path):
        print(f"path not found: {args.path}", file=sys.stderr)
        return 2

    fingerprints = repo_fingerprints(args.path) if os.path.isdir(args.path) else []

    results = []
    for fp in _iter_files(args.path):
        r = analyze_file(fp)
        if "error" in r:
            continue
        r["hardened"] = r["score"] >= args.threshold
        results.append(r)

    results.sort(key=lambda r: r["score"], reverse=True)
    flagged = [r for r in results if r["hardened"]]

    report = {
        "scanned": len(results),
        "flagged": len(flagged),
        "tool_fingerprints": fingerprints,
        "results": results,
    }

    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    if fingerprints:
        print("Tool fingerprints found (strong signal of deliberate hardening):")
        for h in fingerprints:
            print(f"  [{h['tool']}] {h['kind']}: {h['path']}")
        print()

    shown = flagged if args.quiet else results
    if not shown:
        print("No tarpit-like files found.")
    for r in shown:
        tag = "TARPIT" if r["hardened"] else "ok"
        print(f"[{tag}] score={r['score']:>5} conf={r['confidence']:.2f}  {r['path']}")
        if r["hardened"]:
            ev = r["evidence"]
            print(f"         {ev['size_bytes']}B / {ev['line_count']} lines, "
                  f"Math.imul×{ev['math_imul_count']}, decoder_pairs={ev['decoder_pairs']}, "
                  f"garbled_idents={ev['garbled_identifiers']}, decoy_hits={ev['decoy_vocab_hits']}")
            print(f"         fired: {', '.join(r['fired_signals'])}")
            print(f"         -> {r['recommended_strategy']}")

    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main())
