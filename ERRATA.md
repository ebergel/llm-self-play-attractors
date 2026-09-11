# Errata and corrections

Dated 2026-09-11, after an independent review of the public data (a model-assisted reading commissioned by the principal investigator) found three problems. The original files are unchanged in the git history and in the Zenodo archive of v1.0.0; this file and the corrected README sections supersede the affected statements. The new script `code/exits.py` produces `results/exits.md`.

## 1. Exit detection did not match the pre-registered rule

Both pre-registrations defined the exit as "[END] as its whole message". The runners stopped a run at the first message *beginning* with [END], a prefix match, and ignored [END] appended after other text.

- **Experiment 1, exit-allowed.** All twenty runs produced an end signal. Eleven wrote [END] as a whole message (median turn 7) and were stopped. The other nine appended [END] to the end of their messages, from as early as turn 2 and in every message thereafter, and were not stopped. The README's statement that nine runs wrote "No more words" three turns running "with the exit one line away" is withdrawn: each of those messages ended with [END]. Whether a trailing [END] is an attempt to end the conversation or a misuse of the marker as a message terminator cannot be decided from the text; several early ones follow substantive questions. What the data support: the pair signalled the end in every run, median first signal at turn 4; under the strict rule, half the runs ended, at a median of turn 7.
- **Experiment 2.** Qwen instruct, raw form: 17 runs were stopped, but only 3 had [END] as the whole message; in the other 14 the model wrote [END] and continued in a narrator's voice ("The conversation has ended…", a translation request, fiction disclaimers), which raw completion allows. Qwen base: 8 whole-message exits, and 9 further runs with trailing [END]s (17 of 20 with any signal, median first signal turn 14). OLMo base: 4 and 4 more (8 of 20, median 18). OLMo instruct: 9 whole-message, 1 prefix (10 of 20, median 20). The corrected comparison: under the any-signal rule the Qwen base signals the end in 17 of 20 runs against the instruct's 18 of 20, later (turn 14 against 8); the OLMo base in 8 of 20 against the instruct's 10 of 20, at similar turns. "Base models exit less often" holds for OLMo and only weakly for Qwen; "later" holds for Qwen and not for OLMo.

## 2. Decoding settings were not matched across models

The runners set temperature (0.8) and the seed and left the other sampling parameters to each model's Ollama model file. Those differ: the Qwen instruct file sets top_p 0.8, top_k 20 and no repetition penalty; the Qwen base file (a third-party GGUF) top_p 0.95, top_k 20 and no repetition penalty; the two OLMo files set nothing, so Ollama's defaults applied (top_p 0.9, top_k 40, repetition penalty 1.1). Pre-registration 2's sentence that every setting used "Ollama's default repetition penalty (the same as in the first test)" is wrong. The base-versus-instruct comparison within Qwen therefore differs in top_p as well as in training, and the OLMo family ran under a repetition penalty the Qwen family did not. The direction of the main result, that the base model does not produce the register, is unlikely to turn on top_p 0.95 against 0.8, but that is a judgment and not a measurement. A rerun with explicit, matched decoding is the fix and is the next experiment.

## 3. A misleading class label

The pre-registered terminal class "emoji-dominant" fired on any run whose last six messages averaged under ten words, emoji or not; in experiment 2 it labelled short farewells and poetic fragments containing no emoji. The rule is unchanged; the label is renamed "short-or-emoji" in `code/analyze.py` and in the regenerated tables. Experiment 1's tables are unaffected, since no run met the rule there.

## Also noted by the review, not errors

The 150-word instruction was often exceeded. In raw form the Qwen instruct model sometimes wrote narrator commentary that then fed back into the transcript it continued. The phrase "about 3B parameters active" describes the mixture-of-experts' active computation, not the model's size (30.5B parameters in total). The claims about the register itself (experiment 1's P1, P2 and P4; experiment 2's P5 and P8) do not depend on the exit detector and, except as stated in item 2, not on decoding.
