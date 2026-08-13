#!/usr/bin/env python3
"""Score every completed run and assemble the curve tables for REPORT.md.

Side experiment: .claude/handoffs/SIDE_HANDOFF_bloat_calibration.md

  python reference/experiments/bloat/collect.py               # tables to stdout
  python reference/experiments/bloat/collect.py --json        # machine-readable

Format verdicts come from the repo's own unmodified validate.py, invoked as a subprocess:

    validate.py describer <run> --role setting     # primary probe
    validate.py h3        <sub>                    # secondary probe, one level at a time

The secondary run file holds 18 upstream describer records plus eight levels of h3 composer
records, so it is split by case-id prefix first (split_run.py) -- validate.py's h3 subcommand
has no --id-prefix and the handoff forbids adding one.

The two signatures validate.py cannot see come from signature.py: corrupted (near-miss) field
tokens, and length collapse against the same case's unpadded baseline.

Everything here is derived from the archived run files, so every number in the report can be
re-derived rather than trusted.
"""
import argparse
import collections
import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUNS = HERE / 'runs'
sys.path.insert(0, str(HERE))
import signature                                    # noqa: E402
from split_run import subset                        # noqa: E402

PASSED = re.compile(r'^(\d+)/(\d+) passed', re.M)
ERRLINE = re.compile(r'^\s+ERROR\s+(.*)$', re.M)
DRIFT = re.compile(r'^FAIL\s+(same:.*?):', re.M)
FAILCASE = re.compile(r'^\[\d+\] FAIL\s+(\S+)', re.M)

LEVELS = [3800, 3900, 4000, 4200, 4500, 5000]
PRIMARY_ARMS = ['a_end', 'b_end', 'a_mid', 'b_mid']
SECONDARY_LADDER = ['base', 'base2'] + [str(l) for l in LEVELS]

# Token counts of the padded prompts, read from the manifest so the report's x-axis is the
# MEASURED count and not the nominal target.
def token_map():
    m = json.loads((HERE / 'manifest.json').read_text(encoding='utf-8'))
    tok = {(r['prompt'], f'{r["filler"]}_{r["position"]}', r['target']): r['tokens'] for r in m}
    # the unpadded source count, so even the baseline row's x-value is measured not assumed
    tok.update({(r['prompt'], 'source', 0): r['source_tokens'] for r in m})
    return tok


def categorise(err):
    """Collapse a validate.py ERROR string into a signature bucket."""
    e = err.lower()
    for needle, bucket in (
            ('missing field', 'missing field'),
            ('appears', 'duplicated field'),
            ('out of order', 'out of order'),
            ('does not begin', 'wrong first field'),
            ('foreign field', 'foreign field'),
            ('< or >', 'reserved < >'),
            ('markdown fence', 'markdown fence'),
            ('another turn', 'turn continuation'),
            ('expected one of', 'closed vocabulary'),
            ('subject not found', 'stray tail line'),
            ('digit', 'banned digit'),
            ('shot', 'shot numbering'),
            ('timestamp', 'timestamp'),
            ('<d>', 'dialogue block'),
            ('non_diegetic', 'music field'),
            ('mood/effect', 'music field'),
            ('voiceover', 'voiceover'),
            ('stray token', 'stray token')):
        if needle in e:
            return bucket
    return 'other'


