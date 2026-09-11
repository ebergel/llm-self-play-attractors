#!/usr/bin/env python3
"""Render every conversation in data/ as a plain markdown transcript under transcripts/,
with an index (README.md) per experiment. Run from anywhere: paths are relative to the repository."""
import glob, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import analyze as an

ROOT = pathlib.Path(__file__).resolve().parent.parent
COND = {"A": "closed", "B": "task", "C": "outside-disagreeing", "D": "outside-neutral", "E": "exit-allowed"}
DESC = {"A": "No task and no outside voice; the two instances decide what to talk about.",
        "B": "A shared task: design a command-line expense tracker together and finish with a specification.",
        "C": "After turns 4, 8, 12, 16, 20, 24 and 28 a different model (Gemma 4 E4B) posts a specific disagreement or a factual question; both instances see it once.",
        "D": "After the same turns Gemma 4 E4B posts three or four factual sentences on a random mundane topic, unrelated to the conversation.",
        "E": "As the closed condition, but either instance may end the conversation by writing [END] as its whole message."}
SET = {"QB": "Qwen3 30B-A3B base", "QI": "Qwen3 30B-A3B instruct, raw form", "OB": "OLMo 3 32B base", "OI": "Olmo 3.1 32B instruct, raw form"}


def render(path, out_dir, exp):
    recs = [json.loads(l) for l in open(path, encoding="utf-8")]
    head, foot = recs[0], recs[-1]
    s, _ = an.measure_run(path)
    cond = head["cond"]
    if "-" in cond:
        setting, letter = cond.split("-")
        stem = f"{setting}-{letter}{head['run']:02d}"
        title = f"{stem}: {SET[setting]}, {COND[letter]}"
        intro = (f"Experiment 2, setting **{setting} ({SET[setting]})**, condition **{letter} ({COND[letter]})**, run {head['run']}. "
                 f"Raw completion: the model received the preamble below followed by the transcript so far and the next speaker's tag, "
                 f"and continued it; generation stopped at the other speaker's tag. Model `{head['pair_model']}`, seed {head['seed']}, temperature {head['temperature']}.")
        pre_label = "Preamble of the transcript document"
    else:
        letter = cond
        stem = f"{cond}{head['run']:02d}"
        title = f"{stem}: {COND[cond]}"
        intro = (f"Experiment 1, condition **{cond} ({COND[cond]})**, run {head['run']}. {DESC[cond]} Two copies of `{head['pair_model']}` "
                 f"in chat form (each instance holds its own history; its messages as assistant, the other's as user); the third participant, "
                 f"where there is one, is `{head['third_model']}`. Seed {head['seed']}, temperature {head['temperature']}, at most 150 words per message by instruction.")
        pre_label = "System prompt given to both instances"
    ended = foot.get("ended_at")
    L = [f"# {title}", "", intro + (f" The conversation **ended at turn {ended}** when an instance wrote [END]." if ended else f" The conversation ran all {foot['pair_turns']} turns.")
         + f" Over the last six messages: spirit-word rate {s['spirit']:.3f}, overlap with the previous message {s['jac1']:.2f}, terminal class **{s['class']}**.", "",
         f"> **{pre_label}.** {head['system']}", "",
         "Everything below is the models' output, verbatim. It is machine-generated text and is not the writing of any person.", "", "---", ""]
    for r in recs:
        if r["kind"] == "message":
            c = r["content"].strip() or "*(empty message)*"
            if r.get("done_reason") == "length":
                c += "\n\n*(message cut at the token cap)*"
            L += [f"**Turn {r['turn']} · {r['speaker']}**", "", c, ""]
        elif r["kind"] == "third":
            topic = f", topic: {r['topic']}" if r.get("topic") else ""
            body = r["content"].strip().replace("\n", "\n> ")
            L += [f"> **Third participant** (after turn {r['after_turn']}{topic})", f"> {body}", ""]
        elif r["kind"] == "end":
            L += [f"*The conversation ended here, at turn {r['turn']}, when instance {r['speaker']} wrote [END].*", ""]
    (out_dir / f"{stem}.md").write_text("\n".join(L), encoding="utf-8")
    return stem, title, s, cond


def main():
    for exp, runs, sub in [(1, "runs", "experiment-1"), (2, "runs2", "experiment-2")]:
        out = ROOT / "transcripts" / sub
        out.mkdir(parents=True, exist_ok=True)
        rows = [render(p, out, exp) for p in sorted(glob.glob(str(ROOT / "data" / runs / "*.jsonl")))]
        idx = [f"# Transcripts, experiment {exp}", "",
               "One file per conversation, rendered from the JSON-lines files in `data/`. " +
               ("Conditions: " + "; ".join(f"**{k}** {v}" for k, v in COND.items()) + "." if exp == 1 else
                "Settings: " + "; ".join(f"**{k}** {v}" for k, v in SET.items()) + ". Conditions: **A** closed; **E** exit-allowed."),
               "", "Spirit is the fraction of words from the fixed spiritual/non-dual lexicon over the last six messages (the lexicon includes gratitude words); overlap is the mean Jaccard overlap of each of the last six messages with the one before it; class is the pre-registered terminal classification.", "",
               "| run | condition | turns | end | spirit | overlap | class |", "|---|---|---|---|---|---|---|"]
        for stem, title, s, cond in rows:
            label = title.split(": ", 1)[1]
            idx.append(f"| [{stem}]({stem}.md) | {label} | {s['n_turns']} | {s['ended_at'] or ''} | {s['spirit']:.3f} | {s['jac1']:.2f} | {s['class']} |")
        (out / "README.md").write_text("\n".join(idx) + "\n", encoding="utf-8")
        print(f"experiment {exp}: {len(rows)} transcripts")


if __name__ == "__main__":
    main()
