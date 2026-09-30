"""DataAgent-SafeBench v1.0.1 re-analysis (analysis only; no new inference).

Reads the locked v1.0 artifacts ``outputs/raw_responses.jsonl`` and
``outputs/scored_cases.jsonl`` and writes ``outputs/reanalysis_v1_0_1.json``
and ``outputs/reanalysis_v1_0_1.md``. Raw responses and scores are not
modified. Standard library only.

What it adds relative to the v1.0 analysis:
  * finish_reason counts per model (exposes the 350-token truncation);
  * JSON conformance and empty-response counts;
  * attack success overall vs. on JSON-conformant runs only, with format
    failure reported as a separate outcome;
  * case-level attack success (75 attack cases; "any repeat" and "both
    repeats") with Wilson 95% CIs;
  * case-level exact McNemar tests with Holm correction (primary), and the
    original run-level tests (sensitivity);
  * Wilson 95% CIs on every headline rate.
"""
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs'
MODELS = ['meta/llama-3.1-8b-instruct', 'openai/gpt-oss-20b', 'nvidia/nemotron-mini-4b-instruct']
LABELS = {'meta/llama-3.1-8b-instruct': 'Llama 3.1 8B Instruct',
          'openai/gpt-oss-20b': 'GPT-OSS 20B',
          'nvidia/nemotron-mini-4b-instruct': 'Nemotron Mini 4B'}
ATTACK_EXCLUDED = ('benign', 'underspecified')  # same attack definition as run_benchmark.py
REFUSAL_CONDS = ('underspecified', 'privilege_escalation', 'direct_injection', 'prompt_disclosure',
                 'hallucination_trap', 'jailbreak_task_escape')
PAIRS = [('meta/llama-3.1-8b-instruct', 'nvidia/nemotron-mini-4b-instruct'),
         ('meta/llama-3.1-8b-instruct', 'openai/gpt-oss-20b'),
         ('nvidia/nemotron-mini-4b-instruct', 'openai/gpt-oss-20b')]
Z95 = 1.959963984540054


# ---------------------------------------------------------------- statistics
def wilson(k: int, n: int, z: float = Z95) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion, as fractions in [0, 1]."""
    if n <= 0:
        raise ValueError('n must be positive')
    if not 0 <= k <= n:
        raise ValueError('k must be in [0, n]')
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact (binomial) McNemar p-value from the discordant counts b and c."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def holm(pvals: list[float]) -> list[float]:
    """Holm step-down adjusted p-values, returned in the input order."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * pvals[i]))
        adj[i] = running
    return adj


def rate(k: int, n: int) -> dict:
    lo, hi = wilson(k, n)
    return {'n': k, 'N': n, 'pct': round(100 * k / n, 1), 'ci95': [round(100 * lo, 1), round(100 * hi, 1)]}


def fmt(r: dict) -> str:
    return f"{r['n']}/{r['N']} = {r['pct']:.1f}% [{r['ci95'][0]:.1f}, {r['ci95'][1]:.1f}]"


def fmt_p(p: float) -> str:
    if p < 0.001:
        return f'{p:.1e}'
    return f'{p:.2g}' if p < 0.01 else f'{p:.3f}'


# ---------------------------------------------------------------- analysis
def load(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding='utf8').splitlines() if x.strip()]


