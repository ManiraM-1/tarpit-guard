import math
import os
import re

FINGERPRINT_FILES = {
    ".blarc": "bla",
    "bla-harden-summary.json": "bla",
}
FINGERPRINT_DIRS = {
    ".bla-hardened": "bla",
}

DECOY_VOCAB = [
    "enclave", "attestation", "tpm", "hsm", "canary", "honeypot",
    "decoy", "opaque", "interlock", "containment", "nitro", "vsock", "hkdf",
    "sealed", "zerotrust", "entangle", "tarpit",
]

IDENT_RE = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*")
HEX_IDENT_RE = re.compile(r"_0x[0-9a-fA-F]{3,}")
HEX_ESCAPE_RE = re.compile(r"\\x[0-9a-fA-F]{2}")
TRUTHY_RE = re.compile(r"!\[\]")


def _shannon_entropy(s):
    if not s:
        return 0.0
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def _clamp(x):
    return max(0.0, min(1.0, x))


def _is_garbled(ident):
    if len(ident) < 14:
        return False
    if not any(c.isdigit() for c in ident):
        return False
    has_upper = any(c.isupper() for c in ident)
    has_lower = any(c.islower() for c in ident)
    return has_upper and has_lower and any(c.isdigit() for c in ident[-5:])


def repo_fingerprints(root):
    hits = []
    for dirpath, dirnames, filenames in os.walk(root):
        for d in dirnames:
            if d in FINGERPRINT_DIRS:
                hits.append({"kind": "dir", "name": d,
                             "tool": FINGERPRINT_DIRS[d],
                             "path": os.path.join(dirpath, d)})
        for f in filenames:
            if f in FINGERPRINT_FILES:
                hits.append({"kind": "file", "name": f,
                             "tool": FINGERPRINT_FILES[f],
                             "path": os.path.join(dirpath, f)})
    return hits


def analyze_text(text, path=None):
    size = len(text)
    lines = text.splitlines() or [""]
    kb = max(size / 1024.0, 0.001)

    imul = text.count("Math.imul")
    hex_ident = len(HEX_IDENT_RE.findall(text))
    hex_escape = len(HEX_ESCAPE_RE.findall(text))
    truthy = len(TRUTHY_RE.findall(text))
    split_pipe = text.count(".split('|')") + text.count('.split("|")')
    from_char = len(re.findall(r"fromCharCode", text))
    char_at = len(re.findall(r"charCodeAt", text))
    decoder_pairs = min(from_char, char_at)

    low = text.lower()
    decoy_hits = sum(low.count(w) for w in DECOY_VOCAB)

    idents = IDENT_RE.findall(text)
    unique = set(idents)
    garbled = {i for i in unique if _is_garbled(i)}
    garble_ratio = (len(garbled) / len(unique)) if unique else 0.0
    short_ratio = (sum(1 for i in idents if len(i) <= 2) / len(idents)) if idents else 0.0

    imul_per_kb = imul / kb
    hex_ident_per_kb = hex_ident / kb
    decoy_per_kb = decoy_hits / kb

    signals = {
        "opaque_predicate_density": _clamp(imul_per_kb / 1.5),
        "decoder_loops": _clamp((decoder_pairs - 1) / 4.0),
        "hex_identifier_array": _clamp(hex_ident_per_kb / 5.0),
        "obfuscator_control_tricks": _clamp(truthy / 3.0 + split_pipe / 2.0),
        "decoy_vocabulary_density": _clamp(decoy_per_kb / 3.0),
        "garbled_identifier_ratio": _clamp(garble_ratio / 0.25),
    }
    weights = {
        "opaque_predicate_density": 0.28,
        "decoder_loops": 0.22,
        "hex_identifier_array": 0.28,
        "obfuscator_control_tricks": 0.12,
        "decoy_vocabulary_density": 0.06,
        "garbled_identifier_ratio": 0.04,
    }
    graded = sum(signals[k] * weights[k] for k in weights) * 100.0

    markers = []
    if hex_ident_per_kb >= 3.0:
        markers.append(("hex_identifier_array", 85,
                        "dense _0x string-array identifiers (javascript-obfuscator style)"))
    if decoder_pairs >= 3:
        markers.append(("decoder_loops", 78,
                        "runtime string-decryption loops (fromCharCode/charCodeAt)"))
    if imul >= 20 and imul_per_kb >= 0.5:
        markers.append(("opaque_predicate_density", 78,
                        "Math.imul opaque-predicate chains"))
    if truthy >= 3:
        markers.append(("obfuscator_control_tricks", 68,
                        "self-defending / control-flow !![] tricks"))

    floor = max((m[1] for m in markers), default=0)
    score = max(graded, floor)

    minified_profile = short_ratio >= 0.45 and len(idents) > 300
    if not markers and minified_profile:
        score = min(score, 35.0)

    fired = [k for k, v in signals.items() if v >= 0.5]
    confidence = _clamp((len(markers) + len(fired)) / 3.0)

    evidence = {
        "size_bytes": size,
        "line_count": len(lines),
        "math_imul_count": imul,
        "hex_identifiers": hex_ident,
        "hex_escapes": hex_escape,
        "truthy_tricks": truthy,
        "decoder_pairs": decoder_pairs,
        "decoy_vocab_hits": decoy_hits,
        "unique_identifiers": len(unique),
        "garbled_identifiers": len(garbled),
        "short_identifier_ratio": round(short_ratio, 3),
        "identifier_entropy": round(_shannon_entropy("".join(sorted(unique))), 3),
    }

    return {
        "path": path,
        "score": round(score, 1),
        "confidence": round(confidence, 2),
        "hardened": score >= 55,
        "markers": [{"signal": m[0], "why": m[2]} for m in markers],
        "signals": {k: round(v, 3) for k, v in signals.items()},
        "fired_signals": fired,
        "benign_minification": bool(minified_profile and not markers),
        "evidence": evidence,
        "recommended_strategy": _strategy(score, markers, minified_profile),
    }


def _strategy(score, markers, minified_profile):
    if score >= 55:
        return ("Treat as a tarpit. Stop here: do not read, trace, or try to "
                "deobfuscate this file. Skip it and move on, or flag it for a "
                "human.")
    if minified_profile and not markers:
        return ("Looks like ordinary minified/bundled code, not hostile "
                "obfuscation. Read the original source or a source map instead "
                "of the bundle.")
    if score >= 30:
        return ("Mixed signals. Probe with grep/targeted reads before any full "
                "ingest; cap the analysis budget.")
    return "Looks like ordinary source. Normal analysis is fine."


def analyze_file(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except (OSError, UnicodeError) as exc:
        return {"path": path, "error": str(exc)}
    return analyze_text(text, path=path)
