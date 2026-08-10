#!/usr/bin/env python3
"""Archive and clean up run_tests.py output.

Usage:
  python scripts/archive_run.py rename <dest> [--run PATH] [--clean] [--dry-run]
  python scripts/archive_run.py clean [--current] [--dry-run]

rename moves the most recently modified runs/run-*.txt (or --run PATH) to
reference/test_archive/<dest>.txt, e.g.:

  python scripts/archive_run.py rename FL2VA/Describer-FL2VA-Comparison

If that destination already exists, -2, -3, ... is appended until a free name
is found — existing archived rounds are never overwritten.

clean deletes files from runs/:
  (no flag)   delete everything in runs/
  --current   delete only the runs/<id>.txt files for case ids found in the
              most recently modified runs/run-*.txt still present in runs/;
              that run-*.txt itself and any other files are left alone

rename --clean is shorthand for: archive the run, then delete the
runs/<id>.txt files for the case ids in the file that was just archived.
"""
import argparse, pathlib, re, shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
RUNS = ROOT / 'runs'
ARCHIVE = ROOT / 'reference' / 'test_archive'
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
    dest = resolve_dest(a.dest)
    print(f'{"[dry-run] " if a.dry_run else ""}{src} -> {dest}')
    if not a.dry_run:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
    if a.clean:
        text = (src if a.dry_run else dest).read_text(encoding='utf-8')
        delete_ids(record_ids(text), a.dry_run)


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
                    help="also delete this run's per-case runs/<id>.txt files after archiving")
    r.add_argument('--dry-run', action='store_true')
    r.set_defaults(func=cmd_rename)

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
