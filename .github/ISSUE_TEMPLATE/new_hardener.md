---
name: Support a new hardener
about: Add detection for another obfuscator or packer
title: "[hardener] support "
labels: enhancement, hardener
---

**Hardener**
Name and link of the tool (e.g. PyArmor, javascript-obfuscator preset, a
commercial packer).

**Fingerprint artifacts**
Any files or directories it leaves behind that identify it on sight (config
files, output folders, marker comments). These become `FINGERPRINT_FILES` /
`FINGERPRINT_DIRS` entries.

**In-file signatures**
Patterns inside the output that are distinctive and that benign code does not
produce (identifier shapes, specific runtime helpers, string-encoding schemes).

**Sample**
A small file produced by this hardener, for `corpus/obfuscated/`. The more real
the sample, the better.

**Notes**
Anything else: does it mimic minification, target a specific language, etc.
