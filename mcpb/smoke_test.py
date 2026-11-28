"""Start an unpacked extension the way Claude Desktop does and check its tools.

Usage: python mcpb/smoke_test.py <unpacked-bundle-dir> <file-to-check>
Needs uv on PATH. Exits non-zero if the server does not start, does not list
exactly check_file, check_source and scan_repo, or cannot check the file.
"""

import json
import subprocess
import sys

EXPECTED_TOOLS = {"check_file", "check_source", "scan_repo"}


def main(bundle_dir, target):
    manifest = json.load(open(f"{bundle_dir}/manifest.json", encoding="utf-8"))
    cfg = manifest["server"]["mcp_config"]
    args = [a.replace("${__dirname}", bundle_dir) for a in cfg["args"]]
    proc = subprocess.Popen(
        [cfg["command"], *args],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )

    def send(msg):
        proc.stdin.write(json.dumps(msg) + "\n")
        proc.stdin.flush()

    def receive():
        while True:
            line = proc.stdout.readline()
            if not line:
                sys.exit("server exited early:\n" + proc.stderr.read()[-3000:])
            msg = json.loads(line)
            if "id" in msg:
                return msg

    try:
        send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
            "protocolVersion": "2025-06-18", "capabilities": {},
            "clientInfo": {"name": "smoke-test", "version": "0"}}})
        receive()
        send({"jsonrpc": "2.0", "method": "notifications/initialized"})

        send({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        tools = {t["name"] for t in receive()["result"]["tools"]}
        print("tools:", sorted(tools))
        if tools != EXPECTED_TOOLS:
            sys.exit(f"expected tools {sorted(EXPECTED_TOOLS)}")

        send({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
              "params": {"name": "check_file", "arguments": {"path": target}}})
        result = receive()["result"]
        report = result.get("structuredContent") or json.loads(result["content"][0]["text"])
        print("check_file:", report["path"], "score", report["score"], "hardened", report["hardened"])
    finally:
        proc.terminate()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
