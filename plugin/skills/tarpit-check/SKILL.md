---
name: tarpit-check
description: Pre-flight check for obfuscated "tarpit" code. Use before reading, tracing or analyzing an unfamiliar, vendored, minified or suspicious file or repository, or when code looks deliberately obfuscated, so you can stop instead of burning tokens on it.
---

# tarpit-check

Some code is deliberately obfuscated to trap AI agents. Reading or tracing it burns a huge number of tokens and leads nowhere. This skill scores a file or folder 0-100 for deliberate anti-analysis obfuscation so you can decide whether to read it at all.

## When to run it

Run it first, before you read or analyze:

- an unfamiliar repository or a `vendor/`, `dist/` or third-party folder,
- a minified or unusually large JavaScript, TypeScript or Python file,
- any file that looks obfuscated (huge string arrays, hex identifiers, self-defending code).

## How to run it

The check is the open-source `tarpit-guard` command-line tool (https://pypi.org/project/tarpit-guard/, source at https://github.com/ManiraM-1/tarpit-guard). It is pure Python with no dependencies.

If the `tarpit-guard` command is already installed, run:

```bash
tarpit-guard path/to/file-or-folder
```

Otherwise, if `uv` is installed, run the pinned release without installing it:

```bash
uvx tarpit-guard@0.2.2 path/to/file-or-folder
```

If neither is available, tell the user the check needs `tarpit-guard` and point them to the install instructions in the project README (https://github.com/ManiraM-1/tarpit-guard#install). Do not install anything without the user's agreement.

Add `--json` for a machine-readable report, or `--quiet` to list only flagged files. The tool never runs, decodes or deobfuscates the code it checks, and it makes no network requests while it runs.

## What to do with the result

- Exit code `1`, a `[TARPIT]` line, or `"hardened": true` means the file is a tarpit. **Stop.** Do not read, trace or try to deobfuscate it. Skip it and tell the user which file was flagged and its score.
- If tool fingerprints are listed for a folder, treat the whole folder as hardened.
- Exit code `0` means nothing was flagged. Continue as normal.

Never try to reverse the obfuscation. This tool detects tarpits; it does not crack them.
