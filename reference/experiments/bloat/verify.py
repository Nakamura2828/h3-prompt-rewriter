#!/usr/bin/env python3
"""Verify the experiment's instrument, independently of its results.

Side experiment: .claude/handoffs/SIDE_HANDOFF_bloat_calibration.md

The whole experiment rests on one claim -- that the ONLY thing varying across runs is
system-prompt length -- and on the noise floor being small enough for movement to mean
anything. Both are checkable, so they are checked here rather than asserted in the report.

  python .claude/experiments/bloat/verify.py

1. PURE INSERTION. Every padded prompt must differ from its source by exactly one inserted
   block and nothing else: no line of the original added, removed, reordered or altered. If
   this fails, the experiment is measuring a prompt EDIT and not a length change, and every
   number in the report is void.
2. TOKEN WINDOW. Every padded prompt within +/-25 of its nominal target, re-counted live
   rather than read back from the manifest.
3. NOISE FLOOR. The two unpadded baseline runs must be byte-identical. If they are not, the
   floor is whatever they differ by and every conclusion is weaker by that much.
4. SERVER CONFIG. The live sampler settings still match what CLAUDE.md documents, so the run
   is comparable with the rest of the project's archive. The handoff forbids changing these;
   this proves they were not changed.

Exits non-zero if any check fails.
"""
import difflib
import io
import json
import pathlib
import sys
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from token_budget import count                      # noqa: E402

TOLERANCE = 25
EXPECTED_SAMPLER = {'temperature': 0.0, 'top_k': 40, 'top_p': 0.9, 'repeat_penalty': 1.05}


def check_pure_insertion(manifest):
    srcs = {}
    bad = []
    for m in manifest:
        key = m['prompt']
        if key not in srcs:
            srcs[key] = io.open(ROOT / 'prompts' / f'{key}.txt',
                                encoding='utf-8').read().split('\n')
        padded = io.open(HERE / 'prompts' / m['file'], encoding='utf-8').read().split('\n')
        sm = difflib.SequenceMatcher(None, srcs[key], padded, autojunk=False)
        ops = [o for o in sm.get_opcodes() if o[0] != 'equal']
        if len(ops) != 1 or ops[0][0] != 'insert':
            bad.append((m['file'], [o[0] for o in ops]))
    return bad


def check_window(manifest):
    bad = []
    for m in manifest:
        n = count(io.open(HERE / 'prompts' / m['file'], encoding='utf-8').read())
        if abs(n - m['target']) > TOLERANCE:
            bad.append((m['file'], m['target'], n))
    return bad


def check_noise_floor():
    a = HERE / 'runs' / 'primary__base_1.txt'
    b = HERE / 'runs' / 'primary__base_2.txt'
    if not (a.exists() and b.exists()):
        return 'baseline runs not present yet'
    return None if a.read_bytes() == b.read_bytes() else 'baselines DIFFER'


def check_sampler():
    try:
        with urllib.request.urlopen('http://localhost:8080/props', timeout=15) as r:
            d = json.load(r)
    except Exception as e:                            # noqa: BLE001 -- report, do not crash
        return f'could not read /props ({e})'
    gs = d.get('default_generation_settings', {})
    p = gs.get('params', gs)
    off = {k: p.get(k) for k, v in EXPECTED_SAMPLER.items()
           if p.get(k) is None or abs(float(p[k]) - v) > 0.01}
    return None if not off else f'sampler differs from CLAUDE.md: {off}'


def main():
    manifest = json.loads((HERE / 'manifest.json').read_text(encoding='utf-8'))
    ok = True

    bad = check_pure_insertion(manifest)
    if bad:
        ok = False
        print(f'FAIL  {len(bad)} padded prompt(s) are not a pure single insertion:')
        for f, o in bad:
            print(f'        {f}: {o}')
    else:
        print(f'ok    all {len(manifest)} padded prompts are ONE pure insertion into an '
              f'otherwise untouched original')

    bad = check_window(manifest)
    if bad:
        ok = False
        print(f'FAIL  {len(bad)} padded prompt(s) outside the +/-{TOLERANCE} window:')
        for f, t, n in bad:
            print(f'        {f}: target {t}, live count {n}')
    else:
        print(f'ok    all {len(manifest)} live token counts within +/-{TOLERANCE} of target')

    for label, res in (('noise floor', check_noise_floor()), ('server config', check_sampler())):
        if res:
            ok = False
            print(f'FAIL  {label}: {res}')
        else:
            print(f'ok    {label}')

    print('\nINSTRUMENT VERIFIED' if ok else '\nINSTRUMENT NOT VERIFIED -- '
          'do not trust the report until this passes')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
