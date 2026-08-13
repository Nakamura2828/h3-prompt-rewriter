#!/usr/bin/env python3
"""Assemble reference/prompt_archive/ from census.json + tokens.json + the curated table below.

  python reference/prompt_archive/build_archive.py            # build
  python reference/prompt_archive/build_archive.py --dry-run

Regenerable by design: census.py and measure.py derive every fact mechanically, and this file
holds only the decisions a script cannot make -- what a state is CALLED, what it descends from,
and whether it shipped or was rolled back. Those are judgment calls and they are written down
explicitly rather than inferred, so a later session can see them and disagree with them.

Two rules govern the naming, and both exist because guessing either way loses information:

  1. NEVER invent a version number where the project already assigned one. `describer_setting`
     has exactly one state in git but the project calls it v5, because v1-v4 were iterated
     in-session and never committed. Renumbering it "v1" would silently break the mapping to
     reference/test_archive/REF2VA/Describer-Setting-v1..v5.txt, which is the only surviving
     record that those rounds happened.
  2. Version history here is a TREE, not a line. fl2va v4 was reverted and the shipping prompt
     descends from v3, which the v3->v4->current diffs prove: v4's one added rule appears in
     neither v3 nor current. A flat renumbering would assert a lineage that does not exist.

MISSING states are recorded as first-class records with no file. That is the point of the
archive rather than an apology for it: knowing that describer_style's 4,054-token round cannot
be re-run is worth more than a tidy directory that quietly omits it.
"""
import argparse
import hashlib
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _paths import find_root                            # noqa: E402

ROOT = find_root(HERE)
OUT = HERE                                              # this script lives in the archive it builds

