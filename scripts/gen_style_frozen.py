#!/usr/bin/env python3
"""Freeze pass A: turn a two-pass style test into a classifier-only test.

    python scripts/gen_style_frozen.py tests/describer_style_sweep.json \
        reference/test_archive/REF2VA/Describer-Style-v3-split-sweep.txt

`describer_style` runs as two passes: `look_<name>` describes the image, then
`sw_<name>` classifies it from that record. When the thing being tuned lives entirely
in pass B -- which is where the vocabulary, the tie-breaks and the `digital`
over-attractor all live -- re-running pass A every round buys nothing and costs two
things:

  * HALF THE CALLS. 200 -> 100 on the sweep, 60 -> 30 on an enriched round.
  * ATTRIBUTION, which matters more. Pass A's own run-to-run wording variance is
    otherwise inside every measurement: `ivy_toon` answered `western toon` in one round
    and `anime` in another, and the cause was upstream -- pass A wrote a
    differently-worded record from identical inputs (session 12). Freezing A means a
    B-tuning round measures B against a FIXED evidence set.

So this reads the `look_` records out of an archived run and inlines them literally
where `{{look_<name>}}` stood. No harness change is needed: run_tests.py already takes
literal `user` text, and only `{{...}}` substitution requires a live prior case.

WHAT IT DELIBERATELY DOES NOT DO
--------------------------------
It does NOT re-derive the answer key from the master table. `_expected` and every other
`_`-prefixed key are copied VERBATIM from the source test file, because those files carry
hand adjudications -- accept-sets, contested rulings, controls -- that the master table
does not encode. Re-deriving them would silently discard user rulings and re-accumulate
settled cases against the adjudication thresholds, with no error raised. That is
L-ADJUDICATION-DEFEATS-REGENERATION, and it is the whole reason this script takes a test
file as input rather than a corpus.

Consequence worth stating: to refresh a frozen file after an answer-key change, edit the
SOURCE test file and re-run this. The frozen file is derived; never hand-edit it.

USE IT FOR ITERATION, NOT FOR THE GATE. A frozen file exercises pass B only, so it cannot
catch a regression in pass A or in the join between them. Before locking a version, run
the real two-pass test once.
"""
import argparse
import hashlib
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate import parse_records, head_parts          # noqa: E402

TOKEN = re.compile(r'\{\{([^}]+)\}\}')


def records_by_id(run_paths):
    """case id -> the model's output, merged across one or more concatenated run files.

    More than one is needed whenever a test file's images were described across several
    rounds -- the 130-image sweep draws its pass-A records from the 100-image sweep archive
    plus the 30-image s15 archive. Later files win on a collision, and every collision is
    reported: two runs disagreeing about one case is exactly the kind of thing that should
    not pass silently.
    """
    out, seen = {}, {}
    for path in run_paths:
        for r in parse_records(io.open(path, encoding='utf-8').read()):
            _group, cid = head_parts(r['model'])
            if not cid:
                continue
            body = r['output'].strip()
            if cid in out and out[cid] != body:
                seen.setdefault(cid, []).append(path)
            out[cid] = body
    for cid, paths in seen.items():
        print(f'  NOTE {cid}: differing records across runs, using {paths[-1]}')
    return out


def freeze(test_path, run_paths, out_path):
    src = json.loads(io.open(test_path, encoding='utf-8').read())
    recs = records_by_id(run_paths)

    kept, missing, frozen = [], [], 0
    for c in src['cases']:
        user = c.get('user', '')
        refs = TOKEN.findall(user)
        if not refs:
            # A case with no {{...}} reference is a pass-A case; it is what we are dropping.
            # Keep anything else untouched so this stays usable on other chained tests.
            if c['id'].startswith('look_'):
                continue
            kept.append(c)
            continue
        c = dict(c)
        for ref in refs:
            if ref not in recs:
                missing.append((c['id'], ref))
                continue
            user = user.replace('{{%s}}' % ref, recs[ref])
        c['user'] = user
        # `image` is deliberately kept: the classifier sees the image AS WELL AS the record,
        # so dropping it here would change what the prompt is being asked to do.
        kept.append(c)
        frozen += 1

    if missing:
        for cid, ref in missing:
            print(f'ERROR: {cid} references {{{{{ref}}}}}, absent from the given run(s)')
        raise SystemExit(f'{len(missing)} unresolved reference(s) -- wrong or incomplete runs?')

    digest = {os.path.basename(r): hashlib.md5(io.open(r, 'rb').read()).hexdigest()
              for r in run_paths}
    doc = {k: v for k, v in src.items() if k != 'cases'}
    doc['_frozen'] = (
        'DERIVED FILE -- DO NOT HAND-EDIT. Generated by scripts/gen_style_frozen.py from '
        f'{test_path} with pass-A records taken from {", ".join(run_paths)}. '
        'Only the CLASSIFIER runs: '
        'each look_ record is inlined literally, so this measures prompts/'
        'describer_style_class.txt alone, with pass A held fixed. To change the answer key, '
        f'edit {test_path} and re-run the generator. Exercises pass B only, so it cannot '
        'catch a regression in pass A -- run the real two-pass test before locking a version.')
    doc['_frozen_from'] = {'test': test_path, 'runs': list(run_paths), 'run_md5': digest}
    # _passes describes a two-pass run and is now false; replace rather than carry it.
    doc['_passes'] = (
        'ONE PASS. The look_ cases are gone and their records are inlined into each sw_ case, '
        f'so this is {frozen} calls rather than {frozen * 2}. Validate with '
        '--role style_class --id-prefix sw_ ; there is no style_look half to check.')
    doc['cases'] = kept

    io.open(out_path, 'w', encoding='utf-8', newline='\n').write(
        json.dumps(doc, indent=2, ensure_ascii=False) + '\n')
    print(f'wrote {out_path}: {frozen} classifier cases, records frozen from '
          + ', '.join(f'{k} ({v[:12]})' for k, v in digest.items()))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('test', help='the ADJUDICATED source test file')
    ap.add_argument('run', nargs='+',
                    help='archived run(s) holding the look_ records to freeze. Pass several '
                         'when the test spans images described in different rounds -- the '
                         '130-image sweep needs the 100-image sweep archive AND the s15 one')
    ap.add_argument('--out', help='output path (default: <test>_frozen.json)')
    a = ap.parse_args()
    out = a.out or re.sub(r'\.json$', '_frozen.json', a.test)
    freeze(a.test, a.run, out)


if __name__ == '__main__':
    main()
