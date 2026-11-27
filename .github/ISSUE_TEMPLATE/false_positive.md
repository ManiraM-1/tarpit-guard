---
name: False positive (benign code flagged)
about: tarpit-guard called legitimate code a tarpit
title: "[false positive] "
labels: false-positive
---

**What was flagged**
The file or kind of code (e.g. a webpack production bundle, a specific library).

**Score and output**
Paste the `tarpit-guard` output, including the score, confidence, and `fired` signals.

```
paste here
```

**Why it is benign**
Briefly, what the file actually is and why it is not hostile obfuscation.

**Sample**
If you can share the file (or a reduced version that still reproduces the score),
attach it or link it. A sample lets us add it to `corpus/minified/` or
`corpus/clean/` as a regression test.

**Environment**
- tarpit-guard version (`pip show tarpit-guard`):
- Python version:
