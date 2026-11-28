# Security Policy

## Supported versions

Only the latest release on [PyPI](https://pypi.org/project/tarpit-guard/)
receives security fixes.

## Reporting a vulnerability

Please **do not open a public issue** for a security problem.

Report it privately through GitHub instead:

1. Go to the [Security tab](https://github.com/ManiraM-1/tarpit-guard/security) of this repository.
2. Click **Report a vulnerability**.
3. Describe the problem, how to reproduce it, and the impact you expect.

You should get a first reply within 7 days. Once a fix is released, you will be
credited in the changelog unless you prefer not to be.

## What counts as a security issue

tarpit-guard reads untrusted files, so these are in scope:

- A crafted file that makes the scanner crash, hang, or use unbounded memory or CPU.
- A crafted file or directory that makes the scanner read, write, or execute
  anything outside the path it was asked to scan.
- Anything in the MCP server that lets a caller do more than scan.

**Detection misses are not security issues.** If hardened code scores too low,
or clean code scores too high, please open a normal
[missed tarpit](https://github.com/ManiraM-1/tarpit-guard/issues/new?template=missed_tarpit.md)
or [false positive](https://github.com/ManiraM-1/tarpit-guard/issues/new?template=false_positive.md)
issue.

## Out of scope by design

tarpit-guard never deobfuscates or extracts secrets from hardened code.
Requests to add that ability will be declined. See
[CONTRIBUTING.md](CONTRIBUTING.md#the-one-hard-rule).
