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
ACCEPT_SUB = {
    # Session 19: the sub half of the unprinted-print ruling. `halftone` names a screen the
    # model cannot see, so `digital` is a correct reading of the marks that ARE there. Paired
    # with the MEDIUM set below -- this is the first case to need two axes at once, which is
    # why the application loop was rewritten to compose them.
    'misato_car_technical_print': ('halftone | digital', None, None),
}

# Per-image accept-sets on [[MEDIUM]], ruled by the user in session 18.
#
# THE FIGURELESS-PLATE SET. A background plate with no figure and no cel line work is a genuine
# provenance-vs-pixels case: a cel-era background IS a painting, so `2D cel` and `painting` are
# both defensible and only our knowledge of what the frame was made for separates them. The
# user's grounds are the same ones that produced the `car`/`chair` ruling -- "if the eye can't
# differentiate, then we're judging on provenance, not pixels."
#
# WHY THIS IS NOT THE `amb` FLAG, which would have been the obvious home for it: the user's
# direction in session 18 is to STOP USING `amb` altogether and let `_expected` carry these
# rulings, revisiting the flag only if something turns out genuinely ambiguous. Overloading the
# flag would also have forced AMB_WHY/AMB_CONTROL from one global pair into a keyed table, and
# would have silently changed what the `amb` section of docs/image_inventory.md means.
#
# THREE THINGS DELIBERATELY NARROW IT, and each one is load-bearing:
#   * Only plates where line work is genuinely ABSENT. Outlined plates (backyard_anime,
#     garden_pond_anime, pavilion_anime, classroom_anime_empty, shoes_anime,
#     simpsons_couch_toon, spongebob_tree_toon) stay STRICT -- the eye can tell, so forgiving
#     them would absorb a real answer.
#   * The ghibli-ref PAIR IS EXEMPT, both halves strict. That pair exists to test cel-gouache
#     against digital painting; an accept-set over its source half would let a model answer
#     `painting` for both, collapse the discrimination, and still score two passes.
#   * grass_anime_girl is the control for grass_anime_scenery -- literally the same background
#     with characters added, so it must still come back `2D cel`.
_PLATE_WHY = (
    "a background plate with NO FIGURE and NO CEL LINE WORK, where 2D cel vs painting is not "
    "visually determinable (ruled session 18). A cel-era background is itself a painting, so "
    "only provenance separates the two readings and L-SCORE-ONLY-WHAT-THE-INPUT-SHOWS forbids "
    "scoring against that. BOTH pass; drawing / vector / 3D CG / photograph still fail. "
    "Deliberately a WEAK test on this axis -- a pass here is NOT evidence the distinction "
    "works. Controls guard the direction it erodes: `painting` is the forgiven side, so cel "
    "frames that are NOT ambiguous must still come back `2D cel`. NOTE the idiom is scored "
    "STRICTLY on these -- see the [[IDIOM]] note in the test's _role.")
# SESSION 19: `sw_ghibli_painting_reference_anime` REMOVED from this list. It is a cel-era
# painted background -- the SAME ambiguous class this set exists to forgive -- so it can never
# police the set: a control has to sit on the UNAMBIGUOUS side of the axis being widened. It
# was made strict for the probe-pair reason (L-AN-ACCEPT-SET-MUST-NOT-COVER-ITS-OWN-PROBE) and
# then reused as a control, and those are not the same job. Being strict-for-probe-reasons does
# not qualify an image to be a control. It stays strict; it just no longer claims to guard
# anything, and its collapse is now read as the finding it is rather than as an alarm on this
# set. Replaced by the OUTLINED plates session 18 deliberately kept strict -- visible cel line
# work, so `2D cel` is decidable on them -- which are also in the s18 test and therefore live.
_PLATE_CONTROL = ['sw_grass_anime_girl', 'sw_backyard_anime', 'sw_classroom_anime_empty',
                  'sw_pavilion_anime', 'sw_shoes_anime',
                  'sw_ivy_toon', 'sw_april_1987', 'sw_azumanga_anime', 'sw_woman_oil']
ACCEPT_MEDIUM = {n: ('2D cel | painting', _PLATE_WHY, _PLATE_CONTROL) for n in (
    'temple_grounds_anime', 'town_tower_anime', 'river_mountain_anime', 'nerv',
    'grass_anime_scenery', 'ghibli_grass', 'ghibli_kitchen', 'roadway_toon',
)}

