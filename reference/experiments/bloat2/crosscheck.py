#!/usr/bin/env python3
"""Cross-check the two classify_tokens implementations against each other.

Side experiment: .claude/handoffs/SIDE_HANDOFF_bloat_calibration2.md, § Changed under you, item 2.

Round 1 wrote classify_tokens in signature.py because validate.py could not see an invented field
token -- it passed a record containing '[[CONTINGENCY]] none' silently, since all eight required
fields were present, once each, in order. That gap was closed in commit 1322269: scripts/validate.py
now has its own classify_tokens(), and the two implementations coexist.

They should agree. If they ever disagree, one has drifted, and the handoff asks for that to be
said out loud rather than quietly resolved. This runs both over every record in a run file and
prints any disagreement.

TWO DIFFERENCES ARE KNOWN AND EXPECTED, and are reported separately from real drift:

  1. TUPLE ORDER. signature.classify_tokens returns (near, foreign, unknown);
     validate.classify_tokens returns (foreign, near, unknown). Same three buckets, different
     order. This script normalises by name, never by position.
  2. [[SUBJECT NOT FOUND]]. validate.py exempts that token because it has its own dedicated
     checks for it further down; signature.py does not, so it reports it as 'unknown'. For the
     setting role this cannot fire in a correct record -- the role's not_found flag is False, so
     validate.py errors on it anyway by a different route -- but it would show up here as a
     disagreement, and it is not drift.

  python reference/experiments/bloat2/crosscheck.py <run.txt> --role setting
"""
import argparse
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
assert ROOT.name == 'h3-prompt-rewriter' and (ROOT / '.git').is_dir(), \
    f'ROOT resolved to {ROOT} -- refusing to run outside the project'
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'reference' / 'experiments' / 'bloat'))     # round 1, READ ONLY

import validate                                          # noqa: E402 -- imported, never modified
import signature                                         # noqa: E402 -- round 1's, never modified

NOT_FOUND_NAME = validate.NOT_FOUND_NAME


def bare(entries):
    """Both sides decorate near-misses differently ('X (~Y)' vs {'X': 'Y'}). Compare bare names."""
    if isinstance(entries, dict):
        return sorted(entries)
    return sorted(e.split(' (~')[0] for e in entries)


def compare(out, role):
    s_near, s_foreign, s_unknown = signature.classify_tokens(out, role)
    v_foreign, v_near, v_unknown = validate.classify_tokens(out, role)
    # known difference 2: signature.py does not exempt [[SUBJECT NOT FOUND]]
    s_unknown = [e for e in s_unknown if e.split(' (~')[0] != NOT_FOUND_NAME]
    return {
        'near': (bare(s_near), bare(v_near)),
        'foreign': (bare(s_foreign), bare(v_foreign)),
        'unknown': (bare(s_unknown), bare(v_unknown)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('runs', nargs='+')
    ap.add_argument('--role', default='setting', choices=sorted(validate.DESCRIBER_ROLES))
    a = ap.parse_args()

    nrec, ndis, nflag = 0, 0, 0
    for run in a.runs:
        text = pathlib.Path(run).read_text(encoding='utf-8')
        for r in validate.parse_records(text):
            _, cid = validate.head_parts(r['model'])
            if not cid:
                continue
            nrec += 1
            res = compare(r['output'], a.role)
            if any(s or v for s, v in res.values()):
                nflag += 1
            bad = {k: v for k, v in res.items() if v[0] != v[1]}
            if bad:
                ndis += 1
                print(f'DISAGREE  {pathlib.Path(run).name} :: {cid}')
                for k, (s, v) in bad.items():
                    print(f'            {k}: signature.py {s}  vs  validate.py {v}')

    print(f'\n{nrec} records checked across {len(a.runs)} run file(s) · '
          f'{nflag} carried at least one non-own [[...]] token · {ndis} disagreement(s)')
    if not ndis:
        print('ok    signature.py and validate.py agree on every record -- neither has drifted')
    return 1 if ndis else 0


if __name__ == '__main__':
    sys.exit(main())
