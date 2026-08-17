#!/usr/bin/env python3
"""Archive and clean up run_tests.py output.

Usage:
  python scripts/archive_run.py rename   <dest>      [--run PATH] [--clean] [--dry-run]
  python scripts/archive_run.py baseline <test-name> [--run PATH] [--dry-run]
  python scripts/archive_run.py clean [--current] [--dry-run]

rename moves the most recently modified runs/run-*.txt (or --run PATH) to
reference/test_archive/<dest>.txt, e.g.:

  python scripts/archive_run.py rename FL2VA/Describer-FL2VA-Comparison

If that destination already exists, -2, -3, ... is appended until a free name
is found — existing archived rounds are never overwritten.

baseline COPIES that same run to reference/baselines/<test-name>.txt, and is a
different job from rename. An archived round is history: write-once, grouped by
phase, never overwritten. A baseline is the single run the NEXT round is scored
against — read every round, replaced when it advances. Filing it only as history
means score.py --baseline points at a filename that changes every round; this
gives it one that doesn't:

  python scripts/archive_run.py baseline describer_style_sweep130_frozen
  python scripts/score.py tests/describer_style_sweep130_frozen.json runs/run-<new>.txt \
      --fields MEDIUM SUB_MEDIUM IDIOM TREATMENT \
      --baseline reference/baselines/describer_style_sweep130_frozen.txt

Overwriting is the point here, so unlike rename there is no -2/-3 suffixing. Run
both when a round becomes the new baseline: baseline first (it copies), then
rename (it moves).

clean deletes files from runs/:
  (no flag)   delete everything in runs/
  --current   delete only the runs/<id>.txt files for case ids found in the
              most recently modified runs/run-*.txt still present in runs/;
              that run-*.txt itself and any other files are left alone

rename --clean is shorthand for: archive the run, then delete the
runs/<id>.txt files for the case ids in the file that was just archived.

Note on cleanup: every clean path here is scoped to runs/, so a baseline copy is
never at risk from one -- that is part of why baseline copies rather than moves.
Pruning reference/baselines/ itself has no mechanism yet; a baseline is replaced
by the next baseline call and is otherwise only stale if its test is retired.
"""
import argparse, pathlib, re, shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
RUNS = ROOT / 'runs'
ARCHIVE = ROOT / 'reference' / 'test_archive'
BASELINES = ROOT / 'reference' / 'baselines'
ID_RE = re.compile(r'\[(?:.+? :: )?([^\]]+)\]\s*$')


def latest_run(explicit=None):
    if explicit:
        p = pathlib.Path(explicit)
        if not p.is_file():
            raise SystemExit(f'ERROR: {p} not found')
        return p
    candidates = sorted(RUNS.glob('run-*.txt'), key=lambda p: p.stat().st_mtime)
    if not candidates:
        raise SystemExit(f'ERROR: no run-*.txt files in {RUNS}/')
    return candidates[-1]


def record_ids(text):
    """Pull case ids out of a concatenated run file's record headers, e.g.
    'qwen3.6-35b-a3b  [p1_first]' or 'qwen3.6-35b-a3b  [group :: p1_first]'.
    Group-banner lines ('##### group #####') don't match and are skipped."""
    ids = []
    for record in text.replace('\r\n', '\n').split('\n----------\n'):
        head = record.strip().split('\n', 1)[0]
        m = ID_RE.search(head)
        if m:
            ids.append(m.group(1))
    return ids


def resolve_dest(dest):
    base = ARCHIVE / f'{dest}.txt'
    if not base.exists():
        return base
    n = 2
    while True:
        candidate = ARCHIVE / f'{dest}-{n}.txt'
        if not candidate.exists():
            return candidate
        n += 1


def delete_ids(ids, dry_run):
    removed = 0
    for i in ids:
        p = RUNS / f'{i}.txt'
        if p.is_file():
            print(f'{"[dry-run] " if dry_run else ""}delete {p}')
            if not dry_run:
                p.unlink()
            removed += 1
    print(f'{removed} per-case file(s) {"would be " if dry_run else ""}removed')


