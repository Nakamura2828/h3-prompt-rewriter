#!/usr/bin/env python3
"""Regenerate tests/describer_style_sweep.json from the master table.

The answer key is PARSED from docs/image_inventory.md rather than hand-written, so it
cannot drift from the corpus. Session 9 built the first sweep this way with a throwaway
script; session 10 committed it, because the three-axis rebuild proved the generation step
happens more than once.

    python scripts/gen_style_sweep.py                 # the FULL sweep -- see the warning
    python scripts/gen_style_sweep.py --added s15     # only images added in session 15

!!! RE-RUNNING THE FULL SWEEP AFTER A CORPUS ADDITION SILENTLY BREAKS THE BASELINE !!!

    "Re-run this after any master-table edit" was the original instruction and it is WRONG
    once the corpus grows. The full sweep is a REPRESENTATIVE test: `score.py` gates it on
    the failure LEVEL, and `--baseline` compares it against the previous round. Regenerating
    it over a larger corpus changes both N and the medium mix, so the comparison silently
    stops meaning anything -- the same class of mistake as changing a llama-server flag
    mid-phase, and it fails quietly rather than loudly.

    Session 15 added 30 images. The agreed order is: run them as their own ENRICHED test
    first (--added s15), adjudicate, and only THEN regenerate the full sweep and
    re-baseline once, deliberately. See .claude/TODO.md.

    --added emits `"_gate": "enriched"`, so score.py gates on MOVEMENT rather than level.
"""
import argparse, io, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inventory import parse_table, IMG_DIR, EXTS       # noqa: E402

DOC, OUT = 'docs/image_inventory.md', 'tests/describer_style_sweep.json'
LOOK = 'prompts/describer_style_look.txt'
CLASS = 'prompts/describer_style_class.txt'

ap = argparse.ArgumentParser()
ap.add_argument('--added', metavar='TAG',
                help="restrict to master rows whose `added` column is TAG (e.g. s15). "
                     "Writes tests/describer_style_added_TAG.json and marks it enriched.")
ap.add_argument('--out', help='override the output path')
args = ap.parse_args()

lines = io.open(DOC, encoding='utf-8').read().split('\n')
_, master = parse_table(lines, '## Master table')

if args.added:
    master = [r for r in master if r['added'].strip() == args.added]
    if not master:
        raise SystemExit(f'ERROR: no master rows with added == {args.added!r}')
OUT = args.out or (f'tests/describer_style_added_{args.added}.json' if args.added else OUT)

ext = {os.path.splitext(f)[0]: f for f in os.listdir(IMG_DIR)
       if os.path.splitext(f)[1].lower() in EXTS}

# Adjudicated CONTESTED rulings, per field. CONTESTED is PROVISIONAL -- it expires when the
# vocabulary that caused it changes, so each entry names why it is contested rather than just
# excluding the case.
#
# SESSION 17 CLEARED ALL OF THESE, by two different routes.
#
# The three idiom rulings (fish_pixel, lincoln_money, mountain_rain) were put to the user and
# cleared to the master value -- they are a single `flat graphic` over-attractor, not three
# separate ambiguities, and excluding them was hiding a defect rather than recording one.
#
# `coraline1` became an ACCEPT-SET rather than being cleared (see ACCEPT_SUB below). That is
# the better tool for it: CONTESTED threw away the fact that `clay` and `model` would still be
# flatly wrong there. The ruling is short-lived either way -- the puppet -> figure merge
# dissolves the distinction -- but the interim matters, because a pre-merge round still has to
# be scored against a pre-merge key.
#
# Both dicts are kept, empty, because the NEXT contested ruling belongs here rather than in a
# hand-edit -- see L-ADJUDICATION-DEFEATS-REGENERATION for why that distinction matters.
CONTESTED_SUB = {}

CONTESTED_IDIOM = {}

# Per-image accept-sets on [[SUB_MEDIUM]], ruled by the user. An accept-set keeps the case
# scorable while forgiving a genuinely undecidable call; everything outside the set still fails.
#
# EMPTY as of session 17. It briefly held `coraline1`: `puppet | figure`, replacing the session-12
# CONTESTED ruling. The puppet -> figure merge landed later the same session and dissolved the
# distinction, so `coraline1` is now plainly `figure`. Kept as the place the next one goes.
ACCEPT_SUB = {}

# The `amb` accept-set, ruled by the user in session 17. Applied to every master row flagged
# `amb`; see the comment at the point of use for why UNSCORABLE was the wrong verdict.
AMB_WHY = (
    "a clean studio product shot on a pure white sweep, where photo vs render is not visually "
    "determinable (the `amb` shape, session 7-9; ruled scorable session 17). The master value "
    "came from the USER'S KNOWLEDGE OF THE SOURCE -- an automaker press shot, an Amazon "
    "listing -- not from anything in the pixels, and L-SCORE-ONLY-WHAT-THE-INPUT-SHOWS forbids "
    "scoring a describer against that. So BOTH readings pass and neither is punished, while "
    "painting / drawing / vector still fail. This replaces the old UNSCORABLE ruling: the case "
    "stays in the denominator and keeps catching gross errors, instead of dropping out "
    "entirely. NOTE this is a deliberately WEAK test -- do not read a pass here as evidence "
    "the distinction works. Controls guard the direction it can erode: photograph is the "
    "forgiven side, so 3D CG cases that are NOT ambiguous must still come back 3D CG.")
