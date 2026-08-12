#!/usr/bin/env python3
"""Regenerate tests/describer_style_targeted.json -- the fast iteration loop for describer_style.

Curated selection, GENERATED answer key. The case list below is chosen by hand, because the
point of a targeted test is that it is designed; the expected values are parsed out of the
master table in docs/image_inventory.md, because a hand-typed answer key drifts.

Built session 10 to replace tests/describer_style.json, whose 39 cases were selected under the
two-level vocabulary: it probes discriminations we have since dropped (marker vs sketch) and
has no coverage of the terms we added (dimensional toon, traditional cel vs digital, and
comic ink vs digital).

Why it exists at all: the 100-image sweep costs ~10 minutes, and a ten-minute gap invites
batching several changes into one round -- which is exactly how session 10 ended up measuring
three prompt edits at once and being unable to attribute the result. Three tiers:

    smoke (4-6 cases)  after any wording edit  -- format, plus the case you aimed at
    targeted (~40)     the iteration loop      -- ONE change per round
    sweep (100)        before locking a version, or when you need a RATE not a verdict

`same:` groups are drift groups and validate.py cross-checks them on [[MEDIUM]] only, so a
group is named `same:` ONLY where every member must agree on the coarse medium. Cross-media
pairs are deliberately NOT `same:` -- they are supposed to differ.
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inventory import parse_table, IMG_DIR, EXTS       # noqa: E402

SELECTION = [
    # ---- surviving probe pairs, one per discrimination the vocabulary claims to make
    ('same: 2D cel (traditional cel vs digital)',         ['ivy_toon', 'peter_griffin_toon']),
    ('same: 2D cel (anime vs western toon)',              ['azumanga_anime', 'azumanga_toon']),
    ('same: painting (digital vs oil; tie-break 4)',      ['ayanami_oil', 'woman_oil']),
    ('same: comic (ink vs digital, anime vs toon)',       ['annie3', 'comic']),
    ('same: stop-motion (tie-break 1)',                   ['coraline1', 'coraline2']),
    ('same: 3D CG (anime character render)',              ['kasia_render', 'kasia_swimsuit_render']),
    ('same: drawing (both marker; finish is NOT scored)', ['supergirl1', 'supergirl2']),
    ('same: pixel art (two fidelities)',                  ['fish_pixel', 'ramen_pixel']),
    ('same: live-action film (vintage Technicolor)',      ['p5_first', 'p5_last']),

    # cross-media -- these MUST differ on [[MEDIUM]], so never a same: group
    ('cross-media: one character, flat toon vs painted dimensional',
                                                          ['peter_griffin_painting']),
    ('cross-media: one warship, photograph vs plate',     ['destroyer_photo', 'destroyer_drawing']),
    ('cross-media: one man, photograph vs engraving',     ['lincoln_photo', 'lincoln_money']),
    ('nested medium (tie-break 2)',                       ['annie2', 'annie2_cropped']),

    # ---- the live failure clusters, carried in so a fix is measurable
    ('cluster: drawing read as painting',                 ['annie1', 'marker']),
    ('cluster: drawing, already fixed (regression control)',
                                                          ['car_interior_sketch']),
    ('cluster: realist subject on a flat ground',         ['kasia_bag', 'kasia_swimsuit',
                                                           'mountain_rain', 'phone']),
    ('cluster: 2D cel read as painting',                  ['car_interior_mecha_driver']),
    ('cluster: live-action read as photograph',           ['window']),

    # ---- coverage of terms not otherwise hit, plus passing controls
    ('coverage: idiom dimensional toon',                  ['shrek_cg', 'woody_cg']),
    ('coverage: idiom anime, pixel art',                  ['miyu', 'van_pixel']),
    ('coverage: idiom flat graphic (true)',               ['bird_vector']),
    ('coverage: treatment monochrome',                    ['teddy_taft']),
    ('control: passing cases across media',               ['bird_watercolor',
                                                           'chips_hotdog_dr_pepper_painting',
                                                           'kiki', 'door_first', 'fruitbowl']),
]

# Adjudicated CONTESTED idiom rulings. CONTESTED is PROVISIONAL -- it expires when the
# vocabulary that caused it changes, so each entry records WHY rather than just excluding.
# All three are images that are not uniform: the realist-vs-flat-graphic reading depends on
# which region of the frame you weight.
CONTESTED_IDIOM = {
    'fish_pixel':    'a shaded but heavily simplified sprite on a flat ground',
    'lincoln_money': 'flat guilloche border and ground dominate; the engraved portrait is a '
                     'small share of the frame',
    'mountain_rain': 'painterly and dimensional, but posterised into flat bands',
}


def main():
    lines = io.open('docs/image_inventory.md', encoding='utf-8').read().split('\n')
    _, master = parse_table(lines, '## Master table')
    by = {r['image'].strip('`'): r for r in master}
    ext = {os.path.splitext(f)[0]: f for f in os.listdir(IMG_DIR)
           if os.path.splitext(f)[1].lower() in EXTS}

    cases, expected = [], {}
    for group, names in SELECTION:
        for name in names:
            r = by[name]
            cid = 'st_' + name
            cases.append({'group': group, 'id': cid,
                          'image': IMG_DIR + '/' + ext[name], 'user': 'ROLE: style'})
            idiom = r['idiom']
            if name in CONTESTED_IDIOM:
                idiom = '(CONTESTED -- ' + CONTESTED_IDIOM[name] + ')'
            key = '{} / {} / {} / {}'.format(r['medium'], r['sub'], idiom, r['treatment'])
            if 'amb' in r['flags']:
                key = 'UNSCORABLE (amb) -- the pixels do not settle it; table says ' + key
            expected[cid] = key

    doc = {
        '_role': ('describer_style TARGETED test, three-axis vocabulary (session 10). The fast '
                  'iteration loop -- run ONE prompt change against this, not three.'),
        '_generated': ('Curated case list, generated answer key. Edit SELECTION in '
                       'scripts/gen_style_targeted.py and re-run; never hand-edit _expected.'),
        '_gate': 'enriched',
        '_scoring': ('Four fields: MEDIUM / SUB_MEDIUM / IDIOM / TREATMENT (score.py default). '
                     'Roughly half these cases are known failures, carried in deliberately so a '
                     'fix is measurable, so the score here is EXPECTED to sit well below the '
                     'sweep. Do not compare the two numbers -- compare this test to itself, '
                     'round over round. That is what "_gate": "enriched" means: the LEVEL is by '
                     'construction and carries no information, so score.py gates on MOVEMENT '
                     'against the previous round. Run it with '
                     '--baseline <previous run of this test>.'),
        '_expected': expected,
        'defaults': {'server': 'http://localhost:8080/v1/chat/completions',
                     'model': 'qwen3.6-35b-a3b',
                     'system_file': 'prompts/describer_style.txt',
                     'temperature': 0, 'top_p': 0.9, 'top_k': 40, 'max_tokens': 2048},
        'cases': cases,
    }
    io.open('tests/describer_style_targeted.json', 'w', encoding='utf-8', newline='\n').write(
        json.dumps(doc, indent=2, ensure_ascii=False) + '\n')
    print('wrote tests/describer_style_targeted.json: {} cases'.format(len(cases)))


if __name__ == '__main__':
    main()
