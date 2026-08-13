#!/usr/bin/env python3
"""ACTION COVERAGE -- the fl2va composer's content metric.

Side experiment: .claude/handoffs/SIDE_HANDOFF_bloat_calibration2.md

Round 1's dependent variable was too weak for this round's question: format was 26/26 nearly
everywhere, and validate.py cannot see the failure mode that matters. Its own evidence is
set_p6_outside, which turned a furnished view into '[[CONTENTS]] none' while staying perfectly
well-formed. So this round measures CONTENT, and this is the primary probe's half of it.

The composer is chosen because the user's own USER: line NAMES the actions that must appear, so
coverage is mechanically checkable rather than a judgement call. Round 1 built this list by hand;
this formalises it.

MATCHING. Case-insensitive substring against a deliberately TRUNCATED stem, so every inflection
counts as one hit. 'skat' catches skate / skates / skating / skated -- plain 'skate' would miss
'skating', which is the likeliest wording for p5. Likewise 'gun' catches handgun, 'walk' catches
walking, 'stop' catches stopping, 'turn' catches turning.

The stems buy inclusiveness at the price of a small false-positive surface ('suit' inside
'suitable', 'gun' inside 'gunmetal'). That is acceptable because this metric is read as a
DIFFERENCE against the L0 control, never as an absolute score: a false positive that fires at L0
fires at every level. Every hit is printed with its surrounding text so each one is checkable.

p1's 'lamp' is the NEGATIVE CONTROL. It is known-absent in both fl2va v3 and v4 -- the event is
lost upstream, since nothing in the composer's input corroborates it -- so it should stay absent
at every level. If a level makes it appear, that is real signal; if p1 is the only mover, be
suspicious.

  python reference/experiments/bloat2/coverage.py <run.txt> --prefix c_L0_
  python reference/experiments/bloat2/coverage.py <run.txt> --all --json
"""
import argparse
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
assert ROOT.name == 'h3-prompt-rewriter' and (ROOT / '.git').is_dir(), \
    f'ROOT resolved to {ROOT} -- refusing to run outside the project'
sys.path.insert(0, str(ROOT / 'scripts'))
from validate import head_parts, parse_records          # noqa: E402 -- imported, never modified

# case -> [(element name, [accepted stems])]. The stems are truncated ON PURPOSE; see the module
# docstring. Do not "fix" them into whole words.
ELEMENTS = {
    'p1': [('lamp', ['lamp']), ('gun', ['gun'])],
    'p2': [('gun', ['gun', 'pistol']), ('table', ['table'])],
    'p3': [('line', ['already told you'])],
    'p4': [('walk', ['walk']), ('stop', ['stop']), ('turn', ['turn', 'look'])],
    'p5': [('skate', ['skat']), ('suit', ['suit'])],
    'p6': [('rabbit', ['rabbit']), ('window', ['window'])],
}
TOTAL_ELEMENTS = sum(len(v) for v in ELEMENTS.values())     # 12

LEVEL = re.compile(r'^c_(.+)_(p\d)$')


def load(path):
    """{case_id: output} from a concatenated run file."""
    out = {}
    for r in parse_records(pathlib.Path(path).read_text(encoding='utf-8')):
        _, cid = head_parts(r['model'])
        if cid:
            out[cid] = r['output']
    return out


def context(text, at, stem, width=34):
    """The matched text with a little either side, so a hit can be eyeballed."""
    lo = max(0, at - width)
    hi = min(len(text), at + len(stem) + width)
    return ('...' if lo else '') + text[lo:hi].replace('\n', ' ') + ('...' if hi < len(text) else '')


def score_case(case, out):
    """[(element, hit, evidence)] for one composer output."""
    low = out.lower()
    rows = []
    for name, stems in ELEMENTS[case]:
        hit, ev = False, None
        for stem in stems:
            at = low.find(stem)
            if at != -1:
                hit, ev = True, context(out, at, stem)
                break
        rows.append((name, hit, ev))
    return rows


def analyse(run, prefix):
    """(summary, per-case rows) for one level of one run file."""
    cur = load(run)
    cases, npass, ntot = {}, 0, 0
    for cid, out in cur.items():
        m = LEVEL.match(cid)
        if not m or f'c_{m.group(1)}_' != prefix:
            continue
        case = m.group(2)
        if case not in ELEMENTS:
            continue
        rows = score_case(case, out)
        got = sum(1 for _, h, _ in rows if h)
        cases[case] = {'id': cid, 'covered': got, 'specified': len(rows), 'chars': len(out.strip()),
                       'elements': [{'element': n, 'hit': h, 'evidence': e} for n, h, e in rows]}
        npass += got
        ntot += len(rows)
    return ({'covered': npass, 'specified': ntot,
             'missing': [f'{c}:{e["element"]}' for c, d in sorted(cases.items())
                         for e in d['elements'] if not e['hit']]}, cases)


def levels_in(run):
    seen = []
    for cid in load(run):
        m = LEVEL.match(cid)
        if m and m.group(1) not in seen:
            seen.append(m.group(1))
    return seen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('run')
    ap.add_argument('--prefix', help='e.g. c_L0_')
    ap.add_argument('--all', action='store_true', help='every level found in the file')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()

    prefixes = ([f'c_{l}_' for l in levels_in(a.run)] if a.all
                else [a.prefix] if a.prefix else None)
    if not prefixes:
        raise SystemExit('ERROR: pass --prefix c_<level>_ or --all')

    result = {}
    for pref in prefixes:
        summary, cases = analyse(a.run, pref)
        result[pref] = {'summary': summary, 'cases': cases}
        if a.json:
            continue
        print(f'{pref:<12} coverage {summary["covered"]}/{summary["specified"]}'
              + (f'   MISSING: {", ".join(summary["missing"])}' if summary['missing'] else ''))
        for case, d in sorted(cases.items()):
            for e in d['elements']:
                if not e['hit']:
                    print(f'    {case} missing {e["element"]!r}')
    if a.json:
        print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
