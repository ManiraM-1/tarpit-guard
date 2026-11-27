import os
import sys

from tarpit_guard.detector import analyze_file

CORPUS = os.path.join(os.path.dirname(__file__), "corpus")
BENIGN = {"clean", "minified"}
HOSTILE = {"obfuscated"}


def run(threshold=55.0):
    rows = []
    for label in sorted(os.listdir(CORPUS)):
        ldir = os.path.join(CORPUS, label)
        if not os.path.isdir(ldir):
            continue
        for fn in sorted(os.listdir(ldir)):
            r = analyze_file(os.path.join(ldir, fn))
            if "error" in r:
                continue
            flagged = r["score"] >= threshold
            should_flag = label in HOSTILE
            if flagged and not should_flag:
                verdict = "FALSE POSITIVE"
            elif not flagged and should_flag:
                verdict = "FALSE NEGATIVE"
            else:
                verdict = "ok"
            rows.append((label, fn, r["score"], r["confidence"], flagged, verdict))

    rows.sort(key=lambda x: (x[0], -x[2]))
    print(f"{'label':<11}{'file':<28}{'score':>7}{'conf':>6}  {'flag':<5} verdict")
    print("-" * 78)
    for label, fn, score, conf, flagged, verdict in rows:
        mark = "" if verdict == "ok" else "  <<<"
        print(f"{label:<11}{fn[:27]:<28}{score:>7.1f}{conf:>6.2f}  "
              f"{'YES' if flagged else 'no':<5} {verdict}{mark}")

    fp = sum(1 for r in rows if r[5] == "FALSE POSITIVE")
    fn = sum(1 for r in rows if r[5] == "FALSE NEGATIVE")
    benign = sum(1 for r in rows if r[0] in BENIGN)
    hostile = sum(1 for r in rows if r[0] in HOSTILE)
    print("-" * 78)
    print(f"threshold={threshold}")
    print(f"benign files: {benign}  false positives: {fp}  "
          f"(FP rate {fp / benign:.0%})" if benign else "")
    print(f"hostile files: {hostile}  false negatives: {fn}  "
          f"(detection {(hostile - fn) / hostile:.0%})" if hostile else "")
    worst_benign = max((r[2] for r in rows if r[0] in BENIGN), default=0)
    best_hostile = min((r[2] for r in rows if r[0] in HOSTILE), default=0)
    print(f"highest benign score: {worst_benign:.1f}   "
          f"lowest hostile score: {best_hostile:.1f}   "
          f"margin: {best_hostile - worst_benign:+.1f}")
    return fp, fn


if __name__ == "__main__":
    t = float(sys.argv[1]) if len(sys.argv) > 1 else 55.0
    fp, fn = run(t)
    sys.exit(1 if (fp or fn) else 0)
