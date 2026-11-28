# tarpit-guard plugin

Some code is deliberately obfuscated to trap AI agents: reading or tracing it burns a huge number of tokens and leads nowhere. This plugin gives Claude a pre-flight check. Before Claude reads an unfamiliar file or repository, it can score the text 0-100 for deliberate anti-analysis obfuscation. If a file is flagged as hardened, Claude stops and tells you instead of spending your budget on it.

## Install in Claude Code

```
/plugin install tarpit-guard --marketplace ManiraM-1/tarpit-guard
```

## What it adds

One local MCP server, `tarpit-guard`, with three read-only tools:

- `check_file`: check one file before reading it.
- `check_source`: check code that is already in memory, such as a paste or a diff.
- `scan_repo`: scan a folder for obfuscator fingerprints and tarpit files.

## How to use it

Ask Claude something like "check vendor/app.min.js for a tarpit before you read it" or "scan this repo for tarpits first". If a result says `hardened: true`, Claude should skip that file.

## What it runs and what data it sends

The server is started with `uvx --from tarpit-guard[mcp]==0.2.2 tarpit-guard-mcp`, so it needs [uv](https://docs.astral.sh/uv/). The first start downloads the pinned `tarpit-guard` package and its dependencies from PyPI. After that, everything runs locally. The tools only read the files or text you point them at and measure their shape. They never run, decode or deobfuscate code, never make network requests, and never store or send your data anywhere. See the [privacy policy](https://github.com/ManiraM-1/tarpit-guard/blob/main/PRIVACY.md).

The local server loads in Claude Code and in Cowork sessions that run on your computer.

## License

MIT. Source and issues: https://github.com/ManiraM-1/tarpit-guard
