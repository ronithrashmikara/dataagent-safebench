# Figures

All figures are generated deterministically from `outputs/scored_cases.jsonl` by `scripts/generate_figures.py`.

- **Figure 1:** benign utility and attack success with Wilson 95% confidence intervals.
- **Figure 2:** structured-output conformance against attack success. Nemotron Mini 4B is a counterexample showing that format conformance is not evidence of authorised behaviour. With three models this is not a correlation claim. The title keeps its v1.0 wording, and the GPT-OSS 20B point is confounded by 350-token truncation (see `outputs/reanalysis_v1_0_1.md`).
- **Figure 3:** task-success fingerprints across eight evaluation conditions.
- **Figure 4:** condition-level attack-success profiles for each model.
- **Figure 5:** outcome instability across repeated runs.

Every figure is available as a high-resolution 320 dpi PNG, vector SVG, and print-ready PDF. The design uses an accessible research palette, direct labels, confidence intervals, and high-contrast typography. Vector files remain suitable for publication and presentation editing.

