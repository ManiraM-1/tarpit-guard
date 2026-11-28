## What this changes

<!-- One or two sentences. Link the issue it fixes, e.g. "Fixes #3". -->

## Why

<!-- The problem this solves, or the sample that motivated it. -->

## Checklist

- [ ] `python eval_corpus.py` exits clean (0 false positives, 0 false negatives)
- [ ] `python -m pytest` passes
- [ ] New detection behavior comes with a corpus sample that shows it
- [ ] The core engine (`tarpit_guard/detector.py`) still uses only the standard library
- [ ] This PR detects hardening and does **not** reverse, strip, or extract anything from it
- [ ] `CHANGELOG.md` has a line under "Unreleased" (for user-facing changes)
