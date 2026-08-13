#!/usr/bin/env python3
"""ITEM COUNT -- the describer_setting probe's content metric.

Side experiment: .claude/handoffs/SIDE_HANDOFF_bloat_calibration2.md

The handoff's design: count the distinct comma-separated items in [[STRUCTURE]], [[CONTENTS]] and
[[DISTINGUISHING]], per case, against the unpadded control. Degradation = systematically fewer
items, or 'none' where the control itemised. Crude, but it is exactly the set_p6_outside signature
round 1 found -- a perfectly well-formed record that had quietly shed its contents:

    control (893 chars): [[CONTENTS]] a section of exposed red brick wall, a tall rectangular
                         window set into the brickwork, a heavy wooden door frame with peeling
                         paint, a framed picture hanging on the interior wall
    padded  (517 chars): [[CONTENTS]] none

and it is objective, which matters more here than precision. The three fields are chosen because
they are the record's only open-ended lists; the other five are a closed word, a short phrase, or
a single clause, so a count over them would measure nothing.

KNOWN IMPRECISION, stated rather than hidden: splitting on commas over-counts an item that
contains a comma of its own and under-counts two items joined with 'and'. Both biases apply
equally at every level, so the DIFFERENCE against the control is still meaningful even though the
absolute count is not. Character length is reported alongside for exactly that reason -- it is
biased differently, so agreement between the two is worth something.

  python reference/experiments/bloat2/items.py <run.txt>
  python reference/experiments/bloat2/items.py <run.txt> --baseline <L0.txt> --json
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

FIELDS = ['STRUCTURE', 'CONTENTS', 'DISTINGUISHING']
EMPTY = ('none', 'not visible', 'n/a', '')


def load(path):
    out = {}
    for r in parse_records(pathlib.Path(path).read_text(encoding='utf-8')):
        _, cid = head_parts(r['model'])
        if cid:
            out[cid] = r['output']
    return out


def field_value(out, name):
    m = re.search(r'\[\[' + re.escape(name) + r'\]\](.*)', out)
    return m.group(1).strip() if m else None


def count_items(value):
    """Number of comma-separated items. A missing field is None; 'none' is 0."""
    if value is None:
        return None
    if value.lower().strip(' .') in EMPTY:
        return 0
    return len([p for p in (p.strip() for p in value.split(',')) if p])


def measure(out):
    per = {f: count_items(field_value(out, f)) for f in FIELDS}
    total = sum(v for v in per.values() if v is not None)
    return {'per_field': per, 'items': total,
            'nones': [f for f in FIELDS if per[f] == 0],
            'missing_fields': [f for f in FIELDS if per[f] is None],
            'chars': len(out.strip())}


def analyse(run, baseline=None):
    cur = load(run)
    base = load(baseline) if baseline else {}
    rows, tot, btot, tchars, bchars = [], 0, 0, 0, 0
    lost, gained, new_none = [], [], []
    for cid, out in cur.items():
        m = measure(out)
        b = measure(base[cid]) if cid in base else None
        row = {'id': cid, **m,
               'baseline_items': b['items'] if b else None,
               'baseline_chars': b['chars'] if b else None,
               'delta_items': (m['items'] - b['items']) if b else None,
               'ratio_chars': round(m['chars'] / b['chars'], 3) if b and b['chars'] else None}
        rows.append(row)
        tot += m['items']
        tchars += m['chars']
        if b:
            btot += b['items']
            bchars += b['chars']
            if row['delta_items'] < 0:
                lost.append((cid, row['delta_items']))
            elif row['delta_items'] > 0:
                gained.append((cid, row['delta_items']))
            for f in FIELDS:
                if m['per_field'][f] == 0 and (b['per_field'][f] or 0) > 0:
                    new_none.append(f'{cid}:{f}')
    summary = {'cases': len(rows), 'items': tot, 'baseline_items': btot or None,
               'delta_items': (tot - btot) if base else None,
               'chars': tchars, 'baseline_chars': bchars or None,
               'ratio_chars': round(tchars / bchars, 4) if bchars else None,
               'cases_lost_items': len(lost), 'cases_gained_items': len(gained),
               'new_none': new_none,
               'missing_fields': sum(len(r['missing_fields']) for r in rows)}
    return summary, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('run')
    ap.add_argument('--baseline')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()

    summary, rows = analyse(a.run, a.baseline)
    if a.json:
        print(json.dumps({'summary': summary, 'cases': rows}, indent=2))
        return 0

    print(f'{a.run}   {summary["cases"]} cases   {summary["items"]} items'
          + (f'  (baseline {summary["baseline_items"]}, '
             f'{summary["delta_items"]:+d})' if summary['baseline_items'] else ''))
    for r in sorted(rows, key=lambda r: (r['delta_items'] if r['delta_items'] is not None else 0)):
        if r['delta_items'] not in (None, 0) or r['missing_fields']:
            print(f'  {r["id"]:<24} items {r["baseline_items"]} -> {r["items"]} '
                  f'({r["delta_items"]:+d})   chars x{r["ratio_chars"]}'
                  + (f'   MISSING {r["missing_fields"]}' if r['missing_fields'] else ''))
    if summary['new_none']:
        print(f'  NEW "none" where the baseline itemised: {", ".join(summary["new_none"])}')
    if summary['ratio_chars']:
        print(f'  total length vs baseline: x{summary["ratio_chars"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
