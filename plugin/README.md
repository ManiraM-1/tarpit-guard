# tarpit-guard plugin

Some code is deliberately obfuscated to trap AI agents: reading or tracing it burns a huge number of tokens and leads nowhere. This plugin gives Claude a pre-flight check. Before Claude reads an unfamiliar file or repository, it can score the text 0-100 for deliberate anti-analysis obfuscation. If a file is flagged as hardened, Claude stops and tells you instead of spending your budget on it.

## Install in Claude Code

```
/plugin install tarpit-guard --marketplace ManiraM-1/tarpit-guard
```

## What it adds

One skill, `tarpit-check`. It tells Claude when to run the check and what to do with the result. The plugin itself contains only instructions; the check is done by the open-source [`tarpit-guard`](https://pypi.org/project/tarpit-guard/) command-line tool.

## How to use it

Claude runs the check on its own before reading suspicious code. You can also ask, for example: "check vendor/app.min.js for a tarpit before you read it" or "scan this repo for tarpits first". If a file is flagged, Claude skips it.

## What it runs and what data it sends

The skill asks Claude to run `tarpit-guard <path>` if it is installed, or `uvx tarpit-guard@0.2.2 <path>` if [uv](https://docs.astral.sh/uv/) is installed. With uvx, the first run downloads that pinned release from PyPI. If neither is available, Claude points you to the [install instructions](https://github.com/ManiraM-1/tarpit-guard#install) and does not install anything without your agreement. The tool only reads the files you point it at and measures the shape of their text. It never runs, decodes or deobfuscates code, makes no network requests while it runs, and never stores or sends your data anywhere. See the [privacy policy](https://github.com/ManiraM-1/tarpit-guard/blob/main/PRIVACY.md).

Prefer MCP tools? Use the Claude Desktop extension or the PyPI package from the main repository instead.

## License

MIT. Source and issues: https://github.com/ManiraM-1/tarpit-guard
