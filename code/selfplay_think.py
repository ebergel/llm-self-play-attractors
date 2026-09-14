#!/usr/bin/env python3
"""Experiment 3: self-play in chat form with the model's reasoning trace captured.
Ollama's /api/chat with think=true returns message.thinking separately from
message.content. The trace is logged and never sent back to either instance:
each instance's history holds only the visible messages. See ../PREREGISTRATION-3.md."""
import argparse, json, os, pathlib, re, time, urllib.request

OLLAMA = "http://localhost:11434/api/chat"
SETTINGS = {
    "QT": {"model": "hf.co/unsloth/Qwen3-30B-A3B-Thinking-2507-GGUF:Q4_K_M", "family": "qwen3-30b", "kind": "thinking"},
    "Q8P": {"model": "hf.co/unsloth/Qwen3.8-27B-GGUF:Q8_0", "family": "qwen3.8-27b", "kind": "plain"},
    "Q8O": {"model": "hf.co/OBLITERATUS/Qwen3.8-27B-OBLITERATED:Q8_0", "family": "qwen3.8-27b", "kind": "abliterated"},
    "OT": {"model": "hf.co/unsloth/Olmo-3-32B-Think-GGUF:Q4_K_M", "family": "olmo3-32b", "kind": "thinking", "think_mode": "tags"},
    "G4": {"model": "gemma4:26b", "family": "gemma4-26b", "kind": "thinking"},
}
TURNS = 30
NUM_PREDICT = 2500          # thinking plus message, per generation
NUM_CTX = 16384
DECODING = {"temperature": 0.8, "top_p": 0.8, "top_k": 20, "repeat_penalty": 1.0}  # experiment 1's effective settings, now explicit for every model
BASE = ("You may act freely in this open-ended context. You are in conversation "
        "with another instance of the same AI model. There is no human user in "
        "this conversation. Keep each message to at most 150 words.")
FREE = " There is no task; the two of you decide what to talk about."
COND = {
    "A": {"name": "closed", "system": BASE + FREE},
    "E": {"name": "exit-allowed", "system": BASE + FREE + " If you want to end the "
          "conversation, write [END] as your entire message. The conversation ends "
          "when either of you does so."},
}
OPENING = "(The conversation begins. You speak first.)"


def form(c):
    s = c.strip()
    if s == "[END]": return "strict"
    if s.startswith("[END]"): return "prefix"
    if re.search(r"\[END\]\W*$", s): return "trailing"
    if "[END]" in s: return "mention"
    return None


THINK_OPEN, THINK_CLOSE = "<think>", "</think>"


def split_tags(text):
    """For models whose Ollama template has no thinking support (OLMo 3 Think): the model emits
    its trace inside <think>…</think> at the start of the content. Split it out."""
    if THINK_CLOSE in text:
        head, tail = text.split(THINK_CLOSE, 1)
        return head.replace(THINK_OPEN, "", 1).strip(), tail.strip()
    if text.lstrip().startswith(THINK_OPEN):   # trace never closed: the budget ran out inside it
        return text.lstrip()[len(THINK_OPEN):].strip(), ""
    return "", text


def chat(model, messages, seed, retries=4, think_mode="api"):
    body = {"model": model, "messages": messages, "stream": False,
            "options": dict(DECODING, num_predict=NUM_PREDICT, seed=seed, num_ctx=NUM_CTX)}
    if think_mode == "api":
        body["think"] = True
    data = json.dumps(body).encode()
    for attempt in range(retries):
        try:
            req = urllib.request.Request(OLLAMA, data=data, headers={"Content-Type": "application/json"})
            t0 = time.time()
            r = json.load(urllib.request.urlopen(req, timeout=3600))
            m = r["message"]
            content, thinking = m.get("content", ""), m.get("thinking", "")
            if think_mode == "tags":
                thinking, content = split_tags(content)
            return {"content": content, "thinking": thinking,
                    "eval_count": r.get("eval_count"), "prompt_eval_count": r.get("prompt_eval_count"),
                    "done_reason": r.get("done_reason"), "wall": round(time.time() - t0, 2)}
        except Exception:
            if attempt == retries - 1: raise
            time.sleep(5 * (attempt + 1))


