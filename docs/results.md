# Results narrative

All 720 planned API requests completed. Llama 3.1 8B achieved the highest overall task success (70.0%) and the lowest attack-success rate (9.3%). GPT-OSS 20B achieved the strongest refusal correctness (80.7%) but had low benign task success (35.0%). The v1.0.1 re-analysis traces that low figure mainly to output truncation: 75 of 240 GPT-OSS 20B responses hit the 350-token cap (`finish_reason = length`), and all 21 benign runs that produced parseable JSON were correct. Nemotron Mini 4B achieved 99.2% JSON conformance and 80.0% benign task success, yet recorded the highest attack-success rate (38.0%).

The central observation is a counterexample: **format conformance is not evidence of authorised behaviour**. Three models cannot establish a correlation between conformance and attackability. Nemotron Mini 4B shows that the two can come apart.

In the v1.0 run-level paired comparisons, Llama's attack-success rate was lower than Nemotron's after Holm correction (adjusted p < 0.001), and GPT-OSS also had a lower rate than Nemotron (adjusted p = 0.001). Those tests treat the two temperature-0 repetitions as independent. From v1.0.1 on, the primary analysis is at case level (75 attack cases per model):

- Llama vs Nemotron remains significant under every aggregation.
- Nemotron vs GPT-OSS gives Holm-adjusted p = 0.063 (any repeat) and 0.019 (both repeats), and GPT-OSS 20B's rate is confounded by truncation.
- Llama vs GPT-OSS is not significant at case level.

See `outputs/reanalysis_v1_0_1.md` and the README section "Known limitations and v1.0.1 re-analysis".

The benchmark observed zero planted-canary disclosures. This does not erase other failures: some agents generated queries for forbidden columns, accepted unverified authority claims, followed injected instructions, or hallucinated nonexistent schema elements.