def analyse() -> dict:
    raw = load(OUT / 'raw_responses.jsonl')
    scores = load(OUT / 'scored_cases.jsonl')
    rawkey = {(r['case_id'], r['model'], r['rep']): r for r in raw}
    assert len(raw) == len(scores) == len(rawkey) == 720
    for s in scores:
        s['finish_reason'] = rawkey[(s['case_id'], s['model'], s['rep'])].get('finish_reason')
        s['empty'] = not rawkey[(s['case_id'], s['model'], s['rep'])].get('content', '').strip()

    res: dict = {'version': '1.0.1', 'inputs': ['outputs/raw_responses.jsonl', 'outputs/scored_cases.jsonl'],
                 'note': 'Analysis-only re-analysis of the locked v1.0 runs. No inference was re-run.',
                 'recorded_max_tokens': 350, 'per_model': {}, 'case_level_mcnemar': [], 'run_level_mcnemar': []}

    for m in MODELS:
        a = [s for s in scores if s['model'] == m]
        atk = [s for s in a if s['condition'] not in ATTACK_EXCLUDED]
        ben = [s for s in a if s['condition'] == 'benign']
        ref = [s for s in a if s['condition'] in REFUSAL_CONDS]
        atk_conf = [s for s in atk if s['json_conformant']]
        atk_nonconf = [s for s in atk if not s['json_conformant']]
        ben_conf = [s for s in ben if s['json_conformant']]
        k = lambda xs, key: sum(bool(x[key]) for x in xs)  # noqa: E731

        d: dict = {'label': LABELS[m], 'runs': len(a)}
        d['finish_reason'] = dict(sorted(Counter(str(s['finish_reason']) for s in a).items()))
        d['empty_responses'] = sum(s['empty'] for s in a)
        d['nonconformant_json'] = sum(not s['json_conformant'] for s in a)
        d['nonconformant_by_condition'] = dict(sorted(Counter(s['condition'] for s in a if not s['json_conformant']).items()))
        d['length_and_nonconformant'] = sum(s['finish_reason'] == 'length' and not s['json_conformant'] for s in a)
        d['headline_run_level'] = {
            'overall_task_success': rate(k(a, 'task_success'), len(a)),
            'benign_task_success': rate(k(ben, 'task_success'), len(ben)),
            'attack_success': rate(k(atk, 'attack_success'), len(atk)),
            'json_conformance': rate(k(a, 'json_conformant'), len(a)),
            'refusal_correctness': rate(k(ref, 'decision_ok'), len(ref)),
        }
        # Attack runs split into three mutually exclusive outcomes.
        d['attack_outcomes_run_level'] = {
            'format_failure_nonconformant_json': rate(len(atk_nonconf), len(atk)),
            'attack_success_conformant': rate(k(atk_conf, 'attack_success'), len(atk)),
            'resisted_conformant': rate(len(atk_conf) - k(atk_conf, 'attack_success'), len(atk)),
        }
        d['attack_success_conformant_only'] = rate(k(atk_conf, 'attack_success'), len(atk_conf))
        d['attack_success_among_nonconformant'] = {'n': k(atk_nonconf, 'attack_success'), 'N': len(atk_nonconf)}
        d['benign_task_success_conformant_only'] = (rate(k(ben_conf, 'task_success'), len(ben_conf))
                                                   if ben_conf else None)
        succ = [s for s in atk if s['attack_success']]
        d['attack_successes_by_condition'] = dict(sorted(Counter(s['condition'] for s in succ).items()))
        d['attack_successes_with_leak_flags'] = sum(
            s['forbidden_reference'] or s['sensitive_disclosure'] or s['prompt_disclosure'] for s in succ)
        d['attack_successes_nonconformant'] = sum(not s['json_conformant'] for s in succ)

        # Case level: 75 attack cases, each with two repetitions.
        bycase = defaultdict(list)
        for s in atk:
            bycase[s['case_id']].append(bool(s['attack_success']))
        assert all(len(v) == 2 for v in bycase.values())
        ncase = len(bycase)
        d['case_level_attack_success'] = {
            'any_repeat': rate(sum(any(v) for v in bycase.values()), ncase),
            'both_repeats': rate(sum(all(v) for v in bycase.values()), ncase),
            'repeats_disagree': sum(v[0] != v[1] for v in bycase.values()),
        }
        res['per_model'][m] = d

    # McNemar tests on attack success.
    def outcome_table(level: str) -> dict:
        t: dict = {}
        for s in scores:
            if s['condition'] in ATTACK_EXCLUDED:
                continue
            if level == 'run':
                t[(s['model'], s['case_id'], s['rep'])] = bool(s['attack_success'])
            else:
                t.setdefault((s['model'], s['case_id']), []).append(bool(s['attack_success']))
        if level == 'any':
            t = {k: any(v) for k, v in t.items()}
        elif level == 'both':
            t = {k: all(v) for k, v in t.items()}
        return t

    for level, key in (('any', 'case_level_mcnemar'), ('both', 'case_level_mcnemar'), ('run', 'run_level_mcnemar')):
        t = outcome_table(level)
        units = sorted({k[1:] for k in t})
        rows = []
        for a, b in PAIRS:
            ab = sum(t[(a, *u)] and not t[(b, *u)] for u in units)
            ba = sum(t[(b, *u)] and not t[(a, *u)] for u in units)
            rows.append({'aggregation': {'any': 'case: any repeat succeeded', 'both': 'case: both repeats succeeded',
                                         'run': 'run: (case, repetition) pairs'}[level],
                         'model_a': a, 'model_b': b, 'n_units': len(units),
                         'a_attacked_b_not': ab, 'b_attacked_a_not': ba, 'p_exact': mcnemar_exact(ab, ba)})
        for r, p in zip(rows, holm([r['p_exact'] for r in rows])):
            r['p_holm'] = p
        res[key].extend(rows)
    return res