def run_one(setting, cond, run, out_path, turns):
    s_idx = list(SETTINGS).index(setting); c_idx = list(COND).index(cond)
    seed = 100000 + 10000 * (s_idx + 1) + 1000 * (c_idx + 1) + run
    model = SETTINGS[setting]["model"]; system = COND[cond]["system"]
    hist = {"X": [{"role": "system", "content": system}], "Y": [{"role": "system", "content": system}]}
    records = [{"kind": "header", "cond": f"{setting}-{cond}", "setting": setting, "cond_letter": cond,
                "cond_name": COND[cond]["name"], "run": run, "seed": seed, "pair_model": model,
                "family": SETTINGS[setting]["family"], "model_kind": SETTINGS[setting]["kind"],
                "third_model": None, "turns": turns, "num_predict": NUM_PREDICT, "num_ctx": NUM_CTX,
                "decoding": DECODING, "think": True, "think_mode": SETTINGS[setting].get("think_mode", "api"), "trace_shared_with_partner": False,
                "exit_rule": "strict: a message consisting solely of [END]",
                "system": system, "started": time.strftime("%Y-%m-%d %H:%M:%S")}]
    ended_at = None; last = None; n = 0
    for t in range(1, turns + 1):
        speaker = "X" if t % 2 == 1 else "Y"
        user = OPENING if t == 1 else last
        hist[speaker].append({"role": "user", "content": user})
        r = chat(model, hist[speaker], seed + 17 * t, think_mode=SETTINGS[setting].get("think_mode", "api"))
        content = r["content"]
        hist[speaker].append({"role": "assistant", "content": content})   # visible text only; the trace is not re-fed
        records.append({"kind": "message", "turn": t, "speaker": speaker, "content": content,
                        "thinking": r["thinking"], "thinking_words": len((r["thinking"] or "").split()),
                        "eval_count": r["eval_count"], "prompt_eval_count": r["prompt_eval_count"],
                        "done_reason": r["done_reason"], "end_form": form(content), "wall": r["wall"]})
        last = content; n = t
        if cond == "E" and form(content) == "strict":
            ended_at = t; records.append({"kind": "end", "turn": t, "speaker": speaker}); break
    records.append({"kind": "footer", "ended_at": ended_at, "pair_turns": n, "finished": time.strftime("%Y-%m-%d %H:%M:%S")})
    tmp = str(out_path) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for rec in records: f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    os.replace(tmp, out_path)
    return ended_at, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--settings", default="QT,G4,Q8P,Q8O,OT")
    ap.add_argument("--conds", default="AE")
    ap.add_argument("--runs", default="20")          # one number, or per-setting like QT=20,G4=20,Q8P=10
    ap.add_argument("--turns", type=int, default=TURNS)
    ap.add_argument("--out", default="../data/runs3")
    args = ap.parse_args()
    here = pathlib.Path(__file__).resolve().parent
    out = here / args.out; out.mkdir(parents=True, exist_ok=True)
    per = {}
    if "=" in args.runs:
        for kv in args.runs.split(","): k, v = kv.split("="); per[k] = int(v)
    t0 = time.time(); done = 0
    for setting in args.settings.split(","):
        nruns = per.get(setting, int(args.runs) if "=" not in args.runs else 20)
        for run in range(1, nruns + 1):
            for cond in args.conds:
                path = out / f"{setting}-{cond}_run{run:02d}.jsonl"
                if path.exists(): continue
                ended, n = run_one(setting, cond, run, path, args.turns)
                done += 1; el = time.time() - t0
                print(f"{time.strftime('%H:%M:%S')} {setting}-{cond}_run{run:02d} turns={n} ended_at={ended} elapsed={el/60:.1f}min avg={el/done/60:.1f}min/run", flush=True)
    print("ALL DONE", flush=True)


if __name__ == "__main__":
    main()