# --- Session 19 rulings, from the first s18 round -------------------------------------------
#
# THE PUBLICITY-STILL SET. A cast still from a filmed production is honestly both a photograph
# and a frame of live-action film, and nothing in the pixels settles which. What makes this a
# safe set rather than a hole is that the corpus already contains a deliberate probe pair on
# exactly this axis -- wayne_knight_older_adult (photograph) against
# wayne_knight_jurassic_adult (live-action film) -- and BOTH passed the s19 round. The
# distinction demonstrably works; this is one hard case inside a working axis.
_STILL_WHY = (
    "a cast publicity still from a filmed production, where photograph vs live-action film is "
    "not visually determinable (ruled session 19). The frame is a posed studio shot AND a "
    "record of a filmed production, and nothing in the pixels decides which reading the "
    "describer should have reached. BOTH pass; every non-live-action medium still fails. "
    "Controls guard the axis rather than the case: the wayne_knight pair sits on this exact "
    "boundary from both sides and both halves passed, so a collapse there means the "
    "distinction has stopped working and this pass is worthless.")
_STILL_CONTROL = ['sw_wayne_knight_older_adult', 'sw_wayne_knight_jurassic_adult',
                  'sw_hermione_preteen', 'sw_couple_middle_aged']

# THE UNPRINTED-PRINT CASE. `print / halftone` on misato_car_technical_print came from knowing
# the plate came out of a brochure. At the resolution the model is given there is no rosette,
# no dot, no screen -- just an airbrushed illustration with ink outlines, which is exactly what
# it answered. Same shape as the chair/car ruling below: the master value rests on provenance
# the describer cannot see, and L-SCORE-ONLY-WHAT-THE-INPUT-SHOWS forbids scoring against it.
_PRINT_WHY = (
    "a technical brochure plate whose PRINT PROCESS is not visible at the resolution the model "
    "receives -- no rosette, no halftone dot, no screen (ruled session 19). `print / halftone` "
    "records how the artwork was reproduced, which is provenance rather than pixels, so "
    "`drawing / digital` is a correct reading of what is actually there. Control: "
    "destroyer_drawing is the halftone case where the screen IS plainly visible, so a print "
    "plate that shows its process must still come back `print`.")
_PRINT_CONTROL = ['sw_destroyer_drawing', 'sw_sketch_boat', 'sw_fruit_reference_sketch']

# THE FIGURELESS IDIOM CASE, and the ONLY one. Session 18 deliberately withheld an idiom set on
# the plates because the idiom was the thing being measured. The s19 round settled that: 14 of
# 15 figureless plates got the idiom RIGHT, so the predicted defect does not exist and
# roadway_toon is one genuinely undecidable plate rather than a symptom of anything. The
# controls are the plates that got it right, which is what makes this set narrow.
_PLATE_IDIOM_WHY = (
    "a soft painterly cel background with no figure and no idiom cue -- no line work, no "
    "character, nothing that places it in either tradition (ruled session 19). Withheld in "
    "session 18 ON PURPOSE while the figureless defect was still hypothetical; released only "
    "after the s19 round showed 14 of 15 figureless plates reaching the RIGHT idiom, which "
    "means this is one undecidable image and not a systematic failure. Controls are figureless "
    "plates that ARE decidable, from both sides: if they start collapsing, the defect is real "
    "after all and this set must be withdrawn.")
_PLATE_IDIOM_CONTROL = ['sw_simpsons_couch_toon', 'sw_spongebob_tree_toon',
                        'sw_grass_anime_scenery', 'sw_backyard_anime']

# THE PAINTERLY-FACE CASE -- WRITTEN, MEASURED, AND WITHDRAWN INSIDE ONE SESSION. Kept here as
# a comment because the withdrawal is the useful record, not the set.
#
# All four *_painterly files missed `realist -> anime` in the s19 round. The set was written for
# uniform_reference_painterly alone, on the reading that its face carries genuine anime
# construction while the other three are naturalistic, with those three as strict controls.
# Re-scoring the SAME run with the set in place answered the question immediately:
#
#     FIRED  sw_uniform_reference_painterly  IDIOM = 'anime' (primary 'realist')
#            controls: saber_reference_painterly COLLAPSED · blonde_reference_painterly
#                      COLLAPSED · ghibli_painting_reference_painterly COLLAPSED
#
# ALL THREE controls collapsed the same way, which is exactly the condition the control field
# exists to detect: the model is not resolving one anime-faced painting, it is answering `anime`
# for every painterly image it sees. The set was buying a pass it had not earned. User confirmed
# on review that blonde and saber both still read `realist` to the eye, so the key is right and
# the model is wrong. Withdrawn; all four are one honest miss cluster naming an `anime`
# over-attractor on painterly work -- the same SHAPE as the `digital` over-attractor, on a
# different axis.
#
# The general lesson, and the reason this is worth eighteen lines: AN ACCEPT-SET IS A HYPOTHESIS,
# AND ITS CONTROLS ARE THE EXPERIMENT THAT TESTS IT. Writing one and re-scoring an existing run
# costs nothing and can refute it before it ever protects a defect.