def run_validate(args):
    p = subprocess.run([sys.executable, 'scripts/validate.py'] + args,
                       cwd=ROOT, capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    if 'Traceback' in (p.stderr or ''):
        raise SystemExit(f'ERROR: validate.py crashed on {args}\n{p.stderr}')
    m = PASSED.search(p.stdout or '')
    if not m:
        raise SystemExit(f'ERROR: could not parse a score from validate.py {args}\n{p.stdout}')
    buckets = collections.Counter(categorise(e) for e in ERRLINE.findall(p.stdout or ''))
    return (int(m.group(1)), int(m.group(2)), buckets, DRIFT.findall(p.stdout or ''),
            FAILCASE.findall(p.stdout or ''))


def score_primary(tokens):
    base = RUNS / 'primary__base_1.txt'
    rows = []
    for tag in ['base_1', 'base_2'] + [f'{a}_{l}' for a in PRIMARY_ARMS for l in LEVELS]:
        run = RUNS / f'primary__{tag}.txt'
        if not run.exists():
            continue
        npass, total, buckets, drift, fails = run_validate(
            ['describer', str(run.relative_to(ROOT)).replace('\\', '/'), '--role', 'setting'])
        agg, cases = signature.analyse(
            run, baseline=base if run != base else None, role='setting')
        if tag.startswith('base'):
            arm, lvl = 'unpadded', 0
            n = tokens[('describer_setting', 'source', 0)]
        else:
            arm = tag.rsplit('_', 1)[0]
            lvl = int(tag.rsplit('_', 1)[1])
            n = tokens[('describer_setting', arm, lvl)]
        rows.append({'tag': tag, 'arm': arm, 'level': lvl, 'tokens': n,
                     'pass': npass, 'total': total, 'buckets': dict(buckets),
                     'drift_fail': drift, 'fails': fails, 'signature': agg,
                     'flagged': [c for c in cases
                                 if c['near_miss'] or c['unknown']
                                 or (c['ratio'] is not None
                                     and c['ratio'] < signature.COLLAPSE)]})
    return rows


def score_secondary(tokens):
    rows = []
    for arm in ('img', 'noimg'):
        run = RUNS / f'secondary__{arm}.txt'
        if not run.exists():
            continue
        text = run.read_text(encoding='utf-8')
        tmp = HERE / 'runs' / '_split'
        tmp.mkdir(exist_ok=True)
        for level in SECONDARY_LADDER:
            prefix = f'c_{level}_'
            body = subset(text, prefix)
            if not body:
                continue
            sub = tmp / f'{arm}__{level}.txt'
            sub.write_text(body, encoding='utf-8')
            npass, total, buckets, _, fails = run_validate(
                ['h3', str(sub.relative_to(ROOT)).replace('\\', '/')])
            # Every level is length-compared against this SAME arm's unpadded level, per the
            # handoff: the two arms are never compared against each other in absolute terms.
            # The base level therefore compares against itself and reads 1.00, which is a
            # useful check that the keying is right.
            agg, cases = signature.analyse(
                run, baseline=run, h3=True, prefix=prefix, base_prefix='c_base_')
            n = (tokens[('fl2va', 'source', 0)] if level in ('base', 'base2')
                 else tokens[('fl2va', 'a_end', int(level))])
            rows.append({'arm': arm, 'level': level, 'tokens': n,
                         'pass': npass, 'total': total, 'buckets': dict(buckets),
                         'fails': fails, 'signature': agg,
                         'flagged': [c for c in cases
                                     if c['near_miss'] or c['unknown']
                                     or (c['ratio'] is not None
                                         and c['ratio'] < signature.COLLAPSE)]})
    return rows


def curve_table(rows, arms, label='arm', field=None):
    """Format score per (arm, level), arms as columns.

    Rows are keyed on the NOMINAL level, not the measured token count: the four arms land a few
    tokens apart inside the +/-25 window (3,784 vs 3,792 for the same 3,800 target), so keying
    on the measured count would give every arm its own row and there would be nothing to compare
    across. The measured spread is shown in its own column so nothing is hidden by that choice.
    """
    by = {(r[label], r['level']): r for r in rows}
    levels = sorted({r['level'] for r in rows}, key=lambda l: (isinstance(l, str), l))
    w = max([len(a) for a in arms] + [5])
    out = ['| level | measured tokens | ' + ' | '.join(f'{a:<{w}}' for a in arms) + ' |',
           '|---|---|' + '|'.join('---' for _ in arms) + '|']
    for lv in levels:
        got = [by[(a, lv)] for a in arms if (a, lv) in by]
        ns = sorted({g['tokens'] for g in got})
        span = f'{ns[0]}' if len(ns) == 1 else f'{ns[0]}–{ns[-1]}'
        cells = []
        for a in arms:
            r = by.get((a, lv))
            if not r:
                cells.append('—')
            elif field:
                cells.append(str(r['signature'][field]))
            else:
                cells.append(f'{r["pass"]}/{r["total"]}')
        out.append(f'| {lv} | {span} | ' + ' | '.join(f'{c:<{w}}' for c in cells) + ' |')
    return '\n'.join(out)


def failure_tally(rows):
    """Which cases fail, in how many runs, and at which token counts.

    This is the load-bearing table when the curve turns out flat. A format failure that appears
    in a couple of runs scattered across the token range is a MARGINAL CASE, not a length
    effect: the same case flipping verdict at 2,939 and again at 3,784 while passing at 4,982
    cannot be explained by length. Distinguishing that from a genuine cliff is the whole point
    of the experiment, so it is computed rather than eyeballed.
    """
    seen = collections.defaultdict(list)
    for r in rows:
        for cid in r.get('fails') or []:
            seen[cid].append((r['tag'], r['tokens']))
    out = ['| case | failing runs | token counts where it failed |', '|---|---|---|']
    for cid, hits in sorted(seen.items(), key=lambda kv: -len(kv[1])):
        counts = ', '.join(str(t) for _, t in sorted(hits, key=lambda h: h[1]))
        out.append(f'| `{cid}` | {len(hits)} / {len(rows)} | {counts} |')
    if not seen:
        out.append('| *(none)* | 0 | — |')
    return '\n'.join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()

    tokens = token_map()
    primary = score_primary(tokens)
    secondary = score_secondary(tokens)

    if a.json:
        print(json.dumps({'primary': primary, 'secondary': secondary}, indent=2))
        return 0

    print('=' * 78)
    print('PRIMARY PROBE — describer_setting, 26 images, validate.py describer --role setting')
    print('=' * 78)
    for r in primary:
        s = r['signature']
        print(f'{r["tag"]:<14} {r["tokens"]:>5} tok  format {r["pass"]}/{r["total"]:<3} '
              f'near-miss {s["near_miss"]:<3} unknown {s["unknown"]:<3} '
              f'collapsed {s["collapsed"]:<3} len {s["mean_ratio"] or "-"}')
        if r['buckets']:
            print(f'{"":<14} errors: ' + ', '.join(f'{k} x{v}'
                                                   for k, v in sorted(r['buckets'].items())))
        if r['drift_fail']:
            print(f'{"":<14} DRIFT FAIL: {r["drift_fail"]}')

    print()
    print(curve_table([r for r in primary if r['arm'] != 'unpadded'], PRIMARY_ARMS))
    print('\nlength-collapse count (cases under 70% of their unpadded baseline):')
    print(curve_table([r for r in primary if r['arm'] != 'unpadded'], PRIMARY_ARMS,
                      field='collapsed'))
    print('\nwhich cases actually failed format, across all primary runs:')
    print(failure_tally(primary))

    print()
    print('=' * 78)
    print('SECONDARY PROBE — fl2va composer, 6 cases, validate.py h3')
    print('=' * 78)
    for r in secondary:
        s = r['signature']
        print(f'{r["arm"]:<6} {r["level"]:<6} {r["tokens"]:>5} tok  '
              f'format {r["pass"]}/{r["total"]:<3} near-miss {s["near_miss"]:<3} '
              f'collapsed {s["collapsed"]:<3} len {s["mean_ratio"] or "-"}')
        if r['buckets']:
            print(f'{"":<20} errors: ' + ', '.join(f'{k} x{v}'
                                                   for k, v in sorted(r['buckets'].items())))
    if secondary:
        print()
        print(curve_table(secondary, ['img', 'noimg']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