def cmd_rename(a):
    src = latest_run(a.run)
    if a.clean and not (a.adjudicated or a.dry_run):
        raise SystemExit(
            'REFUSING to --clean without --adjudicated.\n'
            '\n'
            '  --clean deletes the per-case runs/<id>.txt files, and those are where the\n'
            "  model's own descriptive lines live. .claude/CLAUDE.md requires adjudication\n"
            '  BEFORE this point precisely because recovering them afterwards means digging\n'
            '  them back out of the archived concatenated run.\n'
            '\n'
            '  Score the run and work the gate first:\n'
            f'    python scripts/score.py <test>.json {src.as_posix()}\n'
            '\n'
            '  Then re-run this with --adjudicated. Pass it straight away only when the run\n'
            '  needs no adjudication at all -- a validity check, a smoke test, a re-run you\n'
            '  have already ruled on.')
    dest = resolve_dest(a.dest)
    print(f'{"[dry-run] " if a.dry_run else ""}{src} -> {dest}')
    if not a.dry_run:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
    if a.clean:
        text = (src if a.dry_run else dest).read_text(encoding='utf-8')
        delete_ids(record_ids(text), a.dry_run)


def cmd_baseline(a):
    """Copy, don't move: the run usually still needs archiving as history afterwards,
    and a baseline that lives only here would be lost the moment it is superseded."""
    src = latest_run(a.run)
    dest = BASELINES / f'{a.test}.txt'
    verb = 'replace' if dest.exists() else 'create'
    print(f'{"[dry-run] " if a.dry_run else ""}{src} -> {dest}  ({verb})')
    if not a.dry_run:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src), str(dest))
    print(f'score against it with:\n'
          f'  python scripts/score.py tests/{a.test}.json runs/run-<new>.txt '
          f'--baseline reference/baselines/{a.test}.txt')


def cmd_clean(a):
    if a.current:
        src = latest_run()
        delete_ids(record_ids(src.read_text(encoding='utf-8')), a.dry_run)
        return
    files = sorted(RUNS.glob('*.txt'))
    if not files:
        print('runs/ already empty')
        return
    for f in files:
        print(f'{"[dry-run] " if a.dry_run else ""}delete {f}')
        if not a.dry_run:
            f.unlink()
    print(f'{len(files)} file(s) {"would be " if a.dry_run else ""}removed')


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='command', required=True)

    r = sub.add_parser('rename', help='archive the latest run-*.txt into reference/test_archive/')
    r.add_argument('dest', help='destination path under reference/test_archive/, without '
                                 'extension, e.g. FL2VA/Describer-FL2VA-Comparison')
    r.add_argument('--run', help='archive this specific file instead of the most recently '
                                  'modified runs/run-*.txt')
    r.add_argument('--clean', action='store_true',
                    help="also delete this run's per-case runs/<id>.txt files after archiving. "
                         'Requires --adjudicated, because those files are the evidence '
                         'adjudication reads')
    r.add_argument('--adjudicated', action='store_true',
                    help='confirm the run has been scored and its gate verdict worked (or that '
                         'it needs no adjudication -- a validity check, a smoke test). Required '
                         'by --clean. The guard exists because the gate was skipped in two '
                         'consecutive sessions despite score.py printing it correctly every '
                         'time; a rule missed twice needs a mechanism, not more prose')
    r.add_argument('--dry-run', action='store_true')
    r.set_defaults(func=cmd_rename)

    b = sub.add_parser('baseline',
                        help='copy the latest run-*.txt into reference/baselines/ as the '
                             'comparison point for the next round')
    b.add_argument('test', help='the test this baselines, without extension, e.g. '
                                 'describer_style_sweep130_frozen -- matches tests/<name>.json')
    b.add_argument('--run', help='use this specific file instead of the most recently '
                                  'modified runs/run-*.txt')
    b.add_argument('--dry-run', action='store_true')
    b.set_defaults(func=cmd_baseline)

    c = sub.add_parser('clean', help='delete files from runs/')
    c.add_argument('--current', action='store_true',
                    help='only delete per-case files for the most recent run-*.txt still in '
                         'runs/; leave that file and anything else alone')
    c.add_argument('--dry-run', action='store_true')
    c.set_defaults(func=cmd_clean)

    a = ap.parse_args()
    a.func(a)


if __name__ == '__main__':
    main()
