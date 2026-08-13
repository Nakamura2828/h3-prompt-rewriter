#!/usr/bin/env python3
"""Verify the experiment's instrument, independently of its results.

Side experiment: .claude/handoffs/SIDE_HANDOFF_bloat_calibration2.md

The whole design rests on two claims -- that TOTAL tokens are constant across every cell while
only the live/inert mix moves, and that the noise floor is small enough for movement to mean
anything. Both are checkable, so they are checked here rather than asserted in the report.

  python .claude/experiments/bloat2/verify2.py

1. PURE INSERTION. Every padded prompt differs from its source by exactly the intended inserted
   blocks and nothing else: no line of the original added, removed, reordered or altered. Two
   inserts for a rules cell (mid + end), one for an L0 cell (end only). If this fails, the
   experiment is measuring a prompt EDIT and every number in the report is void.
2. TOTAL WINDOW. Every padded prompt within +/-25 of 5,000, re-counted live rather than read
   back from the manifest. This is the claim that length is controlled by construction.
3. LIVE-RULE WINDOW. Every cell's live-rule count within +/-25 of its target, re-derived live as
   count(source + rules) - count(source) + source_live. This is the independent variable.
4. L0 == ROUND 1. The L0 files must be byte-identical to round 1's a_end 5,000 prompts. If they
   are, the L0 runs are directly comparable with round 1's stored outputs, which is a free
   cross-session check on the server.
5. NOISE FLOOR. The two L0 baseline runs must be byte-identical. If they are not, the floor is
   whatever they differ by and every conclusion is weaker by that much. (Per the user's call in
   planning, a non-zero floor is REPORTED and the batch continues; it is not a stop condition.)
6. SERVER CONFIG. The live sampler settings still match what CLAUDE.md documents, so this round
   is comparable with the rest of the project's archive.

Exits non-zero if any check fails. Checks 5 and 6 are reported but do not fail the run before
the baselines exist.
"""
import difflib
import io
import json
import pathlib
import sys
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
assert ROOT.name == 'h3-prompt-rewriter' and (ROOT / '.git').is_dir(), \
    f'ROOT resolved to {ROOT} -- refusing to run outside the project'
ROUND1 = ROOT / '.claude' / 'experiments' / 'bloat'

sys.path.insert(0, str(ROOT / 'scripts'))
from token_budget import count                          # noqa: E402

TOLERANCE = 25
TOTAL = 5000
EXPECTED_SAMPLER = {'temperature': 0.0, 'top_k': 40, 'top_p': 0.9, 'repeat_penalty': 1.05}


def check_pure_insertion(manifest):
    srcs, bad = {}, []
    for m in manifest:
        key = m['prompt']
        if key not in srcs:
            srcs[key] = io.open(ROOT / 'prompts' / f'{key}.txt',
                                encoding='utf-8').read().split('\n')
        padded = io.open(HERE / 'prompts' / m['file'], encoding='utf-8').read().split('\n')
        sm = difflib.SequenceMatcher(None, srcs[key], padded, autojunk=False)
        ops = [o for o in sm.get_opcodes() if o[0] != 'equal']
        want = 1 if m['arm'] == 'L0' else 2      # end only, or mid + end
        if len(ops) != want or any(o[0] != 'insert' for o in ops):
            bad.append((m['file'], f'{len(ops)} non-equal opcode(s) '
                                   f'{[o[0] for o in ops]}, expected {want} insert'))
    return bad


def check_total_window(manifest):
    bad = []
    for m in manifest:
        n = count(io.open(HERE / 'prompts' / m['file'], encoding='utf-8').read())
        if abs(n - TOTAL) > TOLERANCE:
            bad.append((m['file'], TOTAL, n))
    return bad


def check_live_window(manifest):
    """Re-derive live-rule tokens from the files, not from what pad2.py recorded.

    live = source_live + (count(source with ONLY the rules inserted) - count(source))

    The rules-only text is recovered by removing the END filler block from the padded file --
    which is exactly the block difflib identifies as the second insertion.
    """
    srcs, bad = {}, []
    for m in manifest:
        key = m['prompt']
        if key not in srcs:
            srcs[key] = io.open(ROOT / 'prompts' / f'{key}.txt', encoding='utf-8').read()
        src_lines = srcs[key].split('\n')
        padded_lines = io.open(HERE / 'prompts' / m['file'], encoding='utf-8').read().split('\n')
        sm = difflib.SequenceMatcher(None, src_lines, padded_lines, autojunk=False)
        ins = [o for o in sm.get_opcodes() if o[0] == 'insert']
        if not ins:
            bad.append((m['file'], m['live_target'], 'no insertion found'))
            continue
        # drop the LAST insertion (the end filler); what remains is source + rules only
        _, _, _, j1, j2 = ins[-1]
        rules_only = '\n'.join(padded_lines[:j1] + padded_lines[j2:])
        live = m['source_live'] + (count(rules_only) - count(srcs[key]))
        if abs(live - m['live_target']) > TOLERANCE:
            bad.append((m['file'], m['live_target'], live))
    return bad


