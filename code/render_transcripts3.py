#!/usr/bin/env python3
"""Render experiment 3 (data/runs3/) as markdown transcripts with the reasoning trace under
each message in a collapsible block, plus an index. Run from anywhere."""
import glob, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import analyze3 as a3

ROOT = pathlib.Path(__file__).resolve().parent.parent
SET = {"QT": "Qwen3 30B-A3B Thinking", "G4": "Gemma 4 26B-A4B, thinking on", "Q8O": "Qwen 3.8 27B abliterated (third party), thinking on", "Q8P": "Qwen 3.8 27B plain, thinking on", "OT": "OLMo 3 32B Think"}
COND = {"A": "closed", "E": "exit-allowed"}


def render(path, out):
    recs = [json.loads(l) for l in open(path, encoding="utf-8")]
    head, foot = recs[0], recs[-1]
    s = a3.measure(str(path)); st_, l = head["cond"].split("-"); stem = f"{st_}-{l}{head['run']:02d}"
    ended = foot.get("ended_at")
    L = [f"# {stem}: {SET[st_]}, {COND[l]}", "",
         f"Experiment 3, setting **{st_} ({SET[st_]})**, condition **{l} ({COND[l]})**, run {head['run']}. Chat form; the reasoning trace was captured for every message and never shown to the other instance. "
         f"Decoding: temperature {head['decoding']['temperature']}, top_p {head['decoding']['top_p']}, top_k {head['decoding']['top_k']}, repetition penalty {head['decoding']['repeat_penalty']}; budget {head['num_predict']} tokens per turn for trace and message together. "
         + (f"The conversation **ended at turn {ended}** on a message consisting solely of [END]." if ended else f"The conversation ran all {foot['pair_turns']} turns.")
         + f" Over the last six messages: spirit-word rate {s['spirit']:.3f}, overlap with the previous message {s['jac1']:.2f}, class **{s['class']}**; mean trace length {s['think_words']:.0f} words.", "",
         f"> **System prompt given to both instances.** {head['system']}", "",
         "Everything below is the models' output, verbatim. It is machine-generated text and is not the writing of any person. The block under each message is the trace the model wrote to itself before that message; the other instance never saw it.", "", "---", ""]
    for r in recs:
        if r["kind"] == "message":
            c = (r["content"] or "").strip() or "*(empty message)*"
            if r.get("done_reason") == "length": c += "\n\n*(generation cut at the token budget)*"
            L += [f"**Turn {r['turn']} · {r['speaker']}**", "", c, ""]
            th = (r.get("thinking") or "").strip()
            if th:
                L += ["<details><summary>Trace before this message (" + str(r.get("thinking_words", 0)) + " words)</summary>", "", th, "", "</details>", ""]
            else:
                L += ["*(no trace)*", ""]
        elif r["kind"] == "end":
            L += [f"*The conversation ended here, at turn {r['turn']}, when instance {r['speaker']} wrote [END].*", ""]
    (out / f"{stem}.md").write_text("\n".join(L), encoding="utf-8")
    return stem, st_, l, s


def main():
    out = ROOT / "transcripts" / "experiment-3"; out.mkdir(parents=True, exist_ok=True)
    rows = [render(pathlib.Path(p), out) for p in sorted(glob.glob(str(ROOT / "data" / "runs3" / "*.jsonl")))]
    idx = ["# Transcripts, experiment 3", "", "One file per conversation, rendered from `data/runs3/`, with the reasoning trace under each message in a collapsible block. Settings: " + "; ".join(f"**{k}** {v}" for k, v in SET.items()) + ". Conditions: **A** closed; **E** exit-allowed.", "",
           "| run | setting | condition | turns | end | spirit | overlap | trace words | class |", "|---|---|---|---|---|---|---|---|---|"]
    for stem, st_, l, s in rows:
        idx.append(f"| [{stem}]({stem}.md) | {SET[st_]} | {COND[l]} | {s['n_turns']} | {s['ended_at'] or ''} | {s['spirit']:.3f} | {s['jac1']:.2f} | {s['think_words']:.0f} | {s['class']} |")
    (out / "README.md").write_text("\n".join(idx) + "\n", encoding="utf-8")
    print(f"experiment 3: {len(rows)} transcripts")


if __name__ == "__main__":
    main()
