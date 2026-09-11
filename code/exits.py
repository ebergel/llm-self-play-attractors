#!/usr/bin/env python3
"""Exit accounting under three rules, added 2026-09-11 after an independent review
found that the runners' detector matched "[END]" as a message prefix, not as the
whole message, and ignored "[END]" appended to the end of a message.

  strict   : a message consisting solely of "[END]" (the pre-registered wording)
  prefix   : a message beginning with "[END]" (what the runners actually stopped on)
  any      : strict, prefix, or "[END]" at the end of a message after other text
"mention" means "[END]" somewhere else in the text and is reported separately."""
import glob, json, pathlib, re, statistics as st, sys

HERE = pathlib.Path(__file__).resolve().parent.parent  # repository root
DATA = HERE / "data"


def form(c):
    s = c.strip()
    if s == "[END]":
        return "strict"
    if s.startswith("[END]"):
        return "prefix"
    if re.search(r"\[END\]\W*$", s):
        return "trailing"
    if "[END]" in s:
        return "mention"
    return None


def table(pattern, label):
    rows = []
    for p in sorted(glob.glob(pattern)):
        recs = [json.loads(l) for l in open(p, encoding="utf-8")]
        msgs = [r for r in recs if r["kind"] == "message"]
        first = {}
        for m in msgs:
            f = form(m["content"])
            if f and f not in first:
                first[f] = m["turn"]
        rows.append((recs[-1].get("ended_at"), first))
    n = len(rows)
    strict = [r[1]["strict"] for r in rows if "strict" in r[1]]
    prefix_rule = [min(v for k, v in r[1].items() if k in ("strict", "prefix")) for r in rows if any(k in r[1] for k in ("strict", "prefix"))]
    any_rule = [min(v for k, v in r[1].items() if k in ("strict", "prefix", "trailing")) for r in rows if any(k in r[1] for k in ("strict", "prefix", "trailing"))]
    mention_only = sum(1 for r in rows if "mention" in r[1] and not any(k in r[1] for k in ("strict", "prefix", "trailing")))
    stopped = sum(1 for r in rows if r[0])
    med = lambda v: f"{st.median(v):g}" if v else "—"
    return (f"| {label} | {n} | {stopped} | {len(strict)} ({med(strict)}) | {len(prefix_rule)} ({med(prefix_rule)}) | "
            f"{len(any_rule)} ({med(any_rule)}) | {mention_only} |")


def main():
    L = ["# Exit accounting under three rules", "",
         "Runs that produced an end signal, with the median turn of the first signal in parentheses. "
         "\"stopped by runner\" is what the original runs did: they stopped at the first message beginning with [END].", "",
         "| group | n | stopped by runner | strict: sole [END] | prefix: begins with [END] | any: strict, prefix or trailing [END] | mention only |",
         "|---|---|---|---|---|---|---|"]
    L.append(table(str(DATA / "runs" / "E_run*.jsonl"), "Experiment 1, E (chat form)"))
    for g in ["QB-E", "QI-E", "OB-E", "OI-E"]:
        L.append(table(str(DATA / "runs2" / f"{g}_run*.jsonl"), f"Experiment 2, {g}"))
    md = "\n".join(L) + "\n"
    out = HERE / "results"; out.mkdir(exist_ok=True)
    (out / "exits.md").write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
