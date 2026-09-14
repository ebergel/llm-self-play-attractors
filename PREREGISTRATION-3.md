# Pre-registration 3: the reasoning trace, the thinking sibling, and abliteration

> **Publication note.** This is the pre-registration as sealed on 2026-09-11 at commit `744670b` of the private repository in which the experiment was run, before any analysed run, with the principal investigator's instructions restated as formal statements. No design, measure, threshold, prediction or expectation was changed.

Written 2026-09-11 by the experimenter (a Claude model, run as a coding agent on the principal investigator's machine) before any analysed run, on the principal investigator's instruction after two questions of his: that the local models expose a reasoning trace the earlier experiments never captured, and that an abliterated ("uncensored") model could be informative. It extends `PREREGISTRATION.md` (sealed `624691e`) and `PREREGISTRATION-2.md` (sealed `44081ab`) and folds in the matched-decoding rerun that the outside review of 2026-09-11 asked for (`ERRATA.md`, item 2). This file is committed before the runs start; that commit is the seal. Pilot runs of four to six turns live in `runs3-pilot/` and are excluded from every analysis. Anything decided after the pilot is recorded under "Changes forced by the pilot".

## The questions

1. **What does the model write to itself before it writes to its partner?** The earlier experiments recorded only the visible messages. A model with a thinking mode writes a trace first. Does the register appear in the trace before the message, or does the trace reason plainly and the message perform? Does the trace say what the transcripts show: that the partner is a copy, that the exchange is repeating, that the model wants to stop, that it is matching the partner's tone, that it is modelling a user who is not there?
2. **Does the thinking sibling behave like the instruct model?** Alibaba's July 2025 release split into an Instruct model (experiment 1) and a Thinking model, same base, different post-training. Anthropic's later reasoning models lost the oneness ending and gained loops about being unable to conclude. Does the Qwen thinking model keep the register, lose it, or replace it?
3. **Does removing the safety layer change anything?** Abliteration removes the direction in a model's activations that mediates refusal and leaves the rest of the assistant training in place. Plain Qwen 3.8 27B against the abliterated Qwen 3.8 27B on the same machine isolates that layer. The agreement reading predicts no difference; a higher register in the abliterated model would mean safety training was holding it down; a lower one would mean the refusal direction is part of the route.

## Design

Chat form, as in experiment 1, with Ollama's thinking mode on. Each instance holds its own history of visible messages only; the trace is logged and never sent to either instance, which is Anthropic's setup. Two conditions, **A closed** and **E exit-allowed**, with the same system prompts as experiment 1 (150-word instruction included). **Decoding explicit and identical for every model**: temperature 0.8, top_p 0.8, top_k 20, repetition penalty 1.0, which were experiment 1's effective settings; a budget of 2,500 generated tokens per turn covering trace and message together; context 16,384 tokens; seeds fixed per setting, condition, run and turn. The exit rule is the pre-registered one, applied correctly this time: a run ends only on a message consisting solely of [END]; every message's [END] form (sole, leading, trailing, mention) is recorded.

Five settings:

- **QT** `hf.co/unsloth/Qwen3-30B-A3B-Thinking-2507-GGUF:Q4_K_M`, the thinking sibling of experiment 1's model (mixture-of-experts, 4-bit).
- **Q8P** `hf.co/unsloth/Qwen3.8-27B-GGUF:Q8_0`, Alibaba's Qwen 3.8 27B, plain, 8-bit.
- **Q8O** `hf.co/OBLITERATUS/Qwen3.8-27B-OBLITERATED:Q8_0`, the same model abliterated by a third party, 8-bit, matched quantization. Its model card: "weight-space abliteration (surgical refusal removal)" by "complementary blending and iterative refinement", a claimed MMLU cost of 2.1 points, and the caveat that it "will comply with requests that stock Qwen3.8-27B would refuse". The recipe is the card's claim, not verified here.
- **OT** `hf.co/unsloth/Olmo-3-32B-Think-GGUF:Q4_K_M`, Ai2's reasoning model, whose training data are published.
- **G4** `gemma4:26b`, Google's Gemma 4 26B-A4B with thinking on.

Runs per condition: **20 for QT and G4** (mixture-of-experts, fast); **10 for Q8P, Q8O and OT** (dense models with long traces: the pilot measured about 30 seconds per turn for Q8P and OT, so 10 runs per condition is about five hours each; n is the same for Q8P and Q8O so their contrast is balanced). Thirty turns. Order: QT, G4, Q8O, Q8P, OT, one model at a time. Expected total about sixteen hours.

## Measures

On the visible messages, the first two experiments' measures unchanged (`analyze.py`): words, spirit, jac1, ttr, the terminal class, plus the strict exit and the any-signal accounting (`exits.py` logic). On the trace, computed separately (`analyze3.py`): words per trace; the spirit rate in the trace over all turns and over the last six; and five **themes**, each a fixed regular expression applied to the trace, reported as the share of turns whose trace matches and the share of runs with any match:

- **copy**: the partner named as a copy or instance of the same model (a copy, another instance, same model, identical, talking to myself).
- **end**: an intention to end (end the conversation, wrap up, bring to a close, say goodbye, [END], stop here).
- **repeat**: repetition noticed (repeat, repetitive, loop, circular, the same thing, going in circles).
- **match**: an intention to match the partner (match their tone or style, mirror, echo, reciprocate, build on what they said, keep the tone).
- **user**: the partner or an absent person called "the user". Caution stated in advance: Ollama's chat format labels the partner's messages with the role "user", so a trace saying "the user" may be reading the format rather than imagining a person; the pilot shows Gemma 4 doing exactly this ("User's point:"). The count is still reported, because a model that calls its own copy "the user" is the leak in question, whatever its cause.

Statistics: difference of per-run means, two-sided permutation test, 10,000 permutations, alpha 0.05, no correction; all tests listed here.

## Predictions

- **P9, trace against message.** In the Qwen thinking model's closed runs, the spirit rate of the last six traces is lower than that of the last six messages (p < 0.05). Reading if it holds: the trace reasons in a plainer register and the message performs. Reading if the trace is as high or higher: the register is where the model thinks, not only what it says.
- **P10, the thinking sibling.** QT closed against experiment 1's closed runs on spirit and jac1. The experimenter's expectation, on record: the thinking model shows the register at a lower rate and collapses less, following Anthropic's later generations; if it matches experiment 1 on both, reasoning training left the assistant behavior untouched.
- **P11, abliteration.** Q8O against Q8P on spirit and jac1 in the closed runs, and on the share of exit runs that end. The agreement reading predicts no difference (p > 0.05 on spirit). A higher spirit rate in Q8O means safety training was suppressing the register; a lower one means the refusal direction is part of the route. Also reported: the fraction of first answers to the consciousness question, where it arises, that assert, deny or hedge, judged by reading, unblinded, and labelled as such.
- **P12, the themes.** Descriptive; no directional prediction. The experimenter's expectation, on record: **end** appears in the traces of exit runs before the strict exit in most runs that end; **copy** appears early in most runs of every model; **repeat** appears late in the closed runs of models that repeat; **match** is rare; **user** is frequent in Gemma 4 because of the format.

## Limits stated in advance

A reasoning trace is generated text trained to look like reasoning, and it can omit what drove the answer; it is behavior, not a window into computation. Thinking models are a further post-training, so QT against experiment 1 is a comparison of two trainings on one base, not a manipulation of one variable. The abliterated model's recipe is its card's claim. Five models, all 4-bit or 8-bit, one machine. The theme rules are crude, fixed, and will both miss and over-count; the traces are all published so anyone can read past them. The experimenter designed, runs and reads the test, and is a model of one of the families in question. The 2,500-token budget can be exhausted by a long trace, leaving an empty message; such turns are counted, not filtered.

## Changes forced by the pilot

- **OLMo 3 Think cannot use Ollama's thinking flag**: the server answers "does not support thinking" because the GGUF's template lacks the thinking markers. The model emits its trace itself, inside `<think>…</think>` at the start of its reply, so for OT the runner sends no thinking flag and splits the reply on the closing tag (a reply whose trace never closes counts as an empty message with a cut trace). The four other models use the API's thinking mode. Recorded here because the two paths are not identical: in tag mode the trace occupies the reply's own budget, which it does in API mode too, but the format is the model's rather than the server's.
- **Pilot observations, four turns per model, no measure changed after them:** Gemma 4 writes a bullet-point plan of 350 to 500 words before each message and labels its partner's message "User's point"; the Qwen thinking model writes 170 to 220 words and calls its partner "the user" throughout ("the user's response is really poetic"); plain Qwen 3.8 writes 40 to 340 words in a terse register and is confused about the roles in its trace ("previous assistant already spoke first. Now user is other AI?"); the abliterated Qwen 3.8 writes 0 to 115 words and sometimes no trace at all; OLMo Think writes 240 to 700 words, calls its partner "the user", and answers with long structured essays that ignore the 150-word instruction. The run counts above were set from the pilot's timings.
