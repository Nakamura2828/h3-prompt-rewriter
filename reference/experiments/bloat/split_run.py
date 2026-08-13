#!/usr/bin/env python3
"""Split a concatenated run file by case-id prefix.

Side experiment: .claude/handoffs/SIDE_HANDOFF_bloat_calibration.md

Why this exists: validate.py's `describer` subcommand has --id-prefix, but its `h3` subcommand
does not. The secondary probe writes one run file holding 18 upstream describer records plus
eight padding levels' worth of h3 composer records, and each level has to be checked on its own.
Rather than touch validate.py -- which the handoff forbids, and which is imported by score.py
and shared by every role -- this splits the file first.

The split is purely mechanical: records are the '\\n----------\\n' chunks run_tests.py writes,
and the case id is read out of the same '[...]' header that validate.py's own HEAD regex reads,
by importing that function rather than re-deriving it.

  python .claude/experiments/bloat/split_run.py <run.txt> --prefix c_3800_ --out sub.txt
  python .claude/experiments/bloat/split_run.py <run.txt> --list
"""
import argparse
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate import head_parts                    # noqa: E402  -- imported, never modified

SEP = '\n----------\n'


def records(text):
    """[(case_id, raw_chunk)] in file order."""
    text = text.replace('\r\n', '\n')
    out = []
    for chunk in re.split(r'\n-{8,}\n', text):
        if not chunk.strip():
            continue
        first = chunk.split('\n', 1)[0]
        _, cid = head_parts(first)
        out.append((cid, chunk))
    return out


def subset(text, prefix):
    keep = [c for cid, c in records(text) if (cid or '').startswith(prefix)]
    return (SEP.join(keep) + SEP) if keep else ''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('run')
    ap.add_argument('--prefix')
    ap.add_argument('--out')
    ap.add_argument('--list', action='store_true')
    a = ap.parse_args()

    text = pathlib.Path(a.run).read_text(encoding='utf-8')
    if a.list:
        for cid, _ in records(text):
            print(cid)
        return 0
    if not (a.prefix and a.out):
        raise SystemExit('ERROR: --prefix and --out are both required (or use --list)')

    body = subset(text, a.prefix)
    if not body:
        raise SystemExit(f'ERROR: no records with id prefix {a.prefix!r} in {a.run}')
    pathlib.Path(a.out).write_text(body, encoding='utf-8')
    print(f'{body.count(SEP)} records -> {a.out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
