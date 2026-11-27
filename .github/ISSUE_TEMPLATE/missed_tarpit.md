---
name: Missed tarpit (hostile code not flagged)
about: Deliberately hardened code that tarpit-guard did not catch
title: "[missed] "
labels: false-negative
---

**What should have been flagged**
The file or the hardening tool that produced it (e.g. PyArmor, obfuscator.io, a
packer).

**Score and output**
Paste the `tarpit-guard` output. The low score it got is the useful part.

```
paste here
```

**How it was hardened**
If you know the tool or technique (string encryption, control-flow flattening,
packing, etc.), say so. It helps us add the right signal.

**Sample**
Share the file if you can, ideally the smallest version that still slips
through. It becomes a new entry in `corpus/obfuscated/`.

**Environment**
- tarpit-guard version:
- Python version:
