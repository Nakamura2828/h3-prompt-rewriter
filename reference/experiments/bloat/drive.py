#!/usr/bin/env python3
"""Batch driver for the bloat calibration, with the handoff's stop conditions in code.

Side experiment: .claude/handoffs/SIDE_HANDOFF_bloat_calibration.md

  python reference/experiments/bloat/drive.py base_1 base_2
  python reference/experiments/bloat/drive.py a_end_3800 a_end_3900 a_end_4000 ...
  python reference/experiments/bloat/drive.py img            # secondary, image arm

The handoff's OVERRIDING RULE is "if it gets weird, stop and wait" -- and it outranks finishing
the experiment. That rule is unenforceable by good intentions across a 26-run unattended batch,
so it is implemented here: any trip aborts the whole batch, writes STOP.md, and exits non-zero.
No retries, no "just once more", no escalating padding to force a break, and nothing outside
this directory is ever written.

STOP CONDITIONS
  - run_tests.py exits non-zero, or 'Traceback' appears on either stream. A crash is not a result.
  - any case returns empty output (server trouble) or runs away past RUNAWAY_CHARS toward
    max_tokens.
  - any single call exceeds MAX_CASE_SECONDS.
  - mean per-call latency departs from the family's first run by more than the bounds below.
  - WALL_SECONDS since the experiment's first run have elapsed: the run in flight finishes and
    then the batch stops, so the cutoff overshoots by at most one run and everything already
    completed is still scoreable.

Latency bounds are per FAMILY because the two probes are not comparable: a 26-case describer run
and a 66-case chained composer run have different per-call costs by design, and the secondary's
text-only arm is legitimately faster than its image arm because it sends no image at all. Judging
one against the other would trip on the experiment's own independent variable.
"""
import json
import pathlib
import re
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STATE = HERE / 'state.json'
LOGS = HERE / 'logs'
RUNS = HERE / 'runs'

WALL_SECONDS = 4 * 3600          # the user's hard cutoff
MAX_CASE_SECONDS = 240
RUNAWAY_CHARS = 6000
BOUNDS = {'primary': (0.40, 2.5), 'secondary': (0.20, 3.5)}

# '[3/26] set_city_day ... 7.3s  1183 chars'
PROGRESS = re.compile(r'^\[(\d+)/(\d+)\]\s+(\S+)\s+\.\.\.\s+([\d.]+)s\s+(\d+) chars\s*$', re.M)

SECONDARY = ('img', 'noimg')


def family(tag):
    return 'secondary' if tag in SECONDARY else 'primary'


def case_file(tag):
    p = HERE / 'cases' / f'{family(tag)}__{tag}.json'
    if not p.exists():
        raise SystemExit(f'ERROR: no case file for tag {tag!r} ({p})')
    return p


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text(encoding='utf-8'))
    return {'t0': None, 'baseline_mean': {}, 'runs': {}, 'stopped': None}


def save_state(st):
    STATE.write_text(json.dumps(st, indent=2), encoding='utf-8')


def stop(st, tag, reason, detail=''):
    st['stopped'] = {'tag': tag, 'reason': reason, 'detail': detail,
                     'at': time.strftime('%Y-%m-%d %H:%M:%S')}
    save_state(st)
    (HERE / 'STOP.md').write_text(
        f'# BATCH STOPPED\n\n'
        f'- **when:** {st["stopped"]["at"]}\n'
        f'- **run in flight:** `{tag}`\n'
        f'- **reason:** {reason}\n\n'
        f'{detail}\n\n'
        f'Completed runs are listed in `state.json` and are still scoreable. Per the handoff, '
        f'nothing was retried and no setting was changed.\n', encoding='utf-8')
    print(f'\n*** STOPPED on {tag}: {reason}\n{detail}')
    return 1


def main():
    tags = sys.argv[1:]
    if not tags:
        raise SystemExit(__doc__)
    LOGS.mkdir(exist_ok=True)
    RUNS.mkdir(exist_ok=True)
    st = load_state()
    if st.get('stopped'):
        raise SystemExit(f'ERROR: batch is in a stopped state '
                         f'({st["stopped"]["reason"]}). Clear state.json deliberately, with '
                         f'the reason understood, before continuing.')
    if st['t0'] is None:
        st['t0'] = time.time()
        save_state(st)

    for tag in tags:
        elapsed = time.time() - st['t0']
        if elapsed > WALL_SECONDS:
            return stop(st, tag, f'{WALL_SECONDS / 3600:.0f}h wall-clock cutoff reached',
                        f'{elapsed / 3600:.2f}h elapsed since the first run. Refusing to start '
                        f'`{tag}`. Remaining tags: {" ".join(tags[tags.index(tag):])}')

        fam = family(tag)
        cf = case_file(tag)
        out = RUNS / f'{fam}__{tag}.txt'
        outdir = RUNS / f'{fam}__{tag}'
        log = LOGS / f'{fam}__{tag}.log'

        print(f'\n=== {tag} ({fam})  [{elapsed / 3600:.2f}h elapsed] ===', flush=True)
        t0 = time.time()
        p = subprocess.run(
            [sys.executable, 'scripts/run_tests.py', str(cf.relative_to(ROOT)).replace('\\', '/'),
             '--out', str(out.relative_to(ROOT)).replace('\\', '/'),
             '--outdir', str(outdir.relative_to(ROOT)).replace('\\', '/')],
            cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
        wall = time.time() - t0
        log.write_text((p.stdout or '') + '\n--- stderr ---\n' + (p.stderr or ''),
                       encoding='utf-8')

        blob = (p.stdout or '') + (p.stderr or '')
        if 'Traceback' in blob:
            return stop(st, tag, 'a traceback appeared -- a crash is not a result',
                        f'See `logs/{log.name}`.')
        if p.returncode != 0:
            return stop(st, tag, f'run_tests.py exited {p.returncode}',
                        f'See `logs/{log.name}`.\n\n```\n{(p.stderr or "")[-1500:]}\n```')

        hits = PROGRESS.findall(p.stdout or '')
        if not hits:
            return stop(st, tag, 'no per-case progress lines were parsed',
                        f'The harness output an unexpected shape. See `logs/{log.name}`.')
        secs = [float(h[3]) for h in hits]
        chars = [int(h[4]) for h in hits]
        ids = [h[2] for h in hits]
        mean = sum(secs) / len(secs)

        empty = [i for i, c in zip(ids, chars) if c == 0]
        runaway = [i for i, c in zip(ids, chars) if c > RUNAWAY_CHARS]
        slow = [(i, s) for i, s in zip(ids, secs) if s > MAX_CASE_SECONDS]

        rec = {'family': fam, 'cases': len(hits), 'wall_s': round(wall, 1),
               'mean_s': round(mean, 2), 'max_s': max(secs), 'min_s': min(secs),
               'mean_chars': round(sum(chars) / len(chars)),
               'run': out.name, 'at': time.strftime('%Y-%m-%d %H:%M:%S')}
        st['runs'][tag] = rec
        save_state(st)
        print(f'    {len(hits)} cases · {wall / 60:.1f} min · mean {mean:.1f}s/call · '
              f'mean {rec["mean_chars"]} chars', flush=True)

        if empty:
            return stop(st, tag, 'a case returned EMPTY output',
                        f'Empty: {", ".join(empty)}. This is a server-health signal, not a '
                        f'score. Nothing was retried.')
        if runaway:
            return stop(st, tag, 'a case ran away toward max_tokens',
                        f'Over {RUNAWAY_CHARS} chars: {", ".join(runaway)}.')
        if slow:
            return stop(st, tag, f'a single call exceeded {MAX_CASE_SECONDS}s',
                        f'{", ".join(f"{i} at {s:.0f}s" for i, s in slow)}')

        lo, hi = BOUNDS[fam]
        ref = st['baseline_mean'].get(fam)
        if ref is None:
            st['baseline_mean'][fam] = mean
            save_state(st)
            projected = mean * len(hits)
            print(f'    latency reference for {fam} set at {mean:.1f}s/call '
                  f'({projected / 60:.1f} min per run)', flush=True)
        elif not (lo * ref <= mean <= hi * ref):
            return stop(st, tag, 'per-call latency departed sharply from this family\'s '
                                 'reference',
                        f'{mean:.1f}s/call against a reference of {ref:.1f}s/call '
                        f'(allowed {lo * ref:.1f}-{hi * ref:.1f}). The handoff makes this a '
                        f'stop condition in EITHER direction. Server was not touched.')

    print(f'\nall {len(tags)} run(s) complete · '
          f'{(time.time() - st["t0"]) / 3600:.2f}h elapsed overall')
    return 0


if __name__ == '__main__':
    sys.exit(main())