ACCEPT_MEDIUM.update({
    'third_rock':                ('photograph | live-action film', _STILL_WHY, _STILL_CONTROL),
    'misato_car_technical_print': ('print | drawing', _PRINT_WHY, _PRINT_CONTROL),
})

# Per-image accept-sets on [[IDIOM]]. New in session 19 -- the axis had never needed one,
# because until the s18 round every idiom miss had turned out to be a real defect.
ACCEPT_IDIOM = {
    'roadway_toon': ('western toon | anime', _PLATE_IDIOM_WHY, _PLATE_IDIOM_CONTROL),
}

# The studio-product-shot accept-set, ruled by the user in session 17.
#
# MIGRATED OFF THE `amb` FLAG IN SESSION 19, on the user's standing direction to stop using the
# flag altogether and let `_expected` carry these rulings. The three files are now ordinary
# ACCEPT_MEDIUM entries and the flag branch is gone. The WHY AND CONTROL TEXT BELOW IS
# UNCHANGED, deliberately: it is the record of a real session-17 ruling, and the migration was
# only allowed on the condition that it does not disturb the existing answer keys. Because the
# expectation is assembled from the same strings, `tests/describer_style_sweep130.json`
# regenerates byte-identically -- which is the check that proves the baseline survived.
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
ACCEPT_MEDIUM.update({n: ('photograph | 3D CG', AMB_WHY, AMB_CONTROL)
                      for n in ('chair', 'car_1', 'car_2')})

# --- Back-ported session 15/16 rulings ------------------------------------------------------
#
# These twelve accept-sets were adjudicated straight into tests/describer_style_sweep130.json
# and never written back here, so from session 16 until session 19 THIS SCRIPT COULD NOT
# REPRODUCE THAT TEST -- regenerating it would have silently dropped every one of them. That
# is L-ADJUDICATION-DEFEATS-REGENERATION happening for real rather than in the abstract.
# Recovered mechanically FROM the committed test file in session 19, so the `why` texts are
# the originals rather than paraphrases, and verified by regenerating sweep130 and diffing.
_S16_ANNIE2CROPPED = (
    "a painting colouring over a drawing's lineart (user, session 16) -- pen line with "
    "watercolour wash over it, so both coherent readings are true: painting / watercolour and "
    "drawing / ink. KNOWN LIMITATION: accept-sets are per-FIELD, so the cross terms drawing / "
    "watercolour and painting / ink also pass even though neither is a legal pairing in the "
    "vocabulary. Accepted deliberately rather than stretching the mechanism to cross-field "
    "constraints, which is the shape ruled out of scope in session 16. If the cross terms "
    "start turning up, that is the signal to reconsider -- probably by adding watercolour to "
    "drawing's sub-list, not by changing score.py.")
_S16_ANNIE2CROPPED_CONTROL = ['sw_bird_watercolor', 'sw_annie1']

_S16_APRIL1987FIGUR = (
    "a photograph of moulded plastic figures on a shelf in a real room (user, s15, reaffirmed "
    "s17: \"both alternatives should be acceptable\"). Tie-break 1 makes `stop-motion / figure` "
    "legal -- the objects win -- but these figures were never animated and the room is not a "
    "set, so the model's `photograph / none` is equally true. This is the SHAPE-2 case "
    "session 16 ruled out of accept-set scope: two fields each holding half a true answer. "
    "Session 17 accepts it as a PAIR of per-field sets instead, with the same known "
    "limitation as sw_annie2_cropped -- the cross terms `stop-motion / none` and `photograph "
    "/ figure` also pass, and `photograph / figure` is the very pairing the user called "
    "invalid. Accepted deliberately rather than adding cross-field constraints to score.py. "
    "Controls guard the erodable direction: `photograph` is forgiven, so real stop-motion is "
    "what can drift, and all four unambiguous stop-motion cases in this file must still come "
    "back stop-motion with a real sub-term.")
