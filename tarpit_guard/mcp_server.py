import os
import sys
from typing import Annotated

try:
    from fastmcp import FastMCP
    from pydantic import Field
except ImportError:  # pragma: no cover - only hit without the [mcp] extra
    sys.exit("The MCP server needs the optional extra: pip install 'tarpit-guard[mcp]'")

from .detector import analyze_file, analyze_text, repo_fingerprints

mcp = FastMCP(
    "tarpit-guard",
    instructions=(
        "Pre-flight tarpit detector. Before reading an unfamiliar or suspicious "
        "file or repo, call check_file or scan_repo. If a result is hardened, stop: "
        "do not read, trace, or deobfuscate it. Skip it or tell the user."
    ),
)

SCAN_EXTS = {".js", ".mjs", ".cjs", ".ts", ".jsx", ".tsx", ".py"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", "__pycache__", ".venv"}


READ_ONLY = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
}


@mcp.tool(annotations={"title": "Check a file for a tarpit", **READ_ONLY})
def check_file(
    path: Annotated[str, Field(description="Path to the file to check, e.g. 'vendor/app.min.js'.")],
) -> dict:
    """Check one file for deliberate anti-AI obfuscation (a "tarpit") before reading it.

    Call this BEFORE reading or analyzing an unfamiliar or suspicious file. It only
    measures the text's shape; it never runs, decodes, or deobfuscates anything.

    Returns a report with `score` (0-100), `hardened` (true when score >= 55),
    `confidence`, the `fired_signals`, and a `recommended_strategy`.
    If `hardened` is true, stop: do not read or trace this file. Skip it, or report
    it to the user, instead of spending tokens on it.
    """
    return analyze_file(path)


@mcp.tool(annotations={"title": "Check source text for a tarpit", **READ_ONLY})
def check_source(
    text: Annotated[str, Field(description="The raw source code to check.")],
    label: Annotated[str, Field(description="A name for this snippet, echoed back as `path` in the report.")] = "snippet",
) -> dict:
    """Check a piece of source code for deliberate anti-AI obfuscation without touching disk.

    Use this when you have code in memory (a paste, a diff, a fetched file) rather than
    a path. Returns the same report as `check_file`. If `hardened` is true, stop and do
    not analyze the code further.
    """
    return analyze_text(text, path=label)


@mcp.tool(annotations={"title": "Scan a folder for tarpits", **READ_ONLY})
def scan_repo(
    root: Annotated[str, Field(description="Path to the directory to scan.")],
    threshold: Annotated[float, Field(description="Score at or above which a file counts as a tarpit (0-100).", ge=0, le=100)] = 55.0,
) -> dict:
    """Scan a directory for known obfuscator fingerprints and tarpit files.

    Use this before committing a budget to understanding an unfamiliar repository.
    Skips node_modules, .git, dist, build, __pycache__ and .venv, and checks JS/TS and
    Python files. Returns `scanned`, `flagged`, `tool_fingerprints`, `flagged_files`
    and `all_results`. Skip every file in `flagged_files` instead of reading it.
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