# ---------------------------------------------------------------------------------------------
# CURATED: md5 prefix -> (archive label, status, parent label or None, note)
#
# status:  live       -- byte-identical to the file in prompts/ right now
#          superseded -- was live, later replaced on the main line
#          reverted   -- tried and rolled back; a dead branch, never shipped
#          pre-build  -- predates the block/manifest build system; comparison input only
# ---------------------------------------------------------------------------------------------
CURATED = {
    # --- built H3-contract prompts ----------------------------------------------------------
    'cc48c24721': ('t2va_v1', 'live', None,
                   'Byte-identical to reference/pre_build_env_canonical_prompts/t2va.txt: '
                   'the build system reproduced the hand-locked prompt exactly.'),
    'd0fa731f45': ('i2va_pre-build', 'pre-build', None,
                   'Untracked on every ref until 2026-08-12 (b4191f4). Same token count as v1 '
                   '(3,007) but different content. Read by scripts/build.py --verify.'),
    'd5b3cdb210': ('i2va_v1', 'live', 'i2va_pre-build', ''),
    'b3c8f88991': ('l2va_pre-build', 'pre-build', None,
                   'Untracked on every ref until 2026-08-12 (b4191f4). Read by '
                   'scripts/build.py --verify.'),
    '622aa43837': ('l2va_v1', 'live', 'l2va_pre-build', ''),

    # --- fl2va: a tree, not a line ----------------------------------------------------------
    '1bbc4fac1a': ('fl2va_v1', 'superseded', None, 'Pre-repo; survived only as dist/fl2va_v1.txt.'),
    '866dd46ab3': ('fl2va_v2', 'superseded', 'fl2va_v1',
                   'Larger than v3 (3,548 vs 3,499): v2->v3 was a net cut.'),
    '563fbb9a6a': ('fl2va_v3', 'superseded', 'fl2va_v2',
                   'Shipped for commits 4dce882..c843e49. The common ancestor of BOTH v4 and '
                   'v5. token_budget.py:41 labels 3,561 tokens "fl2va v3" -- stale: v3 is '
                   '3,499 and 3,561 is v5.'),
    'f7559d7716': ('fl2va_v4', 'reverted', 'fl2va_v3',
                   'DEAD BRANCH. One line added to v3 (+92 tokens) requiring every user action '
                   'to survive into the output. Reverted in session 3 for shedding content. '
                   'Session 13 re-ran v3 vs v4 head-to-head and the failure DID NOT '
                   'REPLICATE -- see reference/experiments/bloat/REPORT.md sec 6a. Existed only '
                   'in the user\'s Downloads until 2026-08-12.'),
    '54eaecfd47': ('fl2va_v5', 'live', 'fl2va_v3',
                   'LABEL ASSIGNED BY THIS ARCHIVE -- the project never numbered it. Descends '
                   'from v3, NOT v4: v4\'s added rule is absent here. Differs from v3 by the '
                   'landing-clause rework (commit 68909d9) plus two example edits.'),

    # --- fl2va_delta: v1 shipped and outlived three successors ------------------------------
    'dc458d9a46': ('fl2va_delta_v1', 'live', None,
                   'Still the shipping prompt. v2, v3 and v4 were all tried and abandoned, so '
                   'the oldest state is the live one.'),
    'cfd0a5572a': ('fl2va_delta_v2', 'reverted', 'fl2va_delta_v1', 'Pre-repo. Lineage presumed '
                   'sequential; not verifiable from git.'),
    '6382a47e93': ('fl2va_delta_v3', 'reverted', 'fl2va_delta_v2', 'Pre-repo.'),
    'e987aebd56': ('fl2va_delta_v4', 'reverted', 'fl2va_delta_v3', 'Pre-repo.'),

    # --- describer_frame: the one complete version history in the project -------------------
    '900b383fa1': ('describer_frame_v1', 'superseded', None,
                   'Also what prompts/describer_frame.txt actually CONTAINED for commits '
                   '4dce882..6546344 -- a wrong-content bug fixed by 3daef42 '
                   '("restore v7 describer content").'),
    'af06ee66c3': ('describer_frame_v2', 'superseded', 'describer_frame_v1', ''),
    '684acc768b': ('describer_frame_v3', 'superseded', 'describer_frame_v2', ''),
    'ee78489105': ('describer_frame_v4', 'superseded', 'describer_frame_v3', ''),
    '87ab10504f': ('describer_frame_v5', 'superseded', 'describer_frame_v4',
                   'Smaller than v4 (3,133 vs 3,200): v4->v5 was a net cut.'),
    '95a4c7ab18': ('describer_frame_v6', 'superseded', 'describer_frame_v5', ''),
    '8e9b2e991b': ('describer_frame_v7', 'superseded', 'describer_frame_v6',
                   '3,713 tokens -- ABOVE the 3,700 line, and it shipped without trouble for '
                   'several sessions. Also appeared as dist/frame_describer.txt.'),
    'a9613d8d0a': ('describer_frame_v8', 'live', 'describer_frame_v7',
                   'v7 + one clothing-agreement rule, MINUS two bans the model never obeyed '
                   '(position-relative-to-person, held-object-in-POSE). Net 10 bytes and 8 '
                   'tokens FEWER than v7.'),

    # --- the REF2VA describers: mostly gone -------------------------------------------------
    '99206cb96c': ('describer_character_v1', 'live', None,
                   'The post-calibration state. The pre-calibration one is MISSING.'),
    '047eb3d74a': ('describer_setting_v5', 'live', None,
                   'The ONLY setting state ever committed. v1-v4 are MISSING.'),
    'b9bd35c4b3': ('describer_style_v1', 'superseded', None,
                   'Validated, never locked. 2,861 tokens.'),
    '310c10ab09': ('describer_style_v2', 'superseded', 'describer_style_v1',
                   'The three-axis rebuild. 3,883 tokens -- the LARGEST prompt state that '
                   'survives anywhere in this project. 43/45 format.'),
    'ee43018093': ('describer_style_v2-compressed', 'superseded', 'describer_style_v2',
                   'Prose tightened, no rule changed. 3,740 tokens, 45/45 format -- the best '
                   'format score on record. The pre-split baseline; still present in prompts/ '
                   'alongside the v3 split that replaced it.'),
    '91808c4a25': ('describer_style_look_v3', 'superseded', 'describer_style_v2-compressed',
                   'Pass A of the v3 split. look + class sum to 4,460 tokens, well over any '
                   'single-prompt budget -- the split buys headroom PER CALL, not in total. '
                   'Superseded in s16 by v4; this is the state that produced the s15 enriched '
                   'round and the v3 split sweep, so it is the comparison point for the '
                   '`digital` fix.'),
    'bf48614103': ('describer_style_look_v4', 'live', 'describer_style_look_v3',
                   'Adds one block, PRODUCTION METHOD IS NOT A MARK (1,876 -> 2,118 tokens). '
                   'Aimed at the `digital` over-attractor, which s15 relocated from the '
                   'classifier to this pass: the describer was emitting "clean digital vector '
                   'outlines" for any clean-lined 2D image, and the classifier faithfully '
                   'transcribed it. 4 of 6 traditional-cel images lost that way. The diagnosis '
                   'that shaped the rule: gordon_1996 (failed) and april_1987 (passed) gave '
                   'IDENTICAL mark descriptions -- "uniform outlines of medium weight, flat '
                   'unmodulated colour fills" -- differing only in an ASSERTED leading phrase, '
                   '"digital vector" vs "traditional hand-drawn". So the marks were seen '
                   'correctly and a provenance guess was prepended. The rule bans the guess and '
                   'names the artefacts that actually discriminate (grain, scan lines, halation, '
                   'colour bleeding, stroke-to-stroke weight variation), which is exactly how '
                   'april_1987 earned its answer.'),
    '0927364a30': ('describer_style_class_v3', 'live', 'describer_style_v2-compressed',
                   'Pass B of the v3 split; receives pass A\'s record.'),
}

