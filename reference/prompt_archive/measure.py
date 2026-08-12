#!/usr/bin/env python3
"""Token-count every distinct prompt state found by census.py.

  python .claude/experiments/prompt_archive/measure.py

Counts come from scripts/token_budget.py's `count` -- the live llama-server tokenizer -- so
they are directly comparable with every number in L-PROMPT-TOKEN-BUDGET, token_budget.py's
own docstring table, and the bloat experiment's curve. A character count is not a substitute:
the whole point of the budget question is token behaviour.

Content is re-read from git (or the working tree) rather than trusted from census.json, and
normalised to LF before counting so a CRLF checkout cannot shift a count.
"""
import io
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _paths import find_root                            # noqa: E402

ROOT = find_root(HERE)
sys.path.insert(0, str(ROOT / 'scripts'))
from token_budget import count, band                   # noqa: E402


def content_of(state):
    """Bytes for a state, from whichever source can still produce it."""
    for c in state['commits']:
        out = subprocess.run(['git', 'show', f'{c["commit"]}:{c["path"]}'],
                             cwd=ROOT, capture_output=True)
        if out.returncode == 0:
            return out.stdout
    for p in state['paths']:
        f = ROOT / p
        if f.exists():
            return f.read_bytes()
    raise SystemExit(f'cannot recover content for {state["md5_norm"]}')


def main():
    data = json.loads((HERE / 'census.json').read_text(encoding='utf-8'))
    rows = []
    for st in data['states']:
        text = content_of(st).replace(b'\r\n', b'\n').decode('utf-8')
        n = count(text)
        first = st['commits'][0] if st['commits'] else None
        rows.append({'md5': st['md5_norm'][:10], 'tokens': n, 'bytes': st['bytes'],
                     'labels': st['labels'], 'names': st['names'],
                     'live': st['in_worktree'], 'committed': bool(st['commits']),
                     'first': f'{first["date"]} {first["commit"]}' if first else '(never)',
                     'paths': st['paths']})

    rows.sort(key=lambda r: -r['tokens'])
    print(f'{"md5":<11} {"tokens":>6}  {"bytes":>6}  {"first seen":<18} label / names')
    for r in rows:
        marker, _ = band(r['tokens'])
        tag = ' LIVE' if r['live'] else ''
        if not r['committed']:
            tag += ' UNCOMMITTED'
        lbl = ', '.join(r['labels']) or ', '.join(r['names'])
        print(f'{r["md5"]:<11} {r["tokens"]:>6}  {r["bytes"]:>6}  {r["first"]:<18} '
              f'{marker} {lbl}{tag}')
    (HERE / 'tokens.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
    return 0


if __name__ == '__main__':
    sys.exit(main())
