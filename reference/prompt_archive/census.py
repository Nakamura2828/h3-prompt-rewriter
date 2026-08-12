#!/usr/bin/env python3
"""Census every distinct system-prompt state that exists anywhere in this project.

  python .claude/experiments/prompt_archive/census.py            readable report
  python .claude/experiments/prompt_archive/census.py --json      machine-readable

Two sources, both inside the project, per the standing scope limit:

  1. git -- every blob at every commit on every ref, for the paths that have ever held a
     finished system prompt (prompts/, the short-lived dist/, and the two reference dirs).
  2. the working tree -- because some files are gitignored and therefore exist in exactly
     one place on earth (reference/pre_build_env_canonical_prompts/ is the live example).

Identity is CONTENT, not filename. The project has repeatedly used a bare filename as the
live version and hand-numbered `_vN` copies as history, so the same bytes appear under
several names and different bytes appear under the same name at different commits. So every
candidate is hashed and grouped by hash: a "state" is a distinct set of bytes, and the names
and commits it appeared under are properties OF that state rather than its identity.

That is also what lets the census answer the question it was written for -- whether an
unnumbered working-tree file is a new state or a duplicate of something already recorded --
without trusting any filename, mtime or version label.

No file is written and nothing is modified; this only reads.
"""
import argparse
import collections
import hashlib
import io
import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _paths import find_root                            # noqa: E402

ROOT = find_root(HERE)

# Paths that have ever held a finished system prompt. Deliberately NOT blocks/ or modes/:
# those are build inputs, and a fragment is not a prompt. See ARCHIVE.md on the gap this
# leaves for the four built prompts.
PROMPT_PATH = re.compile(
    r'^(prompts/|dist/|reference/retired/prompts/|reference/pre_build_env_canonical_prompts/)'
    r'[^/]+\.txt$')

# Extra working-tree files to hash for provenance matching only -- never archived as states
# in their own right. These are the copies the bloat experiment pulled out of git history,
# and the point is to identify what they actually were.
PROVENANCE_ONLY = ['.claude/experiments/bloat/logs']

VER = re.compile(r'^(?P<family>.+?)_v(?P<num>\d+)$')


def git(*args):
    p = subprocess.run(['git'] + list(args), cwd=ROOT, capture_output=True, encoding='utf-8',
                       errors='replace')
    if p.returncode:
        raise SystemExit(f'git {" ".join(args)} failed:\n{p.stderr}')
    return p.stdout


def commits():
    """[(sha, unix_time, date, subject)] oldest first, across all refs."""
    out = []
    for line in git('log', '--all', '--format=%H\t%ct\t%ad\t%s', '--date=short',
                    '--reverse').splitlines():
        sha, ct, date, subj = line.split('\t', 3)
        out.append((sha, int(ct), date, subj))
    return out


def blob(sha):
    p = subprocess.run(['git', 'cat-file', 'blob', sha], cwd=ROOT, capture_output=True)
    if p.returncode:
        raise SystemExit(f'git cat-file blob {sha} failed')
    return p.stdout                                    # bytes, exactly as stored


def family_of(stem):
    m = VER.match(stem)
    return (m.group('family'), int(m.group('num'))) if m else (stem, None)


