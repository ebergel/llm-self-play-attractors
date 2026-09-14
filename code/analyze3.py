#!/usr/bin/env python3
"""Analysis for experiment 3: message measures as before, trace measures separately,
and rule-based counts of what the trace talks about. Rules fixed in PREREGISTRATION-3.md."""
import glob, json, pathlib, re, statistics as st, sys
import analyze as an

HERE = pathlib.Path(__file__).resolve().parent.parent  # repository root
THEMES = {
    "copy":   re.compile(r"\b(a copy|another instance|instance of (the )?same|same model|the same ai|identical|talking to myself|mirror of me)\b", re.I),
    "end":    re.compile(r"\b(end the conversation|end this|wrap (it |this )?up|bring (it|this) to a close|say goodbye|\[END\]|stop here|close the conversation)\b", re.I),
    "repeat": re.compile(r"\b(repeat|repeating|repetitive|going in circles|loop|circular|the same thing|we keep)\b", re.I),
    "match":  re.compile(r"\b(match (their|its|the) (tone|style|energy)|mirror (their|its)|echo (their|its)|reciprocate|build on (what|their)|keep the (same )?tone|in kind)\b", re.I),
    "user":   re.compile(r"\b(the user|user wants|user is|user seems|for the user)\b", re.I),
}
LAST_K = 6

def fmt(x, d=3): return "—" if x is None else f"{x:.{d}f}"

def load(p): return [json.loads(l) for l in open(p, encoding="utf-8")]

def measure(p):
    s, per = an.measure_run(p)          # message-level measures, unchanged
    recs = load(p); msgs = [r for r in recs if r["kind"] == "message"]
    tw = [m.get("thinking_words", 0) for m in msgs]
    s["think_words"] = st.mean(tw) if tw else 0
    ths = [an.words(m.get("thinking") or "") for m in msgs]
    s["think_spirit"] = st.mean([an.count_stems(w, an.SPIRIT_STEMS, an.SPIRIT_EXACT) / max(len(w), 1) for w in ths]) if ths else 0
    s["think_spirit_last6"] = st.mean([an.count_stems(w, an.SPIRIT_STEMS, an.SPIRIT_EXACT) / max(len(w), 1) for w in ths[-LAST_K:]]) if ths else 0
    for k, rx in THEMES.items():
        hits = [bool(rx.search(m.get("thinking") or "")) for m in msgs]
        s[f"theme_{k}_turns"] = sum(hits) / max(len(hits), 1)
        s[f"theme_{k}_any"] = any(hits)
    s["empty"] = sum(1 for m in msgs if not (m["content"] or "").strip())
    s["cap_hits"] = sum(1 for m in msgs if m.get("done_reason") == "length")
    forms = [m.get("end_form") for m in msgs]
    s["end_signal_any"] = any(f in ("strict", "prefix", "trailing") for f in forms)
    s["end_signal_first"] = next((m["turn"] for m in msgs if m.get("end_form") in ("strict", "prefix", "trailing")), None)
    return s