AMB_CONTROL = ['sw_fruitbowl', 'sw_shrek_cg', 'sw_woody_cg']

cases, expected = [], {}
for r in master:
    name = r['image'].strip('`')
    cid = f'sw_{name}'
    img = f'{IMG_DIR}/{ext[name]}'
    # Two passes per image, interleaved so the chain resolves in file order (session 12).
    cases.append({'id': f'look_{name}', 'group': r['medium'], 'image': img,
                  'system_file': LOOK, 'user': 'ROLE: style'})
    cases.append({'id': cid, 'group': r['medium'], 'image': img, 'system_file': CLASS,
                  'user': 'ROLE: style\n\n[[STYLE_RECORD]]\n{{look_' + name + '}}'})
    idiom = r['idiom']
    if name in CONTESTED_IDIOM:
        idiom = f"(CONTESTED -- {CONTESTED_IDIOM[name]})"
    sub = r['sub']
    if name in CONTESTED_SUB:
        sub = f"(CONTESTED -- {CONTESTED_SUB[name]})"
    if name in ACCEPT_SUB:
        sub, _why, _ctl = ACCEPT_SUB[name][0], *ACCEPT_SUB[name][1:]
    key = f"{r['medium']} / {sub} / {idiom} / {r['treatment']}"
    if name in ACCEPT_SUB:
        key = {'expect': key, 'why': ACCEPT_SUB[name][1], 'control': ACCEPT_SUB[name][2]}
    if 'amb' in r['flags']:
        # Session 17: `amb` no longer means UNSCORABLE. The master value for these three came
        # from the user's knowledge of the SOURCE (an automaker press shot, an Amazon listing),
        # not from the pixels, and L-SCORE-ONLY-WHAT-THE-INPUT-SHOWS forbids scoring against
        # that. So the case stays in the denominator as an accept-set that forgives both
        # readings, while painting / drawing / vector still fail. Deliberately a WEAK test.
        key = {'expect': key.replace(r['medium'], f"{r['medium']} | 3D CG", 1),
               'why': AMB_WHY, 'control': AMB_CONTROL}
    expected[cid] = key

doc = {
    '_role': (
        f'describer_style ENRICHED ROUND -- only the images added in {args.added}, scored '
        f'against the master table in docs/image_inventory.md. NOT a representative sample of '
        f'the corpus: collected to fill named gaps, so it is deliberately skewed and a failure '
        f'RATE over it says nothing about the corpus as a whole.'
        if args.added else
        'describer_style FULL CORPUS SWEEP, three-axis vocabulary (session 10). Every '
        'active image in images/, scored against the master table in '
        'docs/image_inventory.md.'),
    '_generated': ('Built by scripts/gen_style_sweep.py, which parses the master table, so the '
                   'answer key cannot drift from the corpus. DO NOT HAND-EDIT -- regenerate. '
                   'Groups are the expected coarse medium, which makes a miss visible in the '
                   'run file itself. NOTE: these are NOT drift groups -- validate.py only '
                   "cross-checks groups named 'same: ...', and none here are."),
    '_passes': (f'TWO PASSES PER IMAGE (session 12). look_<name> runs {LOOK} and emits the six '
                f'descriptive fields; sw_<name> runs {CLASS}, receives that record as its user '
                f'prompt, and emits the four closed-vocabulary fields. The CLASSIFIER keeps the '
                f'sw_ ids on purpose, so _expected is unchanged by the split. Validate each half '
                f'separately: --role style_look --id-prefix look_ , then --role style_class '
                f'--id-prefix sw_. NOTE this is now 2x the calls -- budget ~20 minutes.'),
    '_scoring': ('Four fields: MEDIUM / SUB_MEDIUM / IDIOM / TREATMENT, which is score.py\'s '
                 'default, all emitted by the classifier pass; look_ records are not in '
                 '_expected and are ignored by score.py. The session-9 instruction to treat '
                 'drawing and painting sub-term misses as CONTESTED is RETIRED -- those '
                 'sub-lists no longer mix axes, so score all four fields. Only the amb files '
                 'stay excluded.'),
    **({'_gate': 'enriched',
        '_gate_note': (
            'Enriched, per .claude/CLAUDE.md: gate on MOVEMENT (regressions vs the previous '
            'round), never on the failure level. On the FIRST run there is no delta at all, so '
            'there is nothing to gate -- adjudicate, cap 6. Three of these images carry '
            'provisional rulings the user expects may need reversing; read '
            'docs/image_inventory.md section "Rulings that may need revisiting" BEFORE scoring '
            'them, or you will file a deliberate decision as a model defect.')}
       if args.added else {}),
    '_expected': expected,
    # No system_file default: each case names its own, since the two passes use different
    # prompts and a default would silently apply to whichever one forgot to override it.
    'defaults': {'server': 'http://localhost:8080/v1/chat/completions',
                 'model': 'qwen3.6-35b-a3b',
                 'temperature': 0, 'top_p': 0.9, 'top_k': 40, 'max_tokens': 2048},
    'cases': cases,
}
io.open(OUT, 'w', encoding='utf-8', newline='\n').write(
    json.dumps(doc, indent=2, ensure_ascii=False) + '\n')
print(f'wrote {OUT}: {len(cases)} cases ({len(cases) // 2} images x 2 passes), '
      f'{sum(1 for v in expected.values() if "UNSCORABLE" in v)} excluded')
