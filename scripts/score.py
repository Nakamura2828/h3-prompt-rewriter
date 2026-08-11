#!/usr/bin/env python3
"""Score a run's CONTENT against a test file's `_expected` answer key.

This is the second of two failure pipelines, and the two must not be conflated:

  scripts/validate.py  -> FORMAT.  Does the record have the right fields, in the right
                          order, with no reserved characters? Cannot see content at all.
  scripts/score.py     -> CONTENT. Did the model say the right thing? Needs an answer
                          key, which validate.py never reads.

Only the counts printed here feed the adjudication thresholds in `.claude/CLAUDE.md`.
Format failures are reported separately and are never part of `F`.

The `_expected` map lives at the top level of the test file, keyed by case id:

    "_expected": {
      "sty_coraline1": "stop-motion / none",
      "sty_chair":     "UNSCORABLE (amb) -- the pixels do not settle photo vs render",
      "sty_kasia":     "2D cel / (sub CONTESTED -- score the coarse term only)"
    }

Two markers drop a case out of the denominator, and they mean different things:

  UNSCORABLE  the IMAGE does not determine the answer. Permanent -- pixels don't change.
  CONTESTED   OUR DEFINITIONS cannot decide a decidable image. PROVISIONAL: the ruling
              expires when the vocabulary that made it contested changes, and the case
              must re-enter scoring rather than staying excluded forever.

A marker may appear on the whole value or on one field, e.g.
"2D cel / (sub CONTESTED)" scores the coarse term and excludes the sub-term only.

Usage:
  python scripts/score.py tests/describer_style.json runs/run-*.txt
  python scripts/score.py tests/describer_style_sweep.json <run> --fields MEDIUM SUB_MEDIUM
  python scripts/score.py <test> <run> --misses-only
"""

import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from validate import parse_records, head_parts          # noqa: E402

MARKERS = ('UNSCORABLE', 'CONTESTED')


def field(output, name):
    m = re.search(r'\[\[' + re.escape(name) + r'\]\](.*)', output)
    return m.group(1).strip() if m else '(missing)'


def split_expected(raw, n_fields):
    """An `_expected` value -> per-field expectations, or a whole-record marker.

    Returns (marker, [per-field expectation, ...]). `marker` is set only when the
    WHOLE record is excluded; a per-field marker stays in the list so the other
    fields still score."""
    for mk in MARKERS:
        # whole-record only when the marker leads the value -- "UNSCORABLE (amb)".
        if raw.strip().upper().startswith(mk):
            return mk, []
    parts = [p.strip() for p in raw.split('/')]
    # Tolerate an expectation that names fewer fields than we are scoring.
    parts += ['(unspecified)'] * (n_fields - len(parts))
    return None, parts[:n_fields]


def marker_in(text):
    for mk in MARKERS:
        if mk in text.upper():
            return mk
    return None