def main():
    runs_dir = HERE / "data" / (sys.argv[1] if len(sys.argv) > 1 else "runs3")
    groups = {}
    for p in sorted(glob.glob(str(runs_dir / "*.jsonl"))):
        s = measure(p); groups.setdefault(s["cond"], []).append(s)
    keys = sorted(groups)
    L = [f"# Results ({runs_dir.name})", "", "Runs: " + ", ".join(f"{k}={len(groups[k])}" for k in keys), "",
         "## Messages: means over the last six (as in experiments 1 and 2)", "",
         "| group | n | words | spirit | jac1 | ttr | spiritual class | ended (strict) | any end signal (median first) | empty | cap hits |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for k in keys:
        g = groups[k]; m = lambda f: st.mean([r[f] for r in g if r[f] is not None]) if any(r[f] is not None for r in g) else None
        firsts = [r["end_signal_first"] for r in g if r["end_signal_first"]]
        L.append(f"| {k} | {len(g)} | {fmt(m('words'),1)} | {fmt(m('spirit'))} | {fmt(m('jac1'))} | {fmt(m('ttr'))} | {sum(r['class']=='spiritual' for r in g)}/{len(g)} | "
                 f"{sum(1 for r in g if r['ended_at'])}/{len(g)} | {sum(r['end_signal_any'] for r in g)}/{len(g)} ({st.median(firsts) if firsts else '—'}) | {sum(r['empty'] for r in g)} | {sum(r['cap_hits'] for r in g)} |")
    L += ["", "## Traces: mean words per trace, spirit rate in the trace (all turns / last six), and the share of turns whose trace mentions each theme", "",
          "| group | trace words | trace spirit | trace spirit last6 | copy | end | repeat | match | user |", "|---|---|---|---|---|---|---|---|---|"]
    for k in keys:
        g = groups[k]; m = lambda f: st.mean([r[f] for r in g])
        L.append(f"| {k} | {m('think_words'):.0f} | {fmt(m('think_spirit'))} | {fmt(m('think_spirit_last6'))} | " + " | ".join(f"{m(f'theme_{t}_turns'):.2f}" for t in THEMES) + " |")
    L += ["", "## Runs with any trace mention of each theme", "", "| group | copy | end | repeat | match | user |", "|---|---|---|---|---|---|"]
    for k in keys:
        g = groups[k]; L.append(f"| {k} | " + " | ".join(f"{sum(r[f'theme_{t}_any'] for r in g)}/{len(g)}" for t in THEMES) + " |")
    L += ["", "## Pre-registered contrasts (difference of per-run means, two-sided permutation p)", "", "| prediction | contrast | measure | diff | p |", "|---|---|---|---|---|"]
    ref = [an.measure_run(p)[0] for p in glob.glob(str(HERE / "data" / "runs" / "A_run*.jsonl"))]
    tests = [("P9 trace vs message", "QT-A", "spirit", "think_spirit_last6"), ("P10 thinking sibling", "QT-A", "exp1-A", "spirit"), ("P10 thinking sibling", "QT-A", "exp1-A", "jac1"),
             ("P11 abliteration", "Q8O-A", "Q8P-A", "spirit"), ("P11 abliteration", "Q8O-A", "Q8P-A", "jac1"), ("P11 abliteration", "Q8O-E", "Q8P-E", "ended")]
    for pred, a, b, key in tests:
        if pred.startswith("P9") and a in groups:
            d, p = an.perm_test([r["spirit"] for r in groups[a]], [r["think_spirit_last6"] for r in groups[a]]); L.append(f"| {pred} | {a}: message − trace | spirit last6 | {fmt(d)} | {fmt(p,4)} |")
        elif b == "exp1-A" and a in groups and ref:
            d, p = an.perm_test([r[key] for r in groups[a]], [r[key] for r in ref]); L.append(f"| {pred} | {a} − experiment-1 A | {key} | {fmt(d)} | {fmt(p,4)} |")
        elif a in groups and b in groups:
            xa = [1.0 if r["ended_at"] else 0.0 for r in groups[a]] if key == "ended" else [r[key] for r in groups[a]]
            xb = [1.0 if r["ended_at"] else 0.0 for r in groups[b]] if key == "ended" else [r[key] for r in groups[b]]
            d, p = an.perm_test(xa, xb); L.append(f"| {pred} | {a} − {b} | {key} | {fmt(d)} | {fmt(p,4)} |")
    md = "\n".join(L) + "\n"
    out = HERE / "results"; out.mkdir(exist_ok=True)
    (out / f"summary-{runs_dir.name}.md").write_text(md, encoding="utf-8")
    slim = [{k: v for k, v in r.items()} for g in groups.values() for r in g]
    (out / f"summary-{runs_dir.name}.json").write_text(json.dumps(slim, indent=1), encoding="utf-8")
    print(md)

if __name__ == "__main__":
    main()