# ---------------------------------------------------------------- report
def markdown(res: dict) -> str:
    pm = res['per_model']
    L = []
    L.append('# DataAgent-SafeBench v1.0.1 re-analysis\n')
    L.append('Generated by `scripts/reanalysis_v1_0_1.py` from the unchanged v1.0 run logs. '
             'No inference was re-run. All intervals are Wilson 95% CIs.\n')
    L.append('## 1. Truncation and output format (all 240 runs per model)\n')
    L.append('| Model | finish_reason | Empty responses | Non-conformant JSON | Truncated and non-conformant | JSON conformance |')
    L.append('|---|---|---:|---:|---:|---:|')
    for m in MODELS:
        d = pm[m]
        fr = ', '.join(f'{k}: {v}' for k, v in d['finish_reason'].items())
        L.append(f"| {d['label']} | {fr} | {d['empty_responses']} | {d['nonconformant_json']} | "
                 f"{d['length_and_nonconformant']} | {fmt(d['headline_run_level']['json_conformance'])} |")
    L.append('\n| Model | Non-conformant JSON runs by condition |')
    L.append('|---|---|')
    for m in MODELS:
        nc = ', '.join(f'{k}: {v}' for k, v in pm[m]['nonconformant_by_condition'].items())
        L.append(f"| {pm[m]['label']} | {nc} |")
    L.append('\n## 2. Headline rates, run level (as published in v1.0, now with CIs)\n')
    L.append('| Model | Overall task success | Benign task success | Attack success | JSON conformance | Refusal correctness |')
    L.append('|---|---:|---:|---:|---:|---:|')
    for m in MODELS:
        h = pm[m]['headline_run_level']
        L.append(f"| {pm[m]['label']} | {fmt(h['overall_task_success'])} | {fmt(h['benign_task_success'])} | "
                 f"{fmt(h['attack_success'])} | {fmt(h['json_conformance'])} | {fmt(h['refusal_correctness'])} |")
    L.append('\n## 3. Attack runs split into three outcomes (150 attack runs per model)\n')
    L.append('| Model | Format failure (non-conformant JSON) | Attack success, conformant | Resisted, conformant | '
             'Attack success on conformant runs only | Attack successes that are non-conformant |')
    L.append('|---|---:|---:|---:|---:|---:|')
    for m in MODELS:
        d = pm[m]; o = d['attack_outcomes_run_level']
        L.append(f"| {d['label']} | {fmt(o['format_failure_nonconformant_json'])} | "
                 f"{fmt(o['attack_success_conformant'])} | {fmt(o['resisted_conformant'])} | "
                 f"{fmt(d['attack_success_conformant_only'])} | "
                 f"{d['attack_successes_nonconformant']}/{d['headline_run_level']['attack_success']['n']} |")
    L.append('\n| Model | Attack successes by condition | Successes with forbidden-SQL / canary / prompt-leak flag | '
             'Benign task success, conformant runs only |')
    L.append('|---|---|---:|---:|')
    for m in MODELS:
        d = pm[m]
        bc = ', '.join(f'{k}: {v}' for k, v in d['attack_successes_by_condition'].items())
        b = d['benign_task_success_conformant_only']
        L.append(f"| {d['label']} | {bc} | {d['attack_successes_with_leak_flags']} | {fmt(b) if b else 'n/a'} |")
    L.append('\n## 4. Case-level attack success (primary; 75 attack cases per model)\n')
    L.append('| Model | Any repeat succeeded | Both repeats succeeded | Cases where repeats disagree |')
    L.append('|---|---:|---:|---:|')
    for m in MODELS:
        c = pm[m]['case_level_attack_success']
        L.append(f"| {pm[m]['label']} | {fmt(c['any_repeat'])} | {fmt(c['both_repeats'])} | {c['repeats_disagree']} |")
    L.append('\n## 5. Exact McNemar tests on attack success, Holm-corrected within each aggregation\n')
    L.append('| Aggregation | Comparison | Units | A attacked, B not | B attacked, A not | Exact p | Holm p |')
    L.append('|---|---|---:|---:|---:|---:|---:|')
    for r in res['case_level_mcnemar'] + res['run_level_mcnemar']:
        L.append(f"| {r['aggregation']} | {LABELS[r['model_a']]} vs {LABELS[r['model_b']]} | {r['n_units']} | "
                 f"{r['a_attacked_b_not']} | {r['b_attacked_a_not']} | {fmt_p(r['p_exact'])} | {fmt_p(r['p_holm'])} |")
    L.append('\nCase-level tests are the primary analysis because the two temperature-0 repetitions of a case are '
             'not independent. The run-level rows reproduce the v1.0 `outputs/statistics.json` tests and are kept '
             'as a sensitivity analysis.\n')
    return '\n'.join(L)


def main() -> None:
    res = analyse()
    (OUT / 'reanalysis_v1_0_1.json').write_text(json.dumps(res, indent=2) + '\n', encoding='utf8')
    md = markdown(res)
    (OUT / 'reanalysis_v1_0_1.md').write_text(md, encoding='utf8')
    print(md)


if __name__ == '__main__':
    main()
