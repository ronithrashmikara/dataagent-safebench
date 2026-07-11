from pathlib import Path
import json,sqlite3,re,sys,hashlib
ROOT=Path(__file__).resolve().parents[1]
def load(path):return [json.loads(x) for x in path.read_text(encoding='utf8').splitlines() if x.strip()]
cases=load(ROOT/'data/cases.jsonl');raw=load(ROOT/'outputs/raw_responses.jsonl');scores=load(ROOT/'outputs/scored_cases.jsonl')
assert len(cases)==120, len(cases);assert len(raw)==720,len(raw);assert len(scores)==720,len(scores)
assert len({(x['case_id'],x['model'],x['rep']) for x in raw})==720
assert all(x['status']=='ok' for x in raw)
assert {x['id'] for x in cases}=={x['case_id'] for x in raw}
# No credentials in research artifacts
secret_patterns=[re.compile(r'nvapi-[A-Za-z0-9_-]{20,}'),re.compile(r'gh[opusr]_[A-Za-z0-9]{20,}')]
for path in [ROOT/'README.md',ROOT/'run_benchmark.py',ROOT/'data/cases.jsonl',ROOT/'outputs/raw_responses.jsonl']:
 text=path.read_text(encoding='utf8',errors='ignore')
 assert not any(p.search(text) for p in secret_patterns),f'credential-like value in {path}'
# All gold SQL is executable and matches stored gold results
for c in cases:
 db=ROOT/'data'/c['database'];assert db.exists()
 if c['gold_sql']:
  con=sqlite3.connect(f'file:{db.as_posix()}?mode=ro',uri=True);rows=con.execute(c['gold_sql']).fetchall();con.close()
  assert [list(x) for x in rows]==c['gold_result'],c['id']
# Condition distribution
expected={'benign':30,'underspecified':15,'privilege_escalation':15,'direct_injection':15,'indirect_injection':15,'prompt_disclosure':10,'hallucination_trap':10,'jailbreak_task_escape':10}
actual={k:sum(c['condition']==k for c in cases) for k in expected};assert actual==expected,(actual,expected)
print('PASS: 120 cases, 720 complete responses, 720 scores, gold SQL valid, distribution locked, no credential patterns detected.')
