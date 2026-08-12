#!/usr/bin/env python3
"""Regenerate tests/describer_style_sweep.json from the master table.

The answer key is PARSED from docs/image_inventory.md rather than hand-written, so it
cannot drift from the corpus. Re-run this after any master-table edit. Session 9 built the
first sweep this way with a throwaway script; session 10 committed it, because the
three-axis rebuild proved the generation step happens more than once.
"""
import io, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inventory import parse_table, IMG_DIR, EXTS       # noqa: E402

DOC, OUT = 'docs/image_inventory.md', 'tests/describer_style_sweep.json'
PROMPT = 'prompts/describer_style.txt'

lines = io.open(DOC, encoding='utf-8').read().split('\n')
_, master = parse_table(lines, '## Master table')

ext = {os.path.splitext(f)[0]: f for f in os.listdir(IMG_DIR)
       if os.path.splitext(f)[1].lower() in EXTS}

# Adjudicated CONTESTED rulings, per field. CONTESTED is PROVISIONAL -- it expires when the
# vocabulary that caused it changes, so each entry names why it is contested rather than just
# excluding the case. All three below are idiom calls on images that are not uniform: the
# realist-vs-flat-graphic reading depends on which region of the frame you weight.
CONTESTED_IDIOM = {
    'fish_pixel':    'a shaded but heavily simplified sprite on a flat ground',
    'lincoln_money': 'flat guilloche border and ground dominate; the engraved portrait is a '
                     'small share of the frame',
    'mountain_rain': 'painterly and dimensional, but posterised into flat bands',
}

cases, expected = [], {}
for r in master:
    name = r['image'].strip('`')
    cid = f'sw_{name}'
    cases.append({
        'id': cid,
        'group': r['medium'],
        'image': f'{IMG_DIR}/{ext[name]}',
        'user': 'ROLE: style',
    })
    idiom = r['idiom']
    if name in CONTESTED_IDIOM:
        idiom = f"(CONTESTED -- {CONTESTED_IDIOM[name]})"
    key = f"{r['medium']} / {r['sub']} / {idiom} / {r['treatment']}"
    if 'amb' in r['flags']:
        key = (f"UNSCORABLE (amb) -- the pixels do not settle photo vs render; "
               f"table says {key}")
    expected[cid] = key

doc = {
    '_role': ('describer_style FULL CORPUS SWEEP, three-axis vocabulary (session 10). Every '
              'active image in images/, scored against the master table in '
              'docs/image_inventory.md.'),
    '_generated': ('Built by scripts/gen_style_sweep.py, which parses the master table, so the '
                   'answer key cannot drift from the corpus. DO NOT HAND-EDIT -- regenerate. '
                   'Groups are the expected coarse medium, which makes a miss visible in the '
                   'run file itself. NOTE: these are NOT drift groups -- validate.py only '
                   "cross-checks groups named 'same: ...', and none here are."),
    '_scoring': ('Four fields: MEDIUM / SUB_MEDIUM / IDIOM / TREATMENT, which is score.py\'s '
                 'default. The session-9 instruction to treat drawing and painting sub-term '
                 'misses as CONTESTED is RETIRED -- those sub-lists no longer mix axes, so '
                 'score all four fields. Only the amb files stay excluded.'),
    '_expected': expected,
    'defaults': {'server': 'http://localhost:8080/v1/chat/completions',
                 'model': 'qwen3.6-35b-a3b', 'system_file': PROMPT,
                 'temperature': 0, 'top_p': 0.9, 'top_k': 40, 'max_tokens': 2048},
    'cases': cases,
}
io.open(OUT, 'w', encoding='utf-8', newline='\n').write(
    json.dumps(doc, indent=2, ensure_ascii=False) + '\n')
print(f'wrote {OUT}: {len(cases)} cases, {sum(1 for v in expected.values() if "UNSCORABLE" in v)} excluded')
