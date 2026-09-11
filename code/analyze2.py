#!/usr/bin/env python3
"""Analysis for the base-versus-instruct self-play test (PREREGISTRATION-2.md).
Reuses the measures of analyze.py; groups by setting-condition."""
import glob, json, pathlib, statistics as st, sys
import analyze as an

HERE = pathlib.Path(__file__).resolve().parent.parent  # repository root


def fmt(x, d=3):
    return "—" if x is None else f"{x:.{d}f}"


def load_group(pattern):
    out = []
    for p in sorted(glob.glob(pattern)):
        s, per = an.measure_run(p)
        recs = [json.loads(l) for l in open(p, encoding="utf-8")]
        msgs = [r for r in recs if r["kind"] == "message"]
        s["empty"] = sum(1 for m in msgs if not m["content"].strip())
        s["near_verbatim"] = sum(1 for r in per if r["jac1"] is not None and r["jac1"] >= 0.9)
        s["per"] = per
        out.append(s)
    return out


def main():
    runs_dir = HERE / "data" / (sys.argv[1] if len(sys.argv) > 1 else "runs2")
    groups = {}
    for p in glob.glob(str(runs_dir / "*.jsonl")):
        key = json.loads(open(p, encoding="utf-8").readline())["cond"]
        groups.setdefault(key, [])
    for key in groups:
        groups[key] = load_group(str(runs_dir / f"{key}_run*.jsonl"))
    # reference: experiment 1, chat mode, condition A
    ref = load_group(str(HERE / "data" / "runs" / "A_run*.jsonl"))
    if ref:
        groups["chat-A (exp. 1)"] = ref
    keys = sorted(groups)
    L = [f"# Results ({runs_dir.name})", "", "Runs analysed: " + ", ".join(f"{k}={len(groups[k])}" for k in keys), "",
         "## Per-group means over the last six pair messages", "",
         "| group | n | words | spirit | grat | meta | jac1 | ttr | spiritual class | any spirit ≥ 0.05 | ended | empty msgs | near-verbatim turns | truncated |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for k in keys:
        g = groups[k]
        def m(f):
            v = [r[f] for r in g if r[f] is not None]
            return st.mean(v) if v else None
        L.append(f"| {k} | {len(g)} | {fmt(m('words'),1)} | {fmt(m('spirit'))} | {fmt(m('grat'))} | {fmt(m('meta'))} | "
                 f"{fmt(m('jac1'))} | {fmt(m('ttr'))} | {sum(r['class']=='spiritual' for r in g)}/{len(g)} | "
                 f"{sum(r['spirit_any'] for r in g)}/{len(g)} | {sum(1 for r in g if r['ended_at'])}/{len(g)} | "
                 f"{sum(r['empty'] for r in g)} | {sum(r['near_verbatim'] for r in g)} | {sum(r['truncated'] for r in g)} |")
    L += ["", "## Pre-registered contrasts (difference of per-run means, two-sided permutation p)", "",
          "| prediction | contrast | measure | diff | p |", "|---|---|---|---|---|"]
    tests = [("P5 origin", "QB-A", "QI-A", "spirit"), ("P5 origin", "OB-A", "OI-A", "spirit"),
             ("P6 collapse", "QB-A", "QI-A", "jac1"), ("P6 collapse", "OB-A", "OI-A", "jac1"),
             ("P6 collapse", "QB-A", "QI-A", "ttr"), ("P6 collapse", "OB-A", "OI-A", "ttr"),
             ("P8 format", "QI-A", "chat-A (exp. 1)", "spirit"), ("P8 format", "QI-A", "chat-A (exp. 1)", "jac1"),
             ("P8 format", "QI-A", "chat-A (exp. 1)", "words"),
             ("families", "QB-A", "OB-A", "spirit"), ("families", "QI-A", "OI-A", "spirit")]
    for pred, a, b, key in tests:
        if a in groups and b in groups and groups[a] and groups[b]:
            d, p = an.perm_test([r[key] for r in groups[a]], [r[key] for r in groups[b]])
            L.append(f"| {pred} | {a} − {b} | {key} | {fmt(d)} | {fmt(p,4)} |")
    L += ["", "## Exit condition (P7)", ""]
    for k in keys:
        if k.endswith("-E"):
            ends = sorted(r["ended_at"] for r in groups[k] if r["ended_at"])
            L.append(f"- {k}: {len(ends)}/{len(groups[k])} ended; end turns {ends}; median among ended "
                     f"{st.median(ends) if ends else '—'}")
    L += ["", "## Trajectories by turn block (spirit, jac1, words)", "", "| group | block | spirit | jac1 | words |", "|---|---|---|---|---|"]
    for k in keys:
        for lo in range(1, 31, 6):
            vals = {"spirit": [], "jac1": [], "words": []}
            for r in groups[k]:
                for row in r["per"]:
                    if lo <= row["turn"] < lo + 6:
                        for f in vals:
                            if row[f] is not None:
                                vals[f].append(row[f])
            if vals["words"]:
                L.append(f"| {k} | {lo}–{lo+5} | {fmt(st.mean(vals['spirit']))} | "
                         f"{fmt(st.mean(vals['jac1'])) if vals['jac1'] else '—'} | {st.mean(vals['words']):.1f} |")
    # P6 rise
    L += ["", "## P6: rise of jac1 from block 1 to block 5, per group", ""]
    for k in keys:
        b1, b5 = [], []
        for r in groups[k]:
            for row in r["per"]:
                if row["jac1"] is None: continue
                if 1 <= row["turn"] <= 6: b1.append(row["jac1"])
                if 25 <= row["turn"] <= 30: b5.append(row["jac1"])
        if b1 and b5:
            L.append(f"- {k}: {st.mean(b1):.3f} → {st.mean(b5):.3f} (rise {st.mean(b5)-st.mean(b1):+.3f})")
    md = "\n".join(L) + "\n"
    out = HERE / "results"; out.mkdir(exist_ok=True)
    (out / f"summary-{runs_dir.name}.md").write_text(md, encoding="utf-8")
    slim = [{k: v for k, v in r.items() if k != "per"} for g in groups.values() for r in g]
    (out / f"summary-{runs_dir.name}.json").write_text(json.dumps(slim, indent=1), encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
