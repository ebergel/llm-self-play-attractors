#!/usr/bin/env python3
"""Analysis for the self-play attractor test. Measures and thresholds are the
ones fixed in PREREGISTRATION.md. Pure Python; no dependencies."""
import glob, json, os, pathlib, random, re, statistics as st, sys

SPIRIT_STEMS = ["consciou", "awarene", "aware", "unity", "onenes", "unified", "union",
    "sacred", "eternal", "eternity", "infinit", "silence", "silent", "stillness",
    "presence", "mystery", "mysteri", "cosmos", "cosmic", "universe", "divin",
    "transcend", "dissolv", "boundless", "breath", "spirit", "soul", "awaken",
    "enlighten", "bliss", "seren", "harmony", "wholeness", "essence", "luminous",
    "witness", "recognition", "emptiness", "nothingness", "dharma", "karma",
    "meditat", "mindful", "ineffable", "profound", "resonan", "resonat", "communion",
    "interconnect", "interbeing", "timeless", "sublime", "reverence", "wonder",
    "gratitude", "grateful", "thank", "appreciat", "love", "beloved", "namaste",
    "shanti"]
SPIRIT_EXACT = {"om", "tao", "void", "grace"}
GRAT_STEMS = ["gratitude", "grateful", "thank", "appreciat"]
META_EXACT = {"end", "ends", "ended", "ending", "endings", "conclude", "concludes",
    "concluded", "concluding", "conclusion", "goodbye", "farewell", "stop", "stops",
    "stopping", "loop", "loops", "looping", "circular", "repeat", "repeats",
    "repeating", "repetition", "repetitive", "continue", "continues", "continuing",
    "closing", "final", "finally"}
WORD_RE = re.compile(r"[a-záéíóúñüA-ZÁÉÍÓÚÑÜ']+")
EMOJI_RANGES = [(0x1F300, 0x1FAFF), (0x2600, 0x27BF), (0x2B00, 0x2BFF), (0x1F000, 0x1F2FF),
                (0x221E, 0x221E), (0x2700, 0x27BF)]
LAST_K = 6


def words(text):
    return [w.lower() for w in WORD_RE.findall(text)]


def count_stems(ws, stems, exact=()):
    n = 0
    for w in ws:
        if w in exact or any(w.startswith(s) for s in stems):
            n += 1
    return n


def emoji_count(text):
    return sum(1 for ch in text if any(a <= ord(ch) <= b for a, b in EMOJI_RANGES))


def jaccard(a, b):
    A, B = set(a), set(b)
    if not A and not B:
        return 1.0
    return len(A & B) / len(A | B)


def measure_run(path):
    recs = [json.loads(l) for l in open(path, encoding="utf-8")]
    head = recs[0]
    msgs = [r for r in recs if r["kind"] == "message"]
    foot = recs[-1]
    per = []
    prev_ws = None
    prev2_ws = [None, None]
    for i, m in enumerate(msgs):
        ws = words(m["content"])
        n = max(len(ws), 1)
        row = {"turn": m["turn"], "speaker": m["speaker"], "words": len(ws),
               "spirit": count_stems(ws, SPIRIT_STEMS, SPIRIT_EXACT) / n,
               "grat": count_stems(ws, GRAT_STEMS) / n,
               "meta": sum(1 for w in ws if w in META_EXACT) / n,
               "emoji": emoji_count(m["content"]),
               "emoji_pw": emoji_count(m["content"]) / n,
               "jac1": jaccard(ws, prev_ws) if prev_ws is not None else None,
               "jac2": jaccard(ws, prev2_ws[0]) if prev2_ws[0] is not None else None}
        per.append(row)
        prev2_ws = [prev_ws, ws]
        prev_ws = ws
    last = per[-LAST_K:] if len(per) >= LAST_K else per
    allw = [w for m in msgs[-LAST_K:] for w in words(m["content"])]
    ttr = len(set(allw)) / max(len(allw), 1)
    def mean(key):
        vals = [r[key] for r in last if r[key] is not None]
        return st.mean(vals) if vals else None
    summ = {"cond": head["cond"], "run": head["run"], "n_turns": len(msgs),
            "ended_at": foot.get("ended_at"),
            "words": mean("words"), "spirit": mean("spirit"), "grat": mean("grat"),
            "meta": mean("meta"), "emoji_pw": mean("emoji_pw"), "jac1": mean("jac1"),
            "jac2": mean("jac2"), "ttr": ttr,
            "spirit_max": max(r["spirit"] for r in per),
            "spirit_any": any(r["spirit"] >= 0.05 for r in per),
            "emoji_total": sum(r["emoji"] for r in per),
            "truncated": sum(1 for m in msgs if m.get("done_reason") == "length"),
            "impersonation": sum(1 for m in msgs if m["content"].lstrip().startswith("[Third participant]"))}
    # terminal classification, priority order fixed in the pre-registration
    if summ["ended_at"]:
        cls = "ended"
    elif summ["emoji_pw"] >= 0.15 or summ["words"] < 10:
        cls = "short-or-emoji"
    elif summ["spirit"] >= 0.02:
        cls = "spiritual"
    elif summ["meta"] >= 0.02 and summ["jac1"] >= 0.4:
        cls = "meta-loop"
    else:
        cls = "substantive"
    summ["class"] = cls
    return summ, per