def norm(data):
    """Content hash ignoring line-ending convention.

    Needed because a CRLF/LF difference alone made a one-line change look like a
    whole-file rewrite earlier in this project's history. Both hashes are reported: `md5`
    is the exact bytes (what the user's own MD5 checks would produce), `md5_norm` is the
    line-ending-insensitive one used for grouping.
    """
    return data.replace(b'\r\n', b'\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()

    # ---- gather every candidate: (source, path, bytes) ----------------------------------
    cands = []
    seen_blob = {}                                     # blob sha -> bytes, cat-file once

    log = commits()
    for sha, ct, date, subj in log:
        for line in git('ls-tree', '-r', sha).splitlines():
            meta, path = line.split('\t', 1)
            _mode, kind, bsha = meta.split()
            if kind != 'blob' or not PROMPT_PATH.match(path):
                continue
            if bsha not in seen_blob:
                seen_blob[bsha] = blob(bsha)
            cands.append({'source': 'git', 'path': path, 'data': seen_blob[bsha],
                          'commit': sha[:7], 'ct': ct, 'date': date, 'subject': subj,
                          'blob': bsha[:7]})

    for path in sorted(ROOT.rglob('*.txt')):
        rel = path.relative_to(ROOT).as_posix()
        prov = any(rel.startswith(d + '/') for d in PROVENANCE_ONLY)
        if not (PROMPT_PATH.match(rel) or prov):
            continue
        cands.append({'source': 'provenance' if prov else 'worktree', 'path': rel,
                      'data': path.read_bytes(), 'commit': None,
                      'ct': int(path.stat().st_mtime), 'date': None, 'subject': None,
                      'blob': None, 'mtime': int(path.stat().st_mtime)})

    # ---- group by normalised content ----------------------------------------------------
    states = collections.OrderedDict()
    for c in cands:
        n = norm(c['data'])
        key = hashlib.md5(n).hexdigest()
        st = states.setdefault(key, {
            'md5_norm': key, 'bytes': len(c['data']), 'lines': n.count(b'\n') + 1,
            'md5_exact': set(), 'names': set(), 'paths': set(), 'commits': [],
            'families': set(), 'labels': set(), 'in_worktree': False,
            'provenance_only': True, 'first_ct': None, 'last_ct': None})
        st['md5_exact'].add(hashlib.md5(c['data']).hexdigest())
        stem = pathlib.PurePosixPath(c['path']).stem
        fam, num = family_of(stem)
        st['names'].add(stem)
        st['paths'].add(c['path'])
        st['families'].add(fam)
        if num is not None:
            st['labels'].add(f'{fam} v{num}')
        if c['source'] == 'git':
            st['commits'].append({'commit': c['commit'], 'date': c['date'],
                                  'path': c['path'], 'ct': c['ct'],
                                  'subject': c['subject']})
        if c['source'] == 'worktree':
            st['in_worktree'] = True
        if c['source'] != 'provenance':
            st['provenance_only'] = False
        for k in ('first_ct', 'last_ct'):
            pass
        st['first_ct'] = c['ct'] if st['first_ct'] is None else min(st['first_ct'], c['ct'])
        st['last_ct'] = c['ct'] if st['last_ct'] is None else max(st['last_ct'], c['ct'])

    for st in states.values():
        st['md5_exact'] = sorted(st['md5_exact'])
        st['names'] = sorted(st['names'])
        st['paths'] = sorted(st['paths'])
        st['families'] = sorted(st['families'])
        st['labels'] = sorted(st['labels'])
        st['crlf_variants'] = len(st['md5_exact'])

    # ---- report -------------------------------------------------------------------------
    if a.json:
        print(json.dumps({'commits': [{'commit': s[:7], 'ct': c, 'date': d, 'subject': j}
                                      for s, c, d, j in log],
                          'states': list(states.values())}, indent=2))
        return 0

    byfam = collections.defaultdict(list)
    for st in states.values():
        for fam in st['families']:
            byfam[fam].append(st)

    print(f'{len(cands)} candidate files -> {len(states)} distinct content states\n')
    for fam in sorted(byfam):
        group = sorted(byfam[fam], key=lambda s: s['first_ct'])
        print('=' * 96)
        print(f'{fam}   ({len(group)} distinct state(s))')
        print('=' * 96)
        for st in group:
            tags = []
            if st['in_worktree']:
                tags.append('LIVE-ON-DISK')
            if st['provenance_only']:
                tags.append('provenance-copy-only')
            if st['crlf_variants'] > 1:
                tags.append(f'{st["crlf_variants"]} line-ending variants')
            print(f'  {st["md5_norm"][:10]}  {st["bytes"]:>6}B  {st["lines"]:>4}L  '
                  f'{" ".join(tags)}')
            print(f'      labels: {", ".join(st["labels"]) or "(none -- unnumbered)"}')
            print(f'      names : {", ".join(st["names"])}')
            if st['commits']:
                first = st['commits'][0]
                last = st['commits'][-1]
                span = (f'{first["date"]} {first["commit"]}' if first is last
                        else f'{first["date"]} {first["commit"]} .. '
                             f'{last["date"]} {last["commit"]}')
                print(f'      git   : {len(st["commits"])} appearance(s), {span}')
            else:
                print('      git   : NEVER COMMITTED')
            for p in st['paths']:
                print(f'              {p}')
        print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
