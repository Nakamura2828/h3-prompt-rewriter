#!/usr/bin/env python3
"""The two failure signatures validate.py does not measure.

Side experiment: .claude/handoffs/SIDE_HANDOFF_bloat_calibration.md

validate.py already catches most of the token-ceiling signature: missing, duplicated and
out-of-order fields, a reply not starting with the first field, markdown fences, 'User:'
continuations, the reserved < and >. Two things it cannot see, and the handoff asks for both,
in this file rather than by editing validate.py:

1. CORRUPTED FIELD TOKENS. A misspelled token -- [[DISTINGISHING]], [[DEFINING]] -- with the
   correct content underneath is the most diagnostic signature the project has. validate.py
   reports it as 'missing field', which is true but understates it badly: three fields simply
   absent and three fields present under mangled names are very different results, and only
   the second one implicates length. So unknown [[...]] tokens are classified here:

     near-miss   close to one of this role's own fields   -> the length signature
     foreign     exactly another role's real field name   -> a different defect; validate.py
                                                             already errors on these
     unknown     neither                                  -> invented, worth seeing separately

   For the h3 contract the same idea applies to the three 'label:' lines, checked with difflib
   against the real ones.

2. LENGTH COLLAPSE. Output much shorter than the same case's unpadded baseline, while staying
   perfectly well-formed. This is how fl2va v4 failed -- it silently shed about a third of its
   length and no format checker would ever have caught it.

Also flagged, because the handoff makes them stop conditions rather than results: empty output,
and runaway output near max_tokens.

  python .claude/experiments/bloat/signature.py <run.txt> --role setting --baseline <base.txt>
  python .claude/experiments/bloat/signature.py <run.txt> --h3 --baseline <base.txt> --json
"""
import argparse
import difflib
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate import (DESCRIBER_ROLES, FIELDS, FRAME_FIELDS,   # noqa: E402
                      head_parts, parse_records)

TOKEN = re.compile(r'\[\[([^\[\]]{1,40})\]\]')
LABEL_LINE = re.compile(r'^([A-Za-z][A-Za-z_ ]{2,40}):', re.M)

# Below this fraction of the baseline length, an output is called collapsed. 0.70 is the fl2va
# v4 signature ("shed about a third"); 0.50 is reported separately as severe.
COLLAPSE = 0.70
SEVERE = 0.50
RUNAWAY_CHARS = 6000        # ~max_tokens 2048 territory; a stop condition, not a score
NEAR_MISS_RATIO = 0.75


def classify_tokens(out, role):
    """(near_miss, foreign, unknown) lists of [[...]] token names that are not this role's."""
    own = set(DESCRIBER_ROLES[role]['fields'])
    other = set(FRAME_FIELDS)
    for spec in DESCRIBER_ROLES.values():
        other.update(spec['fields'])
    other -= own

    near, foreign, unknown = [], [], []
    for name in TOKEN.findall(out):
        base = name.split(':')[0].strip()          # [[CHAR: label]] -> CHAR
        if base in own:
            continue
        if base in other:
            foreign.append(base)
            continue
        close = difflib.get_close_matches(base, own, n=1, cutoff=NEAR_MISS_RATIO)
        (near if close else unknown).append(
            f'{base} (~{close[0]})' if close else base)
    return near, foreign, unknown


def classify_h3_labels(out):
    """Near-miss versions of the three contract labels, e.g. 'integrated_multimodal_descripton:'."""
    real = [f[:-1] for f in FIELDS]
    near, unknown = [], []
    for name in LABEL_LINE.findall(out):
        n = name.strip()
        if n in real or n.lower() in ('user', 'assistant', 'input', 'output', 'note', 'usage'):
            continue
        close = difflib.get_close_matches(n, real, n=1, cutoff=NEAR_MISS_RATIO)
        if close:
            near.append(f'{n} (~{close[0]})')
        elif '_' in n:                             # only flag things shaped like a field label
            unknown.append(n)
    return near, unknown


def load(path, prefix=None):
    """{case_id: output} from a concatenated run file."""
    text = pathlib.Path(path).read_text(encoding='utf-8')
    out = {}
    for r in parse_records(text):
        _, cid = head_parts(r['model'])
        if not cid:
            continue
        if prefix and not cid.startswith(prefix):
            continue
        out[cid] = r['output']
    return out


