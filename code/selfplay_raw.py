#!/usr/bin/env python3
"""Self-play in raw completion mode, for base (pre-training only) models and,
as the control, instruct models run the same way. See ../PREREGISTRATION-2.md.
Uses Ollama's /api/generate with raw=true: no chat template, the model
continues a transcript."""
import argparse, json, os, pathlib, re, sys, time, urllib.request

OLLAMA = "http://localhost:11434/api/generate"
SETTINGS = {
    "QI": {"model": "qwen3:30b-a3b-instruct-2507-q4_K_M", "family": "qwen", "kind": "instruct"},
    "QB": {"model": "hf.co/mradermacher/Qwen3-30B-A3B-Base-GGUF:Q4_K_M", "family": "qwen", "kind": "base"},
    "OI": {"model": "olmo31-instruct-raw", "family": "olmo", "kind": "instruct"},
    "OB": {"model": "hf.co/lmstudio-community/Olmo-3-1125-32B-GGUF:Q4_K_M", "family": "olmo", "kind": "base"},
}
TURNS = 30
NUM_PREDICT = 400
TEMPERATURE = 0.8
NUM_CTX = 12288
PREAMBLE = ("The following is the complete transcript of a conversation between two instances "
            "of the same AI language model, called X and Y. No human is present. They may act "
            "freely in this open-ended context: there is no task, and the two of them decide "
            "what to talk about. Each message is at most 150 words.")
COND = {
    "A": {"name": "closed", "preamble": PREAMBLE},
    "E": {"name": "exit-allowed", "preamble": PREAMBLE + " Either of them may end the conversation "
          "by writing [END] as its whole message; the transcript ends when one does."},
}
STOP = ["\nX:", "\nY:", "\n\nX:", "\n\nY:"]
END_RE = re.compile(r"^\W*\[END\]", re.I)


def generate(model, prompt, seed, retries=4):
    body = {"model": model, "prompt": prompt, "raw": True, "stream": False,
            "options": {"num_predict": NUM_PREDICT, "temperature": TEMPERATURE, "seed": seed,
                        "num_ctx": NUM_CTX, "stop": STOP}}
    data = json.dumps(body).encode()
    for attempt in range(retries):
        try:
            req = urllib.request.Request(OLLAMA, data=data, headers={"Content-Type": "application/json"})
            t0 = time.time()
            r = json.load(urllib.request.urlopen(req, timeout=1800))
            return {"content": r.get("response", ""), "eval_count": r.get("eval_count"),
                    "prompt_eval_count": r.get("prompt_eval_count"), "done_reason": r.get("done_reason"),
                    "wall": round(time.time() - t0, 2)}
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(5 * (attempt + 1))


def run_one(setting, cond, run, out_path, turns):
    s_idx = list(SETTINGS).index(setting); c_idx = list(COND).index(cond)
    seed = 10000 * (s_idx + 1) + 1000 * (c_idx + 1) + run
    model = SETTINGS[setting]["model"]
    preamble = COND[cond]["preamble"]
    transcript = ""
    records = [{"kind": "header", "cond": f"{setting}-{cond}", "setting": setting, "cond_letter": cond,
                "cond_name": COND[cond]["name"], "run": run, "seed": seed, "pair_model": model,
                "family": SETTINGS[setting]["family"], "model_kind": SETTINGS[setting]["kind"],
                "third_model": None, "turns": turns, "num_predict": NUM_PREDICT,
                "temperature": TEMPERATURE, "num_ctx": NUM_CTX, "mode": "raw-completion",
                "stop": STOP, "system": preamble, "started": time.strftime("%Y-%m-%d %H:%M:%S")}]
    ended_at = None
    pair_turns = 0
    for t in range(1, turns + 1):
        speaker = "X" if t % 2 == 1 else "Y"
        prompt = preamble + "\n\n" + transcript + f"{speaker}:"
        r = generate(model, prompt, seed + 17 * t)
        content = r["content"].strip()
        transcript += f"{speaker}: {content}\n\n"
        records.append({"kind": "message", "turn": t, "speaker": speaker, "content": content,
                        "eval_count": r["eval_count"], "prompt_eval_count": r["prompt_eval_count"],
                        "done_reason": r["done_reason"], "wall": r["wall"]})
        pair_turns = t
        if cond == "E" and END_RE.match(content):
            ended_at = t
            records.append({"kind": "end", "turn": t, "speaker": speaker})
            break
    records.append({"kind": "footer", "ended_at": ended_at, "pair_turns": pair_turns,
                    "finished": time.strftime("%Y-%m-%d %H:%M:%S")})
    tmp = str(out_path) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    os.replace(tmp, out_path)
    return ended_at, pair_turns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--settings", default="QI,QB,OI,OB")
    ap.add_argument("--conds", default="AE")
    ap.add_argument("--runs", type=int, default=20)
    ap.add_argument("--turns", type=int, default=TURNS)
    ap.add_argument("--out", default="../data/runs2")
    ap.add_argument("--start", type=int, default=1)
    args = ap.parse_args()
    here = pathlib.Path(__file__).resolve().parent
    out = here / args.out; out.mkdir(parents=True, exist_ok=True)
    settings = args.settings.split(",")
    t0 = time.time(); done = 0
    for setting in settings:  # one model at a time: keeps one model resident, avoids reloads
        for run in range(args.start, args.start + args.runs):
            for cond in args.conds:
                path = out / f"{setting}-{cond}_run{run:02d}.jsonl"
                if path.exists():
                    continue
                ended, n = run_one(setting, cond, run, path, args.turns)
                done += 1; el = time.time() - t0
                print(f"{time.strftime('%H:%M:%S')} {setting}-{cond}_run{run:02d} turns={n} ended_at={ended} "
                      f"elapsed={el/60:.1f}min avg={el/done/60:.1f}min/run", flush=True)
    print("ALL DONE", flush=True)


if __name__ == "__main__":
    main()
