"""Every place that pins the release version must match pyproject.toml."""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def project_version(path):
    match = re.search(r'(?m)^version = "([^"]+)"$', path.read_text(encoding="utf-8"))
    return match.group(1)


VERSION = project_version(ROOT / "pyproject.toml")


class TestReleaseVersions(unittest.TestCase):
    def test_registry_server_json(self):
        server = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
        self.assertEqual(server["version"], VERSION)
        self.assertEqual(server["packages"][0]["version"], VERSION)

    def test_extension_manifest(self):
        manifest = json.loads((ROOT / "mcpb" / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], VERSION)

    def test_extension_pyproject(self):
        self.assertEqual(project_version(ROOT / "mcpb" / "pyproject.toml"), VERSION)

    def test_plugin_manifest(self):
        plugin = json.loads((ROOT / "plugin" / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(plugin["version"], VERSION)

    def test_plugin_bundles_the_current_detector(self):
        bundled = ROOT / "plugin" / "skills" / "tarpit-check" / "scripts" / "tarpit_guard"
        for name in ("__init__.py", "detector.py", "cli.py"):
            with self.subTest(file=name):
                self.assertEqual(
                    (bundled / name).read_bytes(),
                    (ROOT / "tarpit_guard" / name).read_bytes(),
                    f"plugin copy of {name} is stale: copy tarpit_guard/{name} over it",
                )

    def test_extension_lists_every_server_tool(self):
        manifest = json.loads((ROOT / "mcpb" / "manifest.json").read_text(encoding="utf-8"))
        listed = {tool["name"] for tool in manifest["tools"]}
        source = (ROOT / "tarpit_guard" / "mcp_server.py").read_text(encoding="utf-8")
        defined = set(re.findall(r"@mcp\.tool\([^\n]*\)\ndef (\w+)\(", source))
        self.assertEqual(listed, defined)


if __name__ == "__main__":
    unittest.main()
