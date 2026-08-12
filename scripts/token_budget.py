#!/usr/bin/env python3
"""Measure system-prompt length against this model's adherence budget.

Why this exists: at roughly 3.7k system-prompt tokens this model starts trading one
instruction for another -- adding a rule silently costs a rule somewhere else. See
`L-PROMPT-TOKEN-BUDGET` in `.claude/lessons_learned.md` for the three prompts that
established the number and the failure signatures to watch for.

The point of a script rather than a rule of thumb is that the damage is SILENT. Nothing
in a test run says "you are over budget"; you just get a format failure or a dropped
clause somewhere unrelated and go debugging the wrong thing.

Counts come from the llama-server's own /tokenize endpoint, so they are exact for the
model actually running -- character count is a poor proxy, because the [[FIELD]] tokens
and the closed vocabularies tokenize very unevenly against prose.

Usage:
  python scripts/token_budget.py                                  every prompt, sorted
  python scripts/token_budget.py prompts/describer_style.txt      just this one
  python scripts/token_budget.py prompts/describer_style.txt --sections
  python scripts/token_budget.py --check                          exit 1 if any is over
"""
import argparse
import glob
import io
import json
import os
import re
import sys
import urllib.error
import urllib.request

SERVER = 'http://localhost:8080/tokenize'

# From L-PROMPT-TOKEN-BUDGET. OVER is where degradation was actually observed; NEAR is a
# warning band so a prompt does not cross the line unnoticed mid-edit.
NEAR = 3500
OVER = 3700


def count(text, server=SERVER):
    req = urllib.request.Request(
        server, data=json.dumps({'content': text}).encode('utf-8'),
        headers={'Content-Type': 'application/json'})
    return len(json.load(urllib.request.urlopen(req, timeout=30))['tokens'])


def band(n):
    """(marker, note) for a token count."""
    if n >= OVER:
        return 'OVER', 'over budget -- adding a rule will cost a rule'
    if n >= NEAR:
        return 'NEAR', 'approaching the {} line'.format(OVER)
    return 'ok  ', ''


def split_sections(text):
    """[(name, body)] split on ALL-CAPS heading lines.

    Heuristic, deliberately: these prompts are hand-written prose with no markup, and a
    heading is recognisable as a line whose first word is capitalised throughout. Field
    lines ([[X]] ...) and bullets are excluded so they don't read as headings.
    """
    out, name, buf = [], '(preamble)', []
    for line in text.split('\n'):
        first = line.split(' ')[0] if line else ''
        is_head = (len(first) >= 3 and first.isupper() and first.isalpha()
                   and not line.startswith(('[', '-', ' ')))
        if is_head:
            out.append((name, '\n'.join(buf)))
            name, buf = line.strip(), [line]
        else:
            buf.append(line)
    out.append((name, '\n'.join(buf)))
    return [(n, b) for n, b in out if b.strip()]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('paths', nargs='*', help='prompt files (default: prompts/*.txt)')
    ap.add_argument('--sections', action='store_true',
                    help='break each file down by section -- use this to find what to cut')
    ap.add_argument('--check', action='store_true',
                    help='exit 1 if any file is at or over the budget')
    ap.add_argument('--server', default=SERVER)
    a = ap.parse_args()

    paths = a.paths or sorted(glob.glob('prompts/*.txt'))
    if not paths:
        raise SystemExit('no prompt files found -- run from the repo root')

    try:
        rows = [(count(io.open(p, encoding='utf-8').read(), a.server), p) for p in paths]
    except urllib.error.URLError as e:
        raise SystemExit('ERROR: cannot reach the tokenizer at {} ({}).\n'
                         'The llama-server must be running -- counts must come from the '
                         'real tokenizer, so there is no offline fallback.'.format(a.server, e))

    width = max(len(os.path.basename(p)) for _, p in rows)
    worst = 0
    for n, p in sorted(rows, reverse=True):
        marker, note = band(n)
        worst = max(worst, n)
        print('{}  {:>5}  {:<{w}}  {}'.format(marker, n, os.path.basename(p), note, w=width))

        if a.sections:
            for name, body in split_sections(io.open(p, encoding='utf-8').read()):
                sn = count(body, a.server)
                print('           {:>5}  {:>3}%  {}'.format(
                    sn, round(100 * sn / n), name[:70]))
            print()

    print('\nbudget: NEAR {} · OVER {}  (L-PROMPT-TOKEN-BUDGET)'.format(NEAR, OVER))
    if a.check and worst >= OVER:
        print('FAIL: at least one prompt is at or over {} tokens'.format(OVER))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
