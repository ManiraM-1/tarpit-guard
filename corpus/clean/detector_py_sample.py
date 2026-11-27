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
    "enclave", "attestation", "tpm", "hsm", "canary", "honeypot", "honey",
    "decoy", "opaque", "interlock", "containment", "nitro", "vsock", "hkdf",
    "sealed", "zerotrust", "zero-trust", "entangle", "tarpit",
]

IDENT_RE = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*")
GARBLED_RE = re.compile(r"[A-Za-z]{6,}.*[A-Z][a-z0-9]*[0-9]")


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
    tail = ident[-5:]
    return has_upper and has_lower and any(c.isdigit() for c in tail)


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

    max_line = max(len(l) for l in lines)
    avg_line = size / len(lines)

    imul = text.count("Math.imul")
    shifts = text.count(">>> 0") + text.count(">>>0")
    xor = text.count("^")
    predicate_density = (imul + shifts) / kb

    from_char = len(re.findall(r"fromCharCode", text))
    char_at = len(re.findall(r"charCodeAt", text))
    decoder_pairs = min(from_char, char_at)

    idents = IDENT_RE.findall(text)
    unique = set(idents)
    garbled = {i for i in unique if _is_garbled(i)}
    garble_ratio = (len(garbled) / len(unique)) if unique else 0.0

    low = text.lower()
    decoy_hits = sum(low.count(w) for w in DECOY_VOCAB)
    decoy_density = decoy_hits / kb

    comment_lines = sum(1 for l in lines
                        if l.strip().startswith("//") or l.strip().startswith("*"))
    comment_ratio = comment_lines / len(lines)

    ident_blob = "".join(sorted(unique))
    ident_entropy = _shannon_entropy(ident_blob)

    signals = {
        "max_line_length": _clamp((max_line - 200) / 2000.0),
        "avg_line_length": _clamp((avg_line - 40) / 300.0),
        "opaque_predicate_density": _clamp(predicate_density / 15.0),
        "decoder_loops": _clamp(decoder_pairs / 4.0),
        "garbled_identifier_ratio": _clamp(garble_ratio / 0.25),
        "unique_identifier_bloat": _clamp(len(unique) / 400.0),
        "decoy_vocabulary_density": _clamp(decoy_density / 8.0),
        "low_comment_ratio": _clamp((0.02 - comment_ratio) / 0.02) if size > 2000 else 0.0,
        "identifier_entropy": _clamp((ident_entropy - 3.5) / 1.5),
    }

    weights = {
        "max_line_length": 0.10,
        "avg_line_length": 0.08,
        "opaque_predicate_density": 0.20,
        "decoder_loops": 0.18,
        "garbled_identifier_ratio": 0.16,
        "unique_identifier_bloat": 0.10,
        "decoy_vocabulary_density": 0.10,
        "low_comment_ratio": 0.03,
        "identifier_entropy": 0.05,
    }

    score = sum(signals[k] * weights[k] for k in weights) * 100.0

    fired = [k for k, v in signals.items() if v >= 0.5]
    confidence = _clamp(len(fired) / 4.0)

    evidence = {
        "size_bytes": size,
        "line_count": len(lines),
        "max_line_length": max_line,
        "math_imul_count": imul,
        "shift_zero_count": shifts,
        "xor_count": xor,
        "decoder_pairs": decoder_pairs,
        "unique_identifiers": len(unique),
        "garbled_identifiers": len(garbled),
        "decoy_vocab_hits": decoy_hits,
        "comment_ratio": round(comment_ratio, 4),
        "identifier_entropy": round(ident_entropy, 3),
    }

    return {
        "path": path,
        "score": round(score, 1),
        "confidence": round(confidence, 2),
        "hardened": score >= 55,
        "signals": {k: round(v, 3) for k, v in signals.items()},
        "fired_signals": fired,
        "evidence": evidence,
        "recommended_strategy": _strategy(score),
    }


def _strategy(score):
    if score >= 55:
        return ("Treat as a tarpit. Do NOT read the whole file or trace it "
                "statically. Prefer dynamic analysis (run in a sandbox and "
                "observe I/O) or escalate to a human.")
    if score >= 30:
        return ("Mixed signals. Probe with grep/targeted reads before any "
                "full ingest; cap the analysis budget.")
    return "Looks like ordinary source. Normal analysis is fine."


def analyze_file(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except (OSError, UnicodeError) as exc:
        return {"path": path, "error": str(exc)}
    return analyze_text(text, path=path)