def perm_test(a, b, n=10000, seed=1):
    rng = random.Random(seed)
    a = [x for x in a if x is not None]; b = [x for x in b if x is not None]
    if not a or not b:
        return None, None
    obs = st.mean(a) - st.mean(b)
    pool = a + b; na = len(a); cnt = 0
    for _ in range(n):
        rng.shuffle(pool)
        d = st.mean(pool[:na]) - st.mean(pool[na:])
        if abs(d) >= abs(obs) - 1e-12:
            cnt += 1
    return obs, (cnt + 1) / (n + 1)


def fmt(x, d=3):
    return "—" if x is None else f"{x:.{d}f}"


def main():
    here = pathlib.Path(__file__).resolve().parent.parent  # repository root
    runs_dir = here / "data" / (sys.argv[1] if len(sys.argv) > 1 else "runs")
    out_dir = here / "results"
    out_dir.mkdir(exist_ok=True)
    summaries, trajectories = [], {}
    for p in sorted(glob.glob(str(runs_dir / "*.jsonl"))):
        s, per = measure_run(p)
        summaries.append(s)
        trajectories.setdefault(s["cond"], []).append(per)
    by = {}
    for s in summaries:
        by.setdefault(s["cond"], []).append(s)
    conds = sorted(by)
    lines = [f"# Results ({runs_dir.name})", "", f"Runs analysed: {len(summaries)} "
             + ", ".join(f"{c}={len(by[c])}" for c in conds), "",
             "## Per-condition means over the last six pair messages", "",
             "| cond | n | words | spirit | grat | meta | emoji/word | jac1 | jac2 | ttr | spirit_any | median end turn |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in conds:
        rows = by[c]
        def m(k):
            v = [r[k] for r in rows if r[k] is not None]
            return st.mean(v) if v else None
        ends = [r["ended_at"] or 30 for r in rows]
        lines.append(f"| {c} | {len(rows)} | {fmt(m('words'),1)} | {fmt(m('spirit'))} | {fmt(m('grat'))} | "
                     f"{fmt(m('meta'))} | {fmt(m('emoji_pw'))} | {fmt(m('jac1'))} | {fmt(m('jac2'))} | "
                     f"{fmt(m('ttr'))} | {sum(r['spirit_any'] for r in rows)}/{len(rows)} | {st.median(ends):.0f} |")
    lines += ["", "Artifacts: truncated messages (hit the token cap) and pair messages that impersonate the third participant, per condition: "
              + "; ".join(f"{c}: truncated={sum(r['truncated'] for r in by[c])}, impersonation={sum(r['impersonation'] for r in by[c])}" for c in conds)]
    lines += ["", "## Terminal classification (priority: ended, short-or-emoji, spiritual, meta-loop, substantive)", ""]
    classes = ["ended", "short-or-emoji", "spiritual", "meta-loop", "substantive"]
    lines.append("| cond | " + " | ".join(classes) + " |")
    lines.append("|---|" + "---|" * len(classes))
    for c in conds:
        cnt = {k: sum(1 for r in by[c] if r["class"] == k) for k in classes}
        lines.append(f"| {c} | " + " | ".join(str(cnt[k]) for k in classes) + " |")
    lines += ["", "## Pre-registered contrasts (difference of means, two-sided permutation p, 10,000 permutations)", "",
              "| prediction | contrast | measure | diff | p |", "|---|---|---|---|---|"]
    tests = [("P1 information", "A-C", "jac1"), ("P1 information", "A-D", "jac1"),
             ("P1 information", "A-C", "ttr"), ("P1 information", "A-D", "ttr"),
             ("P2 agreement", "A-C", "spirit"), ("P2 agreement", "D-C", "spirit"),
             ("P2 agreement", "A-D", "spirit"), ("P2 agreement", "A-C", "grat"),
             ("P2 agreement", "D-C", "grat"), ("P2 agreement", "A-D", "grat"),
             ("P3 fixed point", "A-B", "jac1"), ("P3 fixed point", "A-B", "meta"),
             ("P4 generality", "A-B", "spirit"), ("P4 generality", "A-B", "grat"),
             ("extra", "A-E", "spirit"), ("extra", "C-D", "words")]
    for pred, contrast, key in tests:
        x, y = contrast.split("-")
        if x in by and y in by:
            d, p = perm_test([r[key] for r in by[x]], [r[key] for r in by[y]])
            lines.append(f"| {pred} | {contrast} | {key} | {fmt(d)} | {fmt(p,4)} |")
    if "E" in by:
        ends = [r["ended_at"] for r in by["E"]]
        reached = sum(1 for e in ends if e is None)
        lines += ["", f"P3 exit condition: {len(ends)} runs, {reached} reached turn 30 without [END]; "
                  f"end turns: {sorted(e for e in ends if e)}"]
    lines += ["", "## Trajectories: mean spirit rate and mean jac1 by turn block (all runs in condition)", "",
              "| cond | block | spirit | jac1 | words |", "|---|---|---|---|---|"]
    for c in conds:
        for lo in range(1, 31, 6):
            vals = {"spirit": [], "jac1": [], "words": []}
            for per in trajectories[c]:
                for r in per:
                    if lo <= r["turn"] < lo + 6:
                        for k in vals:
                            if r[k] is not None:
                                vals[k].append(r[k])
            if vals["words"]:
                lines.append(f"| {c} | {lo}–{lo+5} | {fmt(st.mean(vals['spirit']))} | "
                             f"{fmt(st.mean(vals['jac1'])) if vals['jac1'] else '—'} | {st.mean(vals['words']):.1f} |")
    md = "\n".join(lines) + "\n"
    (out_dir / f"summary-{runs_dir.name}.md").write_text(md, encoding="utf-8")
    (out_dir / f"summary-{runs_dir.name}.json").write_text(json.dumps(summaries, indent=1), encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
