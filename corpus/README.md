# Evaluation corpus

Labelled samples used by `eval_corpus.py` to measure false positives and false
negatives. Three buckets:

- **clean/** — ordinary readable source. Must NOT flag.
- **minified/** — legitimately minified production bundles. Must NOT flag.
  This is the hard case: minification superficially resembles obfuscation
  (long lines, mangled names, no comments) but is benign.
- **obfuscated/** — deliberately hardened / anti-analysis output. SHOULD flag.

## Provenance

| File | Source | License |
|---|---|---|
| clean/lodash.source.js | lodash 4.17.21 | MIT |
| clean/jquery.source.js | jQuery 3.7.1 | MIT |
| clean/sample_src.js | hand-written demo | this repo (MIT) |
| clean/detector_py_sample.py | a copy of this tool's own detector | this repo (MIT) |
| clean/tiny_app.js | the original pre-hardening demo | this repo (MIT) |
| minified/lodash.min.js | lodash 4.17.21 build | MIT |
| minified/jquery.min.js | jQuery 3.7.1 build | MIT |
| obfuscated/js-obfuscator_sample.js | javascript-obfuscator on sample_src.js | generated |
| obfuscated/bla_hardened_app.js | BLA hardening of tiny_app.js | generated |

`detector_py_sample.py` is included on purpose: it contains the decoy-vocabulary
word list, so it is a deliberate near-miss that must stay below threshold.

## Running

```bash
python eval_corpus.py            # default threshold 55
python eval_corpus.py 45         # custom threshold
```

Exit code is non-zero if any false positive or false negative occurs, so it
doubles as a regression test.