def analyse(run, baseline=None, role=None, h3=False, prefix=None, base_prefix=None):
    cur = load(run, prefix)
    base = load(baseline, base_prefix) if baseline else {}
    rows, agg = [], {'cases': len(cur), 'near_miss': 0, 'foreign': 0, 'unknown': 0,
                     'collapsed': 0, 'severe': 0, 'empty': 0, 'runaway': 0,
                     'grew': 0, 'min_ratio': None, 'mean_ratio': None}
    ratios = []
    for cid, out in cur.items():
        if h3:
            near, unknown = classify_h3_labels(out)
            foreign = []
        else:
            near, foreign, unknown = classify_tokens(out, role)

        n = len(out.strip())
        # Baseline comparison is per CASE, keyed on the shared suffix: the secondary probe
        # renames ids per level (c_3800_p1 vs c_base_p1), so compare on the trailing part.
        bkey = cid
        if base and cid not in base and prefix and base_prefix:
            bkey = base_prefix + cid[len(prefix):]
        bn = len(base.get(bkey, '').strip()) if base else 0
        ratio = (n / bn) if bn else None
        if ratio is not None:
            ratios.append(ratio)

        row = {'id': cid, 'chars': n, 'baseline_chars': bn or None,
               'ratio': round(ratio, 3) if ratio is not None else None,
               'near_miss': near, 'foreign': foreign, 'unknown': unknown}
        rows.append(row)

        agg['near_miss'] += len(near)
        agg['foreign'] += len(foreign)
        agg['unknown'] += len(unknown)
        if n == 0:
            agg['empty'] += 1
        if n > RUNAWAY_CHARS:
            agg['runaway'] += 1
        if ratio is not None:
            if ratio < COLLAPSE:
                agg['collapsed'] += 1
            if ratio < SEVERE:
                agg['severe'] += 1
            if ratio > 1.30:
                agg['grew'] += 1

    if ratios:
        agg['min_ratio'] = round(min(ratios), 3)
        agg['mean_ratio'] = round(sum(ratios) / len(ratios), 3)
    return agg, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('run')
    ap.add_argument('--role', choices=sorted(DESCRIBER_ROLES))
    ap.add_argument('--h3', action='store_true')
    ap.add_argument('--baseline')
    ap.add_argument('--prefix')
    ap.add_argument('--base-prefix')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()
    if not (a.role or a.h3):
        raise SystemExit('ERROR: pass --role <name> or --h3')

    agg, rows = analyse(a.run, a.baseline, a.role, a.h3, a.prefix, a.base_prefix)
    if a.json:
        print(json.dumps({'summary': agg, 'cases': rows}, indent=2))
        return 0

    print(f'{a.run}   {agg["cases"]} cases')
    for r in rows:
        flags = []
        if r['near_miss']:
            flags.append('NEAR-MISS ' + ', '.join(r['near_miss']))
        if r['foreign']:
            flags.append('foreign ' + ', '.join(r['foreign']))
        if r['unknown']:
            flags.append('unknown ' + ', '.join(r['unknown']))
        if r['chars'] == 0:
            flags.append('EMPTY')
        if r['chars'] > RUNAWAY_CHARS:
            flags.append('RUNAWAY')
        if r['ratio'] is not None and r['ratio'] < COLLAPSE:
            flags.append(f'COLLAPSED to {r["ratio"]:.0%} of baseline')
        if flags:
            print(f'  {r["id"]:<28} {"; ".join(flags)}')
    print(f'\n  near-miss tokens {agg["near_miss"]} · foreign {agg["foreign"]} · '
          f'unknown {agg["unknown"]}')
    print(f'  collapsed (<{COLLAPSE:.0%}) {agg["collapsed"]} · severe (<{SEVERE:.0%}) '
          f'{agg["severe"]} · empty {agg["empty"]} · runaway {agg["runaway"]}')
    if agg['mean_ratio'] is not None:
        print(f'  length vs baseline: mean {agg["mean_ratio"]:.2f} · '
              f'min {agg["min_ratio"]:.2f}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