_S16_APRIL1987FIGUR_CONTROL = ['sw_gromit', 'sw_gumby', 'sw_rudolf', 'sw_pjs']

_S16_APRILCOMIC = (
    "original marker art on a blank sketch cover, photographed with the publisher's printed "
    "trade dress around it (user, s15; MEDIUM opened s17). Tie-break 2's s15 amendment says "
    "report the artwork when the outer layer is pure capture, which gives `drawing`; but the "
    "contents row records real printed trade dress -- IDW logo, issue number, creator credits "
    "-- so the outer layer is NOT pure capture and `comic` is equally defensible. SUB_MEDIUM "
    "stays STRICT at `marker`, exactly as on sw_april_fanart: the user's session-12 ruling is "
    "that `marker` -> `digital` specifically is not acceptable, so opening the instrument "
    "here would forgive the project's largest defect on one of the few images that tests it. "
    "CONTROL GAP, stated plainly: this file contains NO unambiguous `drawing` case, and "
    "`drawing` is the side that can erode, so the axis is only half guarded. sw_gordon_comic "
    "controls the reverse direction (a real comic staying `comic`). Fix by adding an "
    "unambiguous drawing to this file, not by loosening the set.")
_S16_APRILCOMIC_CONTROL = ['sw_gordon_comic']

_S16_APRILFANART = (
    "the user accepts `comic` on the coarse term -- it carries the same style as a comic book "
    "cover -- while the instrument is still unmistakably marker (user, session 16): \"I can "
    "see where painting comes from but it still looks marker to me\". So MEDIUM opens and "
    "SUB_MEDIUM does NOT. Same per-field limitation as sw_annie2_cropped: `comic`'s sub-list "
    "is ink/screentone/digital, so the accepted pairing comic + marker is not legal in the "
    "vocabulary, accepted deliberately rather than stretching the mechanism. NOTE this case "
    "also carries the s15 composite correction (marker figure over a pasted manhole on a "
    "digital white ground), so a describer that averages the layers lands on `digital` by a "
    "route the MEDIUM accept-set does not forgive.")
_S16_APRILFANART_CONTROL = ['sw_gordon_comic']

_S16_AVATAR1 = (
    "a western toon with an anime-inspired style; the two traditions are genuinely converging "
    "(user, sessions 15 and 16). Written on ALL FOUR of the s15 anime-idiom cartoons, not "
    "only the two that failed this way in the s15 round -- the accept-set records a property "
    "of the IMAGE, and keying it to one run's output would be fitting the answer key to a "
    "sample (L-ONE-RUN-IS-A-SAMPLE). Score-neutral this round: boondocks missed to "
    "dimensional toon, outside the set, and titans1 passed on the primary. Controls guard "
    "both directions -- sw_april_1987, sw_car_interior_toon and sw_ivy_toon are unambiguously "
    "western, sw_nadia unambiguously anime. sw_car_interior_toon was added in s16 on a user "
    "ruling that is worth more than its own case: it is ITSELF a converging-styles image, and "
    "the user placed it \"solidly on the western side\" -- so it tests the distinction under "
    "the exact conditions that make it hard, which a easy control cannot. sw_ivy_toon lives "
    "in describer_style_sweep.json and will report 'not in this test' here; run the sweep to "
    "exercise it. EXPECT THE COLLAPSE WARNING: sw_april_1987 already answers `anime`, which "
    "is exactly what the control field exists to make visible -- it is not a reason to widen "
    "the set.")
_S16_AVATAR1_CONTROL = ['sw_april_1987', 'sw_car_interior_toon', 'sw_nadia', 'sw_ivy_toon']

_S16_KASIARENDER = (
    "an AI render in a semi-realistic anime style. Both halves are true at once -- it IS a "
    "dimensional render and it IS anime-styled -- and the two idiom terms are not competing "
    "readings of one property here, they name different properties of the same image (user, "
    "session 16). Controls cover BOTH directions deliberately: sw_kasia / "
    "sw_kasia_swimsuit_worn are the same character rendered flat and unambiguously anime (the "
    "direction this accept-set actually risks -- it forgives dimensional toon, so anime is "
    "the side that can erode), while sw_shrek_cg / sw_woody_cg are unambiguously dimensional "
    "toon.")
_S16_KASIARENDER_CONTROL = ['sw_kasia', 'sw_kasia_swimsuit_worn', 'sw_shrek_cg', 'sw_woody_cg']