# ---------------------------------------------------------------------------------------------
# CURATED: states the project documents but which exist NOWHERE. No file can be written for
# these; the record IS the deliverable. `evidence` is what still proves the state existed.
# ---------------------------------------------------------------------------------------------
MISSING = [
    {'label': 'describer_style_v2-derivation', 'family': 'describer_style',
     'parent': 'describer_style_v2', 'tokens': 4054, 'status': 'reverted',
     'evidence': ['reference/test_archive/REF2VA/'
                  'Describer-Style-v2-targeted-iteration1-derivation-rule.txt',
                  'docs/describers.md:288', 'scripts/token_budget.py:45'],
     'why_it_matters':
         'THE MOST COSTLY LOSS IN THE PROJECT. This is the only prompt that ever produced the '
         'corrupted-field-token signature (39/45 format, correct content under mangled tokens), '
         'and it is the single real degradation underpinning L-PROMPT-TOKEN-BUDGET -- the 3,883 '
         'and 3,740 points did not degrade. The session-13 bloat experiment could not test the '
         'one prompt its whole question was about. It can never be re-run or re-measured.'},
    {'label': 'describer_setting_v1', 'family': 'describer_setting', 'parent': None,
     'tokens': None, 'status': 'superseded',
     'evidence': ['reference/test_archive/REF2VA/Describer-Setting-v1.txt',
                  'docs/describers.md:151'],
     'why_it_matters': '25/26 format with five atmosphere leaks and example-bleed. The '
                       'atmosphere quarantine (the role\'s main design decision) was written '
                       'against this text.'},
    {'label': 'describer_setting_v2', 'family': 'describer_setting',
     'parent': 'describer_setting_v1', 'tokens': None, 'status': 'reverted',
     'evidence': ['reference/test_archive/REF2VA/Describer-Setting-v2.txt',
                  'docs/describers.md:152'],
     'why_it_matters': 'The canonical L-KNOW-WHEN-TO-STOP case: one added paragraph dropped '
                       'format 25/26 -> 21/26. The paragraph itself is gone, so the clearest '
                       'worked example of a rule costing a rule cannot be inspected.'},
    {'label': 'describer_setting_v3', 'family': 'describer_setting',
     'parent': 'describer_setting_v1', 'tokens': None, 'status': 'superseded',
     'evidence': ['reference/test_archive/REF2VA/Describer-Setting-v3.txt',
                  'docs/describers.md:153'],
     'why_it_matters': 'The mechanical-gate attempt; 23/26. Called "diagnostically decisive" '
                       'for removing [[SUBJECT NOT FOUND]] from the role.'},
    {'label': 'describer_setting_v4', 'family': 'describer_setting',
     'parent': 'describer_setting_v3', 'tokens': None, 'status': 'superseded',
     'evidence': ['reference/test_archive/REF2VA/Describer-Setting-v4.txt',
                  'docs/describers.md:154'],
     'why_it_matters': '25/26, tying v5 while failing a DIFFERENT case -- half of the '
                       'reproducibility pair that L-ONE-RUN-IS-A-SAMPLE rests on.'},
    {'label': 'describer_character_v1-precalibration', 'family': 'describer_character',
     'parent': None, 'tokens': None, 'status': 'superseded',
     'evidence': ['reference/test_archive/REF2VA/'
                  'Describer-Character-AgeDrift-BeforeCalibration.txt',
                  'docs/describers.md:60-63'],
     'why_it_matters': 'The closed age vocabulary WITHOUT the apparent-age spans. Proved a '
                       'closed list alone was not enough to stop drift; the before/after pair '
                       'is now half-missing.'},
]


