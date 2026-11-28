#!/usr/bin/env bash
# Builds dist/tarpit-guard-<version>.mcpb, the Claude Desktop extension.
# Needs Node.js (for npx) and Python 3. Run from anywhere: mcpb/build.sh
set -euo pipefail

MCPB_CLI_VERSION="2.1.2"
here="$(cd "$(dirname "$0")" && pwd)"
root="$(dirname "$here")"
stage="$root/build/mcpb"
version="$(python3 -c "import tomllib,sys; print(tomllib.load(open(sys.argv[1],'rb'))['project']['version'])" "$root/pyproject.toml")"

rm -rf "$stage"
mkdir -p "$stage/tarpit_guard" "$root/dist"
cp "$here/manifest.json" "$here/pyproject.toml" "$here/server.py" "$here/icon.png" "$here/.mcpbignore" "$stage/"
cp "$root/LICENSE" "$root/README.md" "$stage/"
cp "$root"/tarpit_guard/*.py "$stage/tarpit_guard/"

# Keep the bundle's version in step with the package version.
python3 - "$stage" "$version" <<'PY'
import json, re, sys
stage, version = sys.argv[1], sys.argv[2]
m = json.load(open(f"{stage}/manifest.json"))
m["version"] = version
json.dump(m, open(f"{stage}/manifest.json", "w"), indent=2)
p = open(f"{stage}/pyproject.toml").read()
p = re.sub(r'(?m)^version = ".*"$', f'version = "{version}"', p, count=1)
open(f"{stage}/pyproject.toml", "w").write(p)
PY

npx --yes "@anthropic-ai/mcpb@${MCPB_CLI_VERSION}" validate "$stage/manifest.json"
npx --yes "@anthropic-ai/mcpb@${MCPB_CLI_VERSION}" pack "$stage" "$root/dist/tarpit-guard-${version}.mcpb"
echo "Built dist/tarpit-guard-${version}.mcpb"