def check_l0_matches_round1(manifest):
    """L0 is 'no rules, filler A at end, 5,000 total' -- which is round 1's a_end 5,000 cell."""
    out = []
    for m in manifest:
        if m['arm'] != 'L0':
            continue
        r1 = ROUND1 / 'prompts' / f'{m["prompt"]}__a_end__5000.txt'
        mine = HERE / 'prompts' / m['file']
        if not r1.exists():
            out.append((m['file'], 'round 1 file not present'))
        elif r1.read_bytes() != mine.read_bytes():
            out.append((m['file'], f'DIFFERS from {r1.name}'))
    return out


def check_noise_floor():
    a = HERE / 'runs' / 'setting__s_L0.txt'
    b = HERE / 'runs' / 'setting__s_L0b.txt'
    if not (a.exists() and b.exists()):
        return None, 'L0 baseline runs not present yet'
    if a.read_bytes() == b.read_bytes():
        return None, None
    ta, tb = a.read_text(encoding='utf-8'), b.read_text(encoding='utf-8')
    diff = sum(1 for l in difflib.unified_diff(ta.split('\n'), tb.split('\n'), n=0)
               if l.startswith(('+', '-')) and not l.startswith(('+++', '---')))
    return f'L0 twins DIFFER on {diff} line(s) -- the noise floor is NOT zero', None


def check_sampler():
    try:
        with urllib.request.urlopen('http://localhost:8080/props', timeout=15) as r:
            d = json.load(r)
    except Exception as e:                                # noqa: BLE001 -- report, do not crash
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
        print(f'FAIL  {len(bad)} padded prompt(s) are not a pure insertion:')
        for f, why in bad:
            print(f'        {f}: {why}')
    else:
        print(f'ok    all {len(manifest)} padded prompts are pure insertions into an '
              f'otherwise untouched original')

    bad = check_total_window(manifest)
    if bad:
        ok = False
        print(f'FAIL  {len(bad)} padded prompt(s) outside the +/-{TOLERANCE} TOTAL window:')
        for f, t, n in bad:
            print(f'        {f}: target {t}, live count {n}')
    else:
        print(f'ok    all {len(manifest)} totals within +/-{TOLERANCE} of {TOTAL} '
              f'-- length is constant by construction')

    bad = check_live_window(manifest)
    if bad:
        ok = False
        print(f'FAIL  {len(bad)} cell(s) outside the +/-{TOLERANCE} LIVE-RULE window:')
        for f, t, n in bad:
            print(f'        {f}: target {t}, re-derived {n}')
    else:
        print(f'ok    all {len(manifest)} live-rule counts within +/-{TOLERANCE} of target '
              f'-- the independent variable is on target')

    bad = check_l0_matches_round1(manifest)
    if bad:
        ok = False
        print('FAIL  L0 does not reproduce round 1\'s a_end 5,000 prompt:')
        for f, why in bad:
            print(f'        {f}: {why}')
    else:
        print('ok    L0 is byte-identical to round 1\'s a_end 5,000 prompt for both probes '
              '-- cross-session comparison is licensed')

    hard, soft = check_noise_floor()
    if hard:
        print(f'WARN  noise floor: {hard}')
        print('      Per the user\'s planning call this is REPORTED, not a stop condition. '
              'Lead the report with it and mark sub-floor differences meaningless.')
    elif soft:
        print(f'      noise floor: {soft}')
    else:
        print('ok    noise floor is ZERO -- the two L0 runs are byte-identical')

    res = check_sampler()
    if res:
        ok = False
        print(f'FAIL  server config: {res}')
    else:
        print('ok    server config matches CLAUDE.md')

    print('\nINSTRUMENT VERIFIED' if ok else '\nINSTRUMENT NOT VERIFIED -- '
          'do not trust the report until this passes')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
