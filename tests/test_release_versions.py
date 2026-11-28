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

    def test_plugin_skill_pins_the_current_release(self):
        skill = (ROOT / "plugin" / "skills" / "tarpit-check" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn(f"uvx tarpit-guard@{VERSION} ", skill)

    def test_plugin_readme_pins_the_current_release(self):
        readme = (ROOT / "plugin" / "README.md").read_text(encoding="utf-8")
        self.assertIn(f"uvx tarpit-guard@{VERSION} ", readme)

    def test_extension_lists_every_server_tool(self):
        manifest = json.loads((ROOT / "mcpb" / "manifest.json").read_text(encoding="utf-8"))
        listed = {tool["name"] for tool in manifest["tools"]}
        source = (ROOT / "tarpit_guard" / "mcp_server.py").read_text(encoding="utf-8")
        defined = set(re.findall(r"@mcp\.tool\([^\n]*\)\ndef (\w+)\(", source))
        self.assertEqual(listed, defined)


if __name__ == "__main__":
    unittest.main()
