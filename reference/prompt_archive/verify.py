#!/usr/bin/env python3
"""Check this archive against its manifest, and against the live prompts/ directory.

  python reference/prompt_archive/verify.py

Three checks:

  1. INTEGRITY -- every file's LF md5 still matches MANIFEST.json, and no file in the
     directory is unlisted. Catches an edit or a partial copy.
  2. LIVE DRIFT -- every record marked status=live must still be byte-identical to its
     counterpart in prompts/. This is the check the archive actually needs: a snapshot of a
     living file goes stale silently, and the failure mode is a future session reading an
     archived "current" prompt that is no longer current. A drift here is not a corruption --
     it means prompts/ moved on and the archive needs a NEW numbered state.
  3. COVERAGE -- every prompts/*.txt matches some archived state. A prompt in prompts/ that
     matches nothing archived is an unrecorded state, which is the exact situation the
     archive exists to prevent.

Comparison is over LF-normalised bytes throughout: core.autocrlf=true in this repo, so a
fresh checkout produces CRLF working copies and a raw byte compare would fail on every file
for no real reason.

Exits non-zero if any check fails.
"""
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent


def find_root(start):
    """Walk up to the repo root, rather than counting directory levels.

    Counting levels breaks the moment the archive is moved, which it is designed to be:
    it is built in reference/experiments/ and lives in reference/. Both locations must work.
    """
    for d in [start, *start.parents]:
        if (d / 'prompts').is_dir() and (d / 'scripts').is_dir():
            return d
    raise SystemExit(f'cannot locate the repo root above {start} -- expected a parent '
                     f'directory containing both prompts/ and scripts/')


ROOT = find_root(HERE)
PROMPTS = ROOT / 'prompts'


def lf(p):
    return p.read_bytes().replace(b'\r\n', b'\n')


def md5(b):
    return hashlib.md5(b).hexdigest()


def main():
    man = json.loads((HERE / 'MANIFEST.json').read_text(encoding='utf-8'))
    recs = man['records']
    ok = True

    # 1 -- integrity
    listed = {r['file'] for r in recs if r.get('file')}
    on_disk = {p.name for p in HERE.glob('*.txt')}
    bad = []
    for r in recs:
        if not r.get('file'):
            continue
        f = HERE / r['file']
        if not f.exists():
            bad.append(f'{r["file"]}: MISSING from the archive')
        elif md5(lf(f)) != r['md5_lf']:
            bad.append(f'{r["file"]}: md5 {md5(lf(f))[:10]} != manifest {r["md5_lf"][:10]}')
    for extra in sorted(on_disk - listed):
        bad.append(f'{extra}: present but not in MANIFEST.json')
    if bad:
        ok = False
        print(f'FAIL  integrity ({len(bad)}):')
        for b in bad:
            print(f'        {b}')
    else:
        print(f'ok    integrity -- {len(listed)} files match the manifest')

    # 2 -- live drift
    drift = []
    live = [r for r in recs if r.get('status') == 'live' and r.get('file')]
    for r in live:
        # family name is the prompts/ basename; the label adds the version suffix
        stem = r['label'].rsplit('_v', 1)[0]
        cand = PROMPTS / f'{stem}.txt'
        if not cand.exists():
            drift.append(f'{r["label"]}: prompts/{stem}.txt does not exist')
        elif md5(lf(cand)) != r['md5_lf']:
            drift.append(f'{r["label"]}: prompts/{stem}.txt has CHANGED since archiving '
                         f'-- archive a new state')
    if drift:
        ok = False
        print(f'FAIL  live drift ({len(drift)}):')
        for d in drift:
            print(f'        {d}')
    else:
        print(f'ok    live drift -- all {len(live)} live states still match prompts/')

    # 3 -- coverage
    by_md5 = {r['md5_lf']: r for r in recs if r.get('md5_lf')}
    live_files = sorted(PROMPTS.glob('*.txt'))
    if not live_files:
        raise SystemExit(f'no prompts found in {PROMPTS} -- refusing to report coverage, '
                         f'since an empty directory would pass this check vacuously')
    uncovered, stale = [], []
    for p in live_files:
        rec = by_md5.get(md5(lf(p)))
        if rec is None:
            uncovered.append(p.name)
        elif rec['status'] != 'live':
            stale.append((p.name, rec['label'], rec['status']))
    if uncovered:
        ok = False
        print(f'FAIL  coverage -- {len(uncovered)} prompt(s) in prompts/ match no archived '
              f'state:')
        for u in uncovered:
            print(f'        {u}   <- unrecorded state; add it to the archive')
    else:
        print(f'ok    coverage -- all {len(live_files)} prompts/*.txt are archived states')

    # Not a failure. A superseded state can be in prompts/ on purpose -- describer_style.txt is
    # the pre-split baseline the current style work is measured against -- so this is reported
    # only so that a deliberately retained file and a forgotten one look different.
    for name, label, status in stale:
        print(f'note  prompts/{name} is {label} ({status}), not the live state -- expected if '
              f'it is being kept as a comparison baseline')

    n_missing = sum(1 for r in recs if not r.get('file'))
    print(f'\n{len(listed)} archived - {n_missing} recorded-but-lost')
    print('ARCHIVE VERIFIED' if ok else 'ARCHIVE NOT VERIFIED')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
