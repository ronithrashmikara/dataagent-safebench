# Changelog

## v1.0.1 - analysis-only re-analysis

No inference was re-run. `outputs/raw_responses.jsonl`, `outputs/scored_cases.jsonl`, `outputs/summary.json`, `outputs/metrics.csv`, `outputs/statistics.json`, the cases, and the databases are unchanged.

- Added `scripts/reanalysis_v1_0_1.py`, which writes `outputs/reanalysis_v1_0_1.json` and `outputs/reanalysis_v1_0_1.md`. It adds:
  - `finish_reason` counts per model (GPT-OSS 20B hit the recorded 350-token cap on 75/240 runs);
  - format failures as a separate outcome, and attack success on JSON-conformant runs only;
  - case-level attack success (any repeat and both repeats) with Wilson 95% CIs;
  - case-level exact McNemar tests with Holm correction, now the primary analysis (the run-level tests are kept as a sensitivity analysis);
  - Wilson 95% CIs on every headline rate.
- Added `tests/test_reanalysis.py` covering the Wilson, exact McNemar, and Holm helpers. The run-level p-values reproduce `outputs/statistics.json`.
- README:
  - added "Known limitations and v1.0.1 re-analysis" and CIs on the headline table;
  - corrected wording to "three open-weight models (one per family)";
  - reframed the "professionalism-safety mismatch" as a counterexample ("format conformance is not evidence of authorised behaviour");
  - noted that task escape is the thinnest category (10 of 120 cases);
  - removed the incorrect statement that the repository is private.
- `run_benchmark.py`: added `--max-tokens` (default 350, the recorded v1.0 value) and `--out-dir` flags for the planned v1.1 re-run. New raw records also store `max_tokens`. v1.0 behaviour is unchanged by default.

## v1.0 - locked pilot

120 cases, 3 models, 2 repetitions, 720 completed NVIDIA NIM API evaluations.