_S16_SUPERGIRL2 = (
    "marker colouring over a pencil sketch, so both instruments are literally present (user, "
    "session 16). This retires the session-9 CONTESTED ruling on the sub-term, which said the "
    "pair differs in finish rather than instrument -- true of the PAIR, but the un-inked "
    "pencil under-drawing is visible in this image on its own merits. NOTE: `drawing / "
    "pencil` has NO unambiguous sample in the corpus, so only the marker side of this "
    "distinction can be controlled.")
_S16_SUPERGIRL2_CONTROL = ['sw_marker', 'sw_supergirl1']

_S16_WINDOW = (
    "a live-action film clip cropped to a photograph's aspect ratio, so the framing genuinely "
    "reads as a still (user, session 16). NOTE the asymmetry: `castle` is NOT an accept-set. "
    "The pair looked like a swap -- the model called castle film and window photo, the "
    "reverse of the key -- but only window is ambiguous; castle is a plain miss and is the "
    "control here.")
_S16_WINDOW_CONTROL = ['sw_castle', 'sw_p6_first']

ACCEPT_MEDIUM.update({
    'annie2_cropped':               ('painting | drawing', _S16_ANNIE2CROPPED, _S16_ANNIE2CROPPED_CONTROL),
    'april_1987_figure':            ('stop-motion | photograph', _S16_APRIL1987FIGUR, _S16_APRIL1987FIGUR_CONTROL),
    'april_comic':                  ('drawing | comic', _S16_APRILCOMIC, _S16_APRILCOMIC_CONTROL),
    'april_fanart':                 ('drawing | comic', _S16_APRILFANART, _S16_APRILFANART_CONTROL),
    'window':                       ('live-action film | photograph', _S16_WINDOW, _S16_WINDOW_CONTROL),
})

ACCEPT_SUB.update({
    'annie2_cropped':               ('watercolour | ink', _S16_ANNIE2CROPPED, _S16_ANNIE2CROPPED_CONTROL),
    'april_1987_figure':            ('figure | none', _S16_APRIL1987FIGUR, _S16_APRIL1987FIGUR_CONTROL),
    'supergirl2':                   ('marker | pencil', _S16_SUPERGIRL2, _S16_SUPERGIRL2_CONTROL),
})

ACCEPT_IDIOM.update({
    'avatar_1':                     ('western toon | anime', _S16_AVATAR1, _S16_AVATAR1_CONTROL),
    'avatar_2':                     ('western toon | anime', _S16_AVATAR1, _S16_AVATAR1_CONTROL),
    'boondocks':                    ('western toon | anime', _S16_AVATAR1, _S16_AVATAR1_CONTROL),
    'kasia_render':                 ('anime | dimensional toon', _S16_KASIARENDER, _S16_KASIARENDER_CONTROL),
    'kasia_swimsuit_render':        ('anime | dimensional toon', _S16_KASIARENDER, _S16_KASIARENDER_CONTROL),
    'titans1':                      ('western toon | anime', _S16_AVATAR1, _S16_AVATAR1_CONTROL),
})

# Every per-axis accept-set table, keyed by the master column it widens. One case may now fire
# on SEVERAL axes -- misato_car_technical_print is the first, needing both `print | drawing`
# and `halftone | digital` -- so the application below composes them instead of letting the
# last one win, which is what the old sequential-overwrite code did.
ACCEPT_BY_AXIS = [('medium', ACCEPT_MEDIUM), ('sub', ACCEPT_SUB), ('idiom', ACCEPT_IDIOM)]

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

    # Assemble the four fields, then widen whichever axes carry an accept-set for this image.
    # Assigning the alternatives straight into the field is safer than the old string
    # .replace(): `2D cel` is a substring of nothing here today, but a medium term that
    # appeared inside another field's value would have been silently rewritten.
    fields = {'medium': r['medium'], 'sub': sub, 'idiom': idiom, 'treatment': r['treatment']}
    whys, controls = [], []
    for axis, table in ACCEPT_BY_AXIS:
        if name not in table:
            continue
        alts, why, control = table[name]
        fields[axis] = alts
        if why and why not in whys:
            whys.append(why)
        for c in control or []:
            if c not in controls:
                controls.append(c)

    key = ' / '.join(fields[a] for a in ('medium', 'sub', 'idiom', 'treatment'))
    if whys:
        # Several axes firing on one case means several rationales. Joining them keeps each
        # ruling readable in the score report rather than letting the last one overwrite the
        # rest, which is how the pre-session-19 code lost ACCEPT_SUB's `why`.
        key = {'expect': key, 'why': '\n\nALSO: '.join(whys), 'control': controls}
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
