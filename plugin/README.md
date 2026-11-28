# tarpit-guard plugin

Some code is deliberately obfuscated to trap AI agents: reading or tracing it burns a huge number of tokens and leads nowhere. This plugin gives Claude a pre-flight check. Before Claude reads an unfamiliar file or repository, it can score the text 0-100 for deliberate anti-analysis obfuscation. If a file is flagged as hardened, Claude stops and tells you instead of spending your budget on it.

## Install in Claude Code

```
/plugin install tarpit-guard --marketplace ManiraM-1/tarpit-guard
```

## What it adds

One skill, `tarpit-check`. It tells Claude when to run the check and what to do with the result. The detector itself ships inside the skill as a small, readable Python script that uses only the standard library, so there is nothing to download or install.

## How to use it

Claude runs the check on its own before reading suspicious code. You can also ask, for example: "check vendor/app.min.js for a tarpit before you read it" or "scan this repo for tarpits first". If a file is flagged, Claude skips it.

## What it runs and what data it sends

The skill runs `python3` on the bundled script `skills/tarpit-check/scripts/tarpit_check.py`, with the file or folder you want checked. The script only reads those files and measures the shape of their text. It never runs, decodes or deobfuscates code, never makes network requests, and never stores or sends your data anywhere. It needs Python 3.9 or newer. See the [privacy policy](https://github.com/ManiraM-1/tarpit-guard/blob/main/PRIVACY.md).

Prefer MCP tools? Use the Claude Desktop extension or the PyPI package from the main repository instead.

## License

MIT. Source and issues: https://github.com/ManiraM-1/tarpit-guard