def sh(*args, binary=False):
    p = subprocess.run(list(args), cwd=ROOT, capture_output=True)
    if p.returncode:
        raise SystemExit(f'{" ".join(args)} failed:\n{p.stderr.decode("utf-8", "replace")}')
    return p.stdout if binary else p.stdout.decode('utf-8', 'replace')


def content_of(state):
    for c in state['commits']:
        p = subprocess.run(['git', 'show', f'{c["commit"]}:{c["path"]}'],
                           cwd=ROOT, capture_output=True)
        if p.returncode == 0:
            return p.stdout
    for path in state['paths']:
        f = ROOT / path
        if f.exists():
            return f.read_bytes()
    raise SystemExit(f'cannot recover {state["md5_norm"]}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    census = json.loads((HERE / 'census.json').read_text(encoding='utf-8'))
    tokens = {r['md5']: r['tokens']
              for r in json.loads((HERE / 'tokens.json').read_text(encoding='utf-8'))}

    unknown = [s['md5_norm'][:10] for s in census['states']
               if s['md5_norm'][:10] not in CURATED]
    if unknown:
        raise SystemExit('CURATED table is out of date -- unlabelled states: '
                         + ', '.join(unknown)
                         + '\nAdd them (or drop them) rather than letting the archive guess.')

    if not a.dry_run:
        OUT.mkdir(parents=True, exist_ok=True)

    records = []
    for st in census['states']:
        key = st['md5_norm'][:10]
        label, status, parent, note = CURATED[key]
        body = content_of(st).replace(b'\r\n', b'\n')     # archive is LF, always
        first = st['commits'][0] if st['commits'] else None
        last = st['commits'][-1] if st['commits'] else None
        rec = {
            'label': label, 'file': f'{label}.txt',
            'family': label.rsplit('_v', 1)[0] if '_v' in label else label,
            'status': status, 'parent': parent,
            'tokens': tokens[key], 'bytes': len(body), 'lines': body.count(b'\n') + 1,
            'md5_lf': hashlib.md5(body).hexdigest(),
            'first_seen': f'{first["date"]} {first["commit"]}' if first else None,
            'last_seen': f'{last["date"]} {last["commit"]}' if last else None,
            'git_paths': st['paths'], 'committed': bool(st['commits']),
            'note': note,
        }
        records.append(rec)
        if not a.dry_run:
            (OUT / rec['file']).write_bytes(body)

    records.sort(key=lambda r: (r['family'], r['label']))
    for m in MISSING:
        m = dict(m, file=None, md5_lf=None, bytes=None, lines=None, committed=False,
                 git_paths=[], first_seen=None, last_seen=None, note='MISSING -- no copy exists')
        records.append(m)

    manifest = {
        'generated_from': ['census.py', 'measure.py', 'build_archive.py'],
        'tokenizer': 'llama-server /tokenize, the model in CLAUDE.md > Model Parameters',
        'line_endings': 'every archived file is LF; md5_lf is over those exact bytes. '
                        'core.autocrlf=true in this repo, so a FRESH CHECKOUT will hand you '
                        'CRLF copies whose md5 differs. Normalise to LF before comparing.',
        'counts': {'archived': len([r for r in records if r.get('file')]),
                   'missing': len(MISSING)},
        'records': records,
    }
    if not a.dry_run:
        (OUT / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')

    print(f'{manifest["counts"]["archived"]} files + {manifest["counts"]["missing"]} '
          f'missing-state records'
          + ('  (dry run, nothing written)' if a.dry_run else f'  -> {OUT}'))
    for r in records:
        tok = f'{r["tokens"]:>5}' if r.get('tokens') else '    ?'
        print(f'  {r["status"]:<10} {tok}  {r["label"]}'
              + ('' if r.get('file') else '   [NO FILE -- LOST]'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
