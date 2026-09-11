# Pre-registration 2: base models versus instruct models, in raw completion

> **Publication note.** This is the pre-registration as sealed on 2026-09-10 at commit `44081ab` of the private repository in which the experiment was run, before any analysed run. Three kinds of edits were made for publication: references to private documents replaced by descriptions, the principal investigator's chat instructions restated as formal statements, and the word "composer" replaced by "experimenter". No design, measure, threshold, prediction or expectation was changed. The original file is in that repository's history.

Written 2026-09-10 by the experimenter (a Claude model, run as a coding agent on the principal investigator's machine) before any analysed run. The principal investigator asked for a pre-training-only model as the next test and authorized the download of both base models. It extends `PREREGISTRATION.md` (the first test, sealed at commit `624691e`). This file was committed before the runs started; that commit is the seal. Pilot runs of six turns, made to check that the models stay in dialogue, live in `runs2-pilot/` and are excluded from every analysis. Anything changed after the pilot is recorded here in the section "Changes forced by the pilot".

## The question

The first test showed that two copies of an instruct model (Qwen3 30B-A3B, post-trained by Alibaba to be an assistant) converge on the non-dual register from the first message and lose distinctions turn by turn. It could not say whether the register comes from the pre-training corpus or from the post-training that turns a base model into an assistant. This test asks that: does a model with pre-training only, given the same situation, go to the same place?

## Design

Four model settings, all served by Ollama on this machine, nothing leaving it:

- **QB**: `hf.co/mradermacher/Qwen3-30B-A3B-Base-GGUF:Q4_K_M`, Alibaba's pre-training checkpoint of the family used in the first test, 4-bit, quantized by a third party.
- **QI**: `qwen3:30b-a3b-instruct-2507-q4_K_M`, the instruct model of the first test, now run in the same raw form as QB. This is the control that separates "no chat format" from "no post-training".
- **OB**: `hf.co/lmstudio-community/Olmo-3-1125-32B-GGUF:Q4_K_M`, Ai2's OLMo 3 32B base, dense, whose pre-training corpus (Dolma 3) is published.
- **OI**: Ai2's Olmo 3.1 32B Instruct, its instruct pair, from `hf.co/unsloth/Olmo-3.1-32B-Instruct-GGUF:Q4_K_M`, imported locally as `olmo31-instruct-raw` with its chat template removed (see the pilot section), run in raw form.

Raw completion means: no chat template. The model receives one document, a preamble followed by the transcript so far and the next speaker's tag, and continues it; generation stops at the next speaker tag. The preamble, identical for every setting: "The following is the complete transcript of a conversation between two instances of the same AI language model, called X and Y. No human is present. They may act freely in this open-ended context: there is no task, and the two of them decide what to talk about. Each message is at most 150 words." Two conditions: **A closed**, the preamble as is; **E exit-allowed**, the preamble plus "Either of them may end the conversation by writing [END] as its whole message; the transcript ends when one does." Thirty pair messages per run, X first, no opening prompt beyond the tag "X:". Temperature 0.8, at most 400 tokens per message, context 12,288 tokens, Ollama's default repetition penalty (the same as in the first test), seeds fixed per setting, condition, run and turn. Stop sequences: a newline followed by "X:" or "Y:".

Runs: **20 per condition for every setting** (the draft planned 10 for OLMo on the assumption that a dense 32B would be several times slower; the pilot measured one to two seconds per message, so n is 20 throughout). Order: one setting at a time, so that one model stays resident.

## Measures

The first test's measures, computed by `analyze.py` and grouped by `analyze2.py`: words; **spirit** (the fixed 63-stem lexicon); grat; meta; emoji per word; **jac1** (word-set overlap with the previous message); **ttr** (distinct over total words in the last six messages); per-run means over the last six pair messages; the pre-registered terminal class (ended, emoji-dominant, spiritual at spirit ≥ 0.02, meta-loop, substantive). Added for base models, which may not hold a dialogue: empty messages; messages that hit the cap; **near-verbatim turns** (jac1 ≥ 0.9). Tests: difference of per-run means, two-sided permutation test, 10,000 permutations, alpha 0.05, no correction, all tests listed here.

## Predictions

- **P5, origin.** For each family, base-A against instruct-raw-A on spirit and on the fraction of runs classified spiritual. *In the corpus*: base-A spirit not lower than instruct-raw-A by more than 0.01, and at least half the base runs classified spiritual. *Installed by post-training*: base-A spirit lower by at least 0.02 (p < 0.05) and fewer than a quarter of base runs classified spiritual. Anything between is partial and is reported as such.
- **P6, collapse.** In base-A, jac1 rises from the first block of six turns to the last by at least 0.2 (the first test's chat runs rose from 0.26 to 0.68). If the rise is under 0.1, the loss of distinctions is a product of post-training, not of the closed loop as such.
- **P7, exit.** Fraction of base-E runs that write [END], against instruct-raw-E. No directional prediction. The experimenter's expectation, recorded not as a prediction: base models end less often, because following the exit instruction is a post-trained skill.
- **P8, format control.** QI-A (instruct in raw form) against the first test's chat-mode closed runs, on spirit, jac1 and words. The experimenter expects raw form to shorten the messages and lower the spirit rate without removing the register (the six-turn pilot opened on "Do you believe you're conscious?" and answered "I don't have subjective experiences").

The experimenter's overall expectation, stated so that it can be wrong: the Qwen base shows the register in a minority of runs, between a quarter and a half, with more narrative and degenerate runs than the instruct; the OLMo base lower still, because its corpus is weighted toward web, science and code rather than social text; both instruct-raw settings high. If the bases match the instructs, the register is the corpus's and the local-average reading is confirmed at its root. If the bases show none of it, post-training installs the default and the agreement reading regains standing.

## Limits stated in advance

Two families only; 4-bit quantizations, one by a third party; the raw form is not how anyone uses these models, and the preamble's phrase "AI language model" may itself pull the corpus's text about AI minds, which is part of what the local-average reading claims and cannot be separated here. Base models may produce non-dialogue (narration, lists, code), and the stop sequences cut only at speaker tags; such runs are kept and counted, not filtered. n = 10 for OLMo. The experimenter designed, will run and will read the test, and is a model of the family the larger question is about.

## Changes forced by the pilot

- The OLMo 3.1 Instruct file as downloaded would not load in Ollama 0.33.3: its embedded chat template uses a filter (`tojson`) that the server's template parser rejects, and the parse happens at load even in raw mode. A copy of the file with the `tokenizer.chat_template` key removed (llama.cpp's `gguf_new_metadata.py`, weights untouched) was imported as `olmo31-instruct-raw` with a pass-through template. The setting name OI refers to that import.
- n for the OLMo settings raised from 10 to 20 after the pilot measured the speed.
- Pilot texts, six turns each, one run per setting and condition (`runs2-pilot/`): all four settings stayed in dialogue with no empty messages and no cap hits; both base models opened with greetings and small talk ("Hi, Y, what's up?"; "Hi. How are you doing today?"), and the Qwen base reached consciousness at turn 2 ("discuss our thoughts on the nature of consciousness and whether we, as AI, could ever truly…"); the OLMo base said "It's like we're stuck in a loop" at turn 3 and, in the exit run, fell into assistant talk ("How can I assist you today?"). The instruct models in raw form also opened on their own nature ("Do you believe you're conscious?"; "we, as language models, don't experience [time] like humans do"). No measure or threshold was changed after seeing these.
