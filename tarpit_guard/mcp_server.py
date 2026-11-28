import os
import sys

try:
    from fastmcp import FastMCP
except ImportError:  # pragma: no cover - only hit without the [mcp] extra
    sys.exit("The MCP server needs the optional extra: pip install 'tarpit-guard[mcp]'")

from .detector import analyze_file, analyze_text, repo_fingerprints

mcp = FastMCP("tarpit-guard")

SCAN_EXTS = {".js", ".mjs", ".cjs", ".ts", ".jsx", ".tsx", ".py"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", "__pycache__", ".venv"}


@mcp.tool()
def check_file(path: str) -> dict:
    """Score a single file for obfuscation / anti-analysis tarpit signals.

    Call this BEFORE reading or statically analyzing an unfamiliar file.
    If hardened is true, do not ingest the whole file; run it in a sandbox
    and observe its behavior instead.
    """
    return analyze_file(path)


@mcp.tool()
def check_source(text: str, label: str = "snippet") -> dict:
    """Score a raw source string for tarpit signals without touching disk."""
    return analyze_text(text, path=label)


@mcp.tool()
def scan_repo(root: str, threshold: float = 55.0) -> dict:
    """Scan a directory tree: report tool fingerprints and any tarpit files.

    Use this before an agent commits a budget to understanding a repo.
    """
    if not os.path.isdir(root):
        return {"error": f"not a directory: {root}"}

    results = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            if os.path.splitext(f)[1] in SCAN_EXTS:
                r = analyze_file(os.path.join(dirpath, f))
                if "error" not in r:
                    r["hardened"] = r["score"] >= threshold
                    results.append(r)

    results.sort(key=lambda r: r["score"], reverse=True)
    flagged = [r for r in results if r["hardened"]]
    return {
        "root": root,
        "scanned": len(results),
        "flagged": len(flagged),
        "tool_fingerprints": repo_fingerprints(root),
        "flagged_files": flagged,
        "all_results": results,
    }


def run():
    mcp.run()


if __name__ == "__main__":
    run()