def clean(expectation):
    """Drop a trailing parenthetical note so it cannot contaminate the comparison.

    `_expected` values carry rationale inline -- "photograph / colour  (tie-break 2:
    a photograph OF a watercolour)" -- and splitting on "/" leaves that note glued to
    the last field. Only called after marker_in(), so a marker inside the parenthetical
    has already been honoured."""
    return re.sub(r'\s*\([^()]*\)\s*$', '', expectation).strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('test', help='test JSON carrying the _expected map')
    ap.add_argument('run', help='a concatenated runs/run-*.txt')
    ap.add_argument('--fields', nargs='+', default=['MEDIUM', 'SUB_MEDIUM'],
                    help='fields the _expected value describes, in "a / b" order')
    ap.add_argument('--misses-only', action='store_true',
                    help='omit the passing rows')
    a = ap.parse_args()

    spec = json.loads(pathlib.Path(a.test).read_text(encoding='utf-8'))
    expected = spec.get('_expected')
    if not expected:
        raise SystemExit(f'ERROR: {a.test} has no top-level "_expected" map -- '
                         f'nothing to score against.')

    got = {}
    for r in parse_records(pathlib.Path(a.run).read_text(encoding='utf-8')):
        _, cid = head_parts(r['model'])
        if cid:
            got[cid] = tuple(field(r['output'], f) for f in a.fields)

    rows, excluded = [], []
    field_contested = set()
    n_pass = n_miss = 0
    per_field_excluded = 0

    for cid, raw in expected.items():
        if cid not in got:
            excluded.append((cid, 'NOT RUN', raw))
            continue
        marker, want = split_expected(raw, len(a.fields))
        if marker:
            excluded.append((cid, marker, ' / '.join(got[cid])))
            continue

        verdicts = []
        for w, g in zip(want, got[cid]):
            mk = marker_in(w)
            if mk or w == '(unspecified)':
                verdicts.append(None)                    # field excluded
                per_field_excluded += 1
                if mk == 'CONTESTED':
                    field_contested.add(cid)
            else:
                verdicts.append(g.strip().lower() == clean(w).lower())

        scored = [v for v in verdicts if v is not None]
        if not scored:
            excluded.append((cid, 'CONTESTED', ' / '.join(got[cid])))
            continue
        ok = all(scored)
        n_pass += ok
        n_miss += not ok
        if not ok or not a.misses_only:
            rows.append((cid, ' / '.join(got[cid]), raw, ok))

    w = max((len(c) for c, *_ in rows + excluded), default=10)
    for cid, g, e, ok in rows:
        print(f'{"ok " if ok else "MISS"}  {cid:{w}}  {g:34}  expected {e}')

    if excluded:
        print()
        for cid, why, g in excluded:
            print(f'skip  {cid:{w}}  {g:34}  [{why}]')

    n = n_pass + n_miss
    print()
    print(f'CONTENT  {n_pass}/{n} exact   ({n_miss} misses)')

    n_contested = sum(1 for _, why, _ in excluded if why == 'CONTESTED')
    n_unscorable = sum(1 for _, why, _ in excluded if why == 'UNSCORABLE')
    n_notrun = sum(1 for _, why, _ in excluded if why == 'NOT RUN')
    total = n + n_contested + n_unscorable
    print(f'excluded {len(excluded)}: {n_contested} contested · '
          f'{n_unscorable} unscorable · {n_notrun} not run'
          + (f' · {per_field_excluded} field(s) on {len(field_contested)} '
             f'partly-scored case(s)' if per_field_excluded else ''))

    if total:
        # Surfaced deliberately: a growing contested share means the vocabulary is
        # asking for a distinction the images don't support (.claude/CLAUDE.md).
        # Counts partly-contested cases too -- a contested SUB-term is still the
        # vocabulary failing to decide, which is the signal this number exists for.
        contested_any = n_contested + len(field_contested)
        print(f'contested rate  {contested_any}/{total} = '
              f'{100 * contested_any / total:.0f}% of ruled cases'
              + (f'  ({n_contested} whole, {len(field_contested)} partial)'
                 if field_contested else ''))
        print('  NOTE: contested rulings are PROVISIONAL -- they expire when the '
              'vocabulary changes.')

    threshold = max(6, round(0.15 * n))
    verdict = 'ADJUDICATION' if n_miss <= threshold else 'DIAGNOSIS'
    print(f'\ngate: F={n_miss} vs threshold max(6, 15% of {n})={threshold}  ->  {verdict}')
    if verdict == 'DIAGNOSIS':
        print('      lead with the systematic finding, and attach 2-3 exemplars')
    else:
        print(f'      bring {min(n_miss, 6)} of them'
              + (' (triage to six, one per pattern)' if n_miss > 6 else ''))
    print('      format failures are counted separately -- run scripts/validate.py')

    sys.exit(0 if n_miss == 0 else 1)


if __name__ == '__main__':
    main()
