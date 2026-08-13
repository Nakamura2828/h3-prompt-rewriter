#!/usr/bin/env python3
"""Score every completed cell and assemble the curve tables for REPORT.md.

Side experiment: .claude/handoffs/SIDE_HANDOFF_bloat_calibration2.md

  python .claude/experiments/bloat2/collect2.py            # tables to stdout
  python .claude/experiments/bloat2/collect2.py --json     # machine-readable

Format verdicts come from the repo's own UNMODIFIED validate.py, invoked as a subprocess:

    validate.py describer <run> --role setting      # setting probe
    validate.py h3        <sub>                     # fl2va probe, one level at a time

The fl2va run file holds 18 upstream describer records plus nine levels of h3 composer records,
so it is split by case-id prefix first (round 1's split_run.py) -- validate.py's h3 subcommand has
no --id-prefix and the handoff forbids adding one.

CONTENT comes from coverage.py (fl2va action coverage) and items.py (setting item counts), and
the two signatures validate.py cannot see come from round 1's signature.py. Everything is derived
from the archived run files, so every number in the report is re-derivable rather than trusted.

The x-axis is LIVE-RULE TOKENS, read from manifest.json's measured values -- not the nominal
target -- with total tokens shown alongside to make constancy visible rather than claimed.
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
assert ROOT.name == 'h3-prompt-rewriter' and (ROOT / '.git').is_dir(), \
    f'ROOT resolved to {ROOT} -- refusing to run outside the project'
RUNS = HERE / 'runs'
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / '.claude' / 'experiments' / 'bloat'))     # round 1, READ ONLY
import signature                                          # noqa: E402 -- round 1's, unmodified
from split_run import subset                              # noqa: E402 -- round 1's, unmodified
import coverage as cov                                    # noqa: E402
import items as itm                                       # noqa: E402

PASSED = re.compile(r'^(\d+)/(\d+) passed', re.M)
ERRLINE = re.compile(r'^\s+ERROR\s+(.*)$', re.M)
DRIFT = re.compile(r'^FAIL\s+(same:.*?):', re.M)
FAILCASE = re.compile(r'^\[\d+\] FAIL\s+(\S+)', re.M)

SETTING_ORDER = ['s_L0', 's_L0b',
                 's_R2700', 's_R3100', 's_R3400', 's_R3800',
                 's_N2700', 's_N3100', 's_N3400', 's_N3800',
                 's_NF3400']
FL2VA_ORDER = ['L0', 'L0b', 'R3100', 'R3400', 'R3800', 'N3100', 'N3400', 'N3800', 'NF3400']


def prompt_tag(run_tag):
    """'s_R2700' -> 'R2700'; 's_L0b' -> 'L0'; 'L0b' -> 'L0'."""
    t = run_tag[2:] if run_tag.startswith('s_') else run_tag
    return 'L0' if t.startswith('L0') else t


def token_map():
    m = json.loads((HERE / 'manifest.json').read_text(encoding='utf-8'))
    return {(r['prompt'], r['tag']): r for r in m}


def arm_of(tag):
    t = prompt_tag(tag)
    return 'L0' if t == 'L0' else re.match(r'^(NF|R|N)', t).group(1)


def categorise(err):
    e = err.lower()
    for needle, bucket in (
            ('missing field', 'missing field'), ('appears', 'duplicated field'),
            ('out of order', 'out of order'), ('does not begin', 'wrong first field'),
            ('foreign field', 'foreign field'), ('corrupted field', 'CORRUPTED field'),
            ('invented field', 'INVENTED field'), ('< or >', 'reserved < >'),
            ('markdown fence', 'markdown fence'), ('another turn', 'turn continuation'),
            ('expected one of', 'closed vocabulary'), ('subject not found', 'stray tail line'),
            ('digit', 'banned digit'), ('shot', 'shot numbering'), ('timestamp', 'timestamp'),
            ('<d>', 'dialogue block'), ('non_diegetic', 'music field'),
            ('mood/effect', 'music field'), ('voiceover', 'voiceover'),
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
    return (int(m.group(1)), int(m.group(2)),
            collections.Counter(categorise(e) for e in ERRLINE.findall(p.stdout or '')),
            DRIFT.findall(p.stdout or ''), FAILCASE.findall(p.stdout or ''))


def score_setting(tok):
    base = RUNS / 'setting__s_L0.txt'
    rows = []
    for tag in SETTING_ORDER:
        run = RUNS / f'setting__{tag}.txt'
        if not run.exists():
            continue
        npass, total, buckets, drift, fails = run_validate(
            ['describer', str(run.relative_to(ROOT)).replace('\\', '/'), '--role', 'setting'])
        sig, cases = signature.analyse(run, baseline=base if run != base else None, role='setting')
        content, _ = itm.analyse(run, baseline=base if run != base else None)
        m = tok[('describer_setting', prompt_tag(tag))]
        rows.append({'tag': tag, 'arm': arm_of(tag), 'live': m['live_tokens'],
                     'total': m['total_tokens'], 'inert': m['inert_tokens'],
                     'rule_units': m['rule_units'],
                     'pass': npass, 'of': total, 'buckets': dict(buckets),
                     'drift_fail': drift, 'fails': fails,
                     'signature': sig, 'content': content,
                     'flagged': [c for c in cases if c['near_miss'] or c['unknown']]})
    return rows


def score_fl2va(tok):
    run = RUNS / 'fl2va__f_img.txt'
    if not run.exists():
        return []
    text = run.read_text(encoding='utf-8')
    tmp = RUNS / '_split'
    tmp.mkdir(exist_ok=True)
    rows = []
    for level in FL2VA_ORDER:
        prefix = f'c_{level}_'
        body = subset(text, prefix)
        if not body:
            continue
        sub = tmp / f'{level}.txt'
        sub.write_text(body, encoding='utf-8')
        npass, total, buckets, _, fails = run_validate(
            ['h3', str(sub.relative_to(ROOT)).replace('\\', '/')])
        sig, cases = signature.analyse(run, baseline=run, h3=True,
                                       prefix=prefix, base_prefix='c_L0_')
        summary, ccases = cov.analyse(run, prefix)
        m = tok[('fl2va', prompt_tag(level))]
        rows.append({'tag': level, 'arm': arm_of(level), 'live': m['live_tokens'],
                     'total': m['total_tokens'], 'inert': m['inert_tokens'],
                     'rule_units': m['rule_units'],
                     'pass': npass, 'of': total, 'buckets': dict(buckets), 'fails': fails,
                     'signature': sig, 'coverage': summary, 'cases': ccases,
                     'flagged': [c for c in cases if c['near_miss'] or c['unknown']]})
    return rows


# ---------------------------------------------------------------- tables

def curve(rows, cell, title):
    """Rows are live-rule levels; columns are arms. The L0 control spans the arms as one row."""
    arms = [a for a in ('R', 'N', 'NF') if any(r['arm'] == a for r in rows)]
    by = {(r['arm'], r['live']): r for r in rows}
    lives = sorted({r['live'] for r in rows})
    w = max([len(a) for a in arms] + [9])
    out = [title,
           '| live-rules | total | ' + ' | '.join(f'{a:<{w}}' for a in arms) + ' |',
           '|---|---|' + '|'.join('---' for _ in arms) + '|']
    for lv in lives:
        got = [r for r in rows if r['live'] == lv]
        totals = sorted({r['total'] for r in got})
        span = str(totals[0]) if len(totals) == 1 else f'{totals[0]}-{totals[-1]}'
        if got[0]['arm'] == 'L0':
            # L0 is ONE shared control, run twice for the noise floor. Both arms' ladders start
            # from it, so its value is repeated across every arm column rather than left ragged;
            # the twin pair is reported separately, per-cell, above.
            vals = ' / '.join(cell(g) for g in got)
            out.append(f'| **{lv}** *(L0 control, x{len(got)})* | {span} | '
                       + ' | '.join(f'{vals:<{w}}' for _ in arms) + ' |')
            continue
        cells = [cell(by[(a, lv)]) if (a, lv) in by else '—' for a in arms]
        out.append(f'| {lv} | {span} | ' + ' | '.join(f'{c:<{w}}' for c in cells) + ' |')
    return '\n'.join(out)


def failure_tally(rows):
    seen = collections.defaultdict(list)
    for r in rows:
        for cid in r.get('fails') or []:
            seen[cid].append((r['tag'], r['live']))
    out = ['| case | failing cells | live-rule counts where it failed |', '|---|---|---|']
    for cid, hits in sorted(seen.items(), key=lambda kv: -len(kv[1])):
        out.append(f'| `{cid}` | {len(hits)} / {len(rows)} | '
                   + ', '.join(str(n) for _, n in sorted(hits, key=lambda h: h[1])) + ' |')
    if not seen:
        out.append('| *(none)* | 0 | — |')
    return '\n'.join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()

    tok = token_map()
    setting = score_setting(tok)
    fl2va = score_fl2va(tok)

    if a.json:
        print(json.dumps({'setting': setting, 'fl2va': fl2va}, indent=2))
        return 0

    print('=' * 90)
    print('SETTING PROBE — describer_setting, 26 images')
    print('=' * 90)
    for r in setting:
        s, c = r['signature'], r['content']
        print(f'{r["tag"]:<10} live {r["live"]:>5}  total {r["total"]:>5}  '
              f'{r["rule_units"]:>3} rule units | format {r["pass"]}/{r["of"]:<3} | '
              f'items {c["items"]:>4}'
              + (f' ({c["delta_items"]:+d})' if c['delta_items'] is not None else '     ')
              + f' | corrupt {s["near_miss"]} invented {s["unknown"]} '
                f'collapsed {s["collapsed"]} len {s["mean_ratio"] or "-"}')
        if r['buckets']:
            print(f'{"":<10} errors: '
                  + ', '.join(f'{k} x{v}' for k, v in sorted(r['buckets'].items())))
        if r['drift_fail']:
            print(f'{"":<10} DRIFT FAIL: {r["drift_fail"]}')
        if r['content']['new_none']:
            print(f'{"":<10} NEW "none": {", ".join(r["content"]["new_none"])}')

    if setting:
        print()
        print(curve(setting, lambda r: f'{r["pass"]}/{r["of"]}',
                    'FORMAT — describer_setting'))
        print()
        print(curve(setting, lambda r: str(r['content']['items']),
                    'CONTENT — total items in STRUCTURE + CONTENTS + DISTINGUISHING'))
        print('\nwhich cases failed format, across all setting cells:')
        print(failure_tally(setting))

    print()
    print('=' * 90)
    print('FL2VA PROBE — composer, 6 cases, action coverage out of 12 elements')
    print('=' * 90)
    for r in fl2va:
        s, c = r['signature'], r['coverage']
        print(f'{r["tag"]:<10} live {r["live"]:>5}  total {r["total"]:>5}  '
              f'{r["rule_units"]:>3} rule units | format {r["pass"]}/{r["of"]:<3} | '
              f'coverage {c["covered"]}/{c["specified"]} | '
              f'corrupt {s["near_miss"]} collapsed {s["collapsed"]} '
              f'len {s["mean_ratio"] or "-"}')
        if c['missing']:
            print(f'{"":<10} missing: {", ".join(c["missing"])}')
        if r['buckets']:
            print(f'{"":<10} errors: '
                  + ', '.join(f'{k} x{v}' for k, v in sorted(r['buckets'].items())))
    if fl2va:
        print()
        print(curve(fl2va, lambda r: f'{r["pass"]}/{r["of"]}', 'FORMAT — fl2va composer'))
        print()
        print(curve(fl2va, lambda r: f'{r["coverage"]["covered"]}/12',
                    'CONTENT — action coverage'))
        print('\nwhich cases failed format, across all fl2va cells:')
        print(failure_tally(fl2va))
    return 0


if __name__ == '__main__':
    sys.exit(main())
