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
    '2eda7d4cfa': ('ref2va_v1', 'live', None,
                   'Session 32: FIRST DRAFT of the REF2VA composer Pass A, the fifth '
                   'blocks/modes/manifests mode (3,029 tokens). No pre-build ancestor -- REF2VA '
                   'postdates the build system entirely, unlike t2va/i2va/l2va which were '
                   'hand-locked first and reproduced by it. Roster records (<Subject N>/'
                   '<Picture N>/<Audio N>) are passed through verbatim rather than reformatted, '
                   'mirroring describer_style\'s two-pass handoff. Required converting '
                   'blocks/10_output_contract.txt and blocks/80_music.txt from a hardcoded '
                   '"integrated_multimodal_description" to a {{MAIN_FIELD}} slot -- '
                   'build.py --verify confirmed zero regression on t2va/i2va/l2va. Draft only: '
                   'no live model call against it yet, no tests/ref2va*.json, deliberately '
                   'excludes subject_definitions/summary/retention_analysis (Pass B + code\'s '
                   'job per docs/REF2VA_architecture.md).'),

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
    # ---- describer_object, session 22. THREE states, FOUR rounds: v3 produced two, because
    # round 4 changed the harness and the test file rather than the prompt.
    # RECONSTRUCTED: v1 and v2 were edited in place and rebuilt afterwards by reversing the
    # exact edits. The scores were measured against the originals, but these are the only two
    # states in this archive not captured live -- weigh them accordingly.
    'e2e87a1ac8': ('describer_object_v1', 'superseded', None,
                   'First object describer. 3,325 tokens, 9 fields. Format 29/35. Three '
                   'defects: the SUBJECT line overrode the image (a jumpsuit described onto a '
                   'jacket), printed names laundered out of [[TEXT]] into [[LABEL]], and the '
                   '[[SUBJECT NOT FOUND]] tail line fired empty on 6 cases.'),
    '2dc9a9ee62': ('describer_object_v2', 'superseded', 'describer_object_v1',
                   '3,886 tokens. Added THE SUBJECT LINE SELECTS; IT NEVER SUPPLIES, the '
                   'name-laundering ban, and [[SCALE]] fixed to "worn on the body" for '
                   'garments. Format 32/35 -- subject-override and SCALE both FIXED, laundering '
                   'unmoved at 4. Its own new rule quoted a SUBJECT-shaped phrase, which the '
                   'tail line then stole on SUBJECT-less cases: L-NAME-THE-CASE at its '
                   'documented limit.'),
    '8e8de06ccc': ('describer_object_v3', 'superseded', 'describer_object_v2',
                   '3,943 tokens. Removed the stolen phrase and banned the tail line from '
                   'copying the rules. The theft simply MOVED to the next SUBJECT-shaped string '
                   'in the prompt -- three rounds, three different stolen phrases. Format 31/35 '
                   'raw. The line was then offloaded to code (strip_unsolicited_not_found in '
                   'run_tests.py, docs/graph_mechanics.md); with that mechanic and 4 added '
                   'cases the SAME prompt scores 38/39. Session 28 content-scored '
                   '[[OBJECT_KIND]] for the first time on this state: 43/44 exact.'),
    '504408d564': ('describer_object_v4', 'live', 'describer_object_v3',
                   '3,951 tokens. Session 29: rewrote the VISIBLE TEXT anti-laundering rule as '
                   '"THE BLACKOUT TEST", a procedure, replacing the one banned-output list '
                   '(three real brand/person names) that had stood unchanged since v2 -- '
                   'checking the archive found that rule had only ever been written once, not '
                   'revised across three rounds as the round-count summary implied. Format '
                   '37/44 -> 39/44 on the same 44-case file (validate.py\'s new no_launder '
                   'check); one of the four original laundering cases (ob_misato_print) cleared '
                   'for the first time, no regressions, [[OBJECT_KIND]] unaffected (43/44).'),
    'b9bd35c4b3': ('describer_style_v1', 'superseded', None,
                   'Validated, never locked. 2,861 tokens.'),
    '310c10ab09': ('describer_style_v2', 'superseded', 'describer_style_v1',
                   'The three-axis rebuild. 3,883 tokens -- the LARGEST prompt state that '
                   'survives anywhere in this project. 43/45 format.'),
    'ee43018093': ('describer_style_v2-compressed', 'superseded', 'describer_style_v2',
                   'Prose tightened, no rule changed. 3,740 tokens, 45/45 format -- the best '
                   'format score on record. The pre-split baseline; still present in prompts/ '
                   'alongside the v3 split that replaced it.'),
    '91808c4a25': ('describer_style_look_v3', 'live', 'describer_style_v2-compressed',
                   'Pass A of the v3 split. look + class sum to 4,460 tokens, well over any '
                   'single-prompt budget -- the split buys headroom PER CALL, not in total. '
                   'Briefly superseded by v4 in s16 and RESTORED the same session when v4 '
                   'measured worse (17/30 vs 19/30). Produced the s15 enriched round and the v3 '
                   'split sweep.'),
    'bf48614103': ('describer_style_look_v4', 'reverted', 'describer_style_look_v3',
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
                   'april_1987 earned its answer. '
                   'REVERTED THE SAME SESSION. 17/30 vs v3\'s 19/30 on the s15 enriched round '
                   '(format 60/60). The rule WORKED and did not help, which is the useful part: '
                   'the look pass cut "digital" 50->18 and "vector" 36->24 in [[EXECUTION]], and '
                   'the classifier answered digital 18 times, then 17. ONE case. So the look pass '
                   'was never the lever -- describer_style_class.txt defaults to `digital` on its '
                   'own, whether or not the record claims it. Two ways it backfired: (1) the tell '
                   'list got recited back as evidence ("anti-alias" 0->24, "grain" 18->34), so '
                   'the same conclusion arrived laundered through evidence language, and "no '
                   'grain of any kind" is a WRONG digital tell -- a clean transfer of cel '
                   'animation has no grain either, grain is about capture not drawing; (2) it '
                   'banned "hand-drawn"/"traditional" (2->0), the vocabulary april_1987 used '
                   'and the only route to a correct traditional-cel answer in the whole round. '
                   'Also pushed IDIOM sideways: removing the flat/vector anchor made shading '
                   'language relatively salient and `dimensional toon` over-fired.'),
    '0927364a30': ('describer_style_class_v3', 'superseded', 'describer_style_v2-compressed',
                   'Pass B of the v3 split; receives pass A\'s record. 2,584 tokens. Superseded '
                   'by v4a in session 17. Its last measurement is the ROUND 0 validity pair '
                   '(Describer-Style-v3-frozenA-sweep-ROUND0 / -s15-ROUND0), which reproduced '
                   'the live two-pass scores exactly -- 80/100 and 18/30 -- and so also serves '
                   'as the proof that freezing pass A is faithful.'),
    'd7e49714aa': ('describer_style_class_v4a', 'superseded', 'describer_style_class_v3',
                   'THE VOCABULARY MERGE, AND NOTHING ELSE (2,584 -> 2,530 tokens; it is the '
                   'only state in the project that got SMALLER). Two user rulings, both taken on '
                   'their merits rather than on a score: stop-motion `puppet` merged into '
                   '`figure` (agreed s12, executed here), and `2D cel` lost its sub-list '
                   'entirely -- it held `traditional cel` and `digital`, and `traditional cel` '
                   'measured 2/7 with ALL FIVE losses going to `digital`. `none` rather than a '
                   'one-value list, because a single-value sub-list would make every 2D cel '
                   'record ASSERT digital production downstream, including of april_1987 and '
                   'pocahontas, which are hand-drawn. Deliberately carries NO new definitions '
                   '-- those are v4b -- so that the two rounds are separable. '
                   'ROUND 1 (Describer-Style-v4a-vocab-merge-ROUND1), 130-image frozen-pass-A '
                   'sweep: 101/130 exact, format 129/130. THIS IS THE NEW BASELINE; every '
                   'archived style round before it is scored against a vocabulary that no longer '
                   'exists. It behaved: 30 SUB_MEDIUM outputs moved and all were the mechanical '
                   'merge, TREATMENT did not move at all, and only 4 IDIOM cases changed -- two '
                   'of them (ivy_toon, kasia_bag) already measured as run-to-run noise in Round '
                   '0. Per-axis: MEDIUM 124, SUB_MEDIUM 118, IDIOM 110, TREATMENT 129. Two '
                   'consequences for reading anything after it: the `digital`-correct watch list '
                   'shrank 30 -> 12 (18 were `2D cel / digital`), isolating the real defect as '
                   'ink 1/5, marker 1/5, oil 1/2; and IDIOM became the LARGEST defect axis at 20 '
                   'misses, ahead of SUB_MEDIUM\'s 12.'),
    'e7aa542f83': ('describer_style_class_v4b', 'superseded', 'describer_style_class_v4a',
                   'THE DEFINITION LAYER (2,530 -> 3,050 tokens). Attacks the `digital` '
                   'over-attractor in the CLASSIFIER, which session 16 measured as the lever '
                   'after describer_style_look v4 failed to be one. '
                   'THE DIAGNOSIS, and it is not "tie-break 4 is unfollowed": of the twelve '
                   '[[SUB_MEDIUM]] terms, the ONLY ones carrying a definition were '
                   'stop-motion\'s four. ink, marker, oil, pencil, screentone, engraving, '
                   'halftone and traditional cel had none at all -- and `digital` DID have one, '
                   'inside tie-break 4, stated as an ABSENCE ("no medium physics, no wet edges, '
                   'no visible tooth or weave"), which any clean image satisfies vacuously. So '
                   'the single term with a stated test was the over-attractor, and its test '
                   'passed on no evidence. That is L-UNDEFINED-TERMS-READ-AS-OBVIOUS, the lesson '
                   '`clay` cost us in s15, one level up. Direct confirmation it defaults rather '
                   'than transcribes: in the look-v4 round, fern_gully / gordon_1996 / '
                   'gordon_2004 / scooby had records containing none of digital, vector, cel or '
                   'traditional, and the classifier still answered `digital`. '
                   'THE CHANGE: a positive visual tell for every sub-term, in the shape the '
                   'stop-motion line already used; `digital` rewritten from a test-by-absence '
                   'into one needing its own positive tell (even line weight, fills registering '
                   'exactly to the line, gradients with no instrument behind them); and the '
                   'session-12 asymmetry made an explicit default -- where no digital tell is '
                   'present and a physical instrument fits, write the instrument. Plus the s15 '
                   'boondocks ruling, recorded as data at the time and never written into a '
                   'prompt: flat two-tone highlight/shadow shading is NOT `dimensional toon`. '
                   'TWO v4 TRAPS AVOIDED DELIBERATELY. (1) No "grain" tell anywhere -- it is a '
                   'WRONG discriminator, a clean transfer of cel animation has no grain either; '
                   'grain separates photographic capture, not cel from digital drawing. (2) '
                   'Tells live in the CLASSIFIER, which emits only four label lines, so there is '
                   'no prose channel to launder a tell back through as evidence -- which is '
                   'exactly how look v4 failed. '
                   'RESULT: 92/130 against v4a\'s 101/130 (ROUND 2, '
                   'Describer-Style-v4b-definitions-ROUND2). NOT baselined. Two findings, and '
                   'the negative one is the more valuable. '
                   '(1) THE DEFINITION LAYER DID LITERALLY NOTHING. ink 1/5, marker 1/5, oil '
                   '1/2, digital 11/12 -- every term identical to v4a, and only 2 of 130 '
                   'SUB_MEDIUM outputs moved at all. The observation behind it was TRUE (ten of '
                   'twelve sub-terms genuinely had no definition) and the fix was still inert. '
                   'That is the second `digital` attempt to produce ~zero movement, after look '
                   'v4 moved it by one case. Defining the starved terms is NOT the lever. '
                   '(2) THE dimensional-toon CLAUSE COST 8 IDIOM CASES, all in one direction: '
                   'western toon 18/25 -> 11/25, with ALL NINE regressions going to `anime`. '
                   'dimensional toon itself never moved (11/11 both rounds), so the clause did '
                   'not even do its job. THE CAUSE IS THE WORDING, and it is worth remembering: '
                   'the clause ended "the answer is `anime` or `western toon`" -- naming `anime` '
                   'FIRST in a two-option list handed to a model that already over-attracts to '
                   'it. western -> anime was running at 3 cases in v4a and the standing defect '
                   'since s15; v4b took it to 12. An enumeration inside a rule is a ranking, not '
                   'a set.'),
    '4839880444': ('describer_style_class_v4c', 'superseded', 'describer_style_class_v4b',
                   'THE PROPORTION LICENCE -- the fix the v3 split was BUILT to make possible '
                   'and which was never written (3,050 -> 3,432 tokens). docs/describers.md:250 '
                   'records the intent from session 12: "pass B emits four closed-vocabulary '
                   'terms and cannot leak content, so it can later be licensed to judge facial '
                   'proportion and caricature -- which is what the `western toon` collapse '
                   'needs". It was shelved because the split appeared to fix the collapse on its '
                   'own; it did not, and v4b put western toon at 11/25. '
                   'THE DIAGNOSIS, same shape as `digital` one axis up: `anime` was defined as '
                   '"the Japanese animation and manga tradition" -- PURE PROVENANCE, with no '
                   'visual tell at all, which tie-break 4 forbids everywhere else. It was a free '
                   'attractor because nothing in the prompt said what it LOOKS like. '
                   'THE RULE, the user\'s, verified against the images before writing: '
                   'proportion first -- a body pushed away from life (noodle limbs, oversized '
                   'head/hands/feet, tiny torso) is western toon; otherwise BOTH traditions draw '
                   'naturally-proportioned figures, so THE EYE decides -- a large iris standing '
                   'as its own shape apart from the pupil, usually with a glint, is anime; a '
                   'naturalistic eye or a small flat pupil is western toon. Two guards the user '
                   'insisted on: naturalistic proportion is NOT by itself evidence of anime, and '
                   'the BACKGROUND TRACKS THE FIGURE rather than marking the term -- western '
                   'toon\'s realistic arm has realistic backgrounds, and that arm is exactly the '
                   'one that keeps failing to anime. '
                   'Also fixes v4b\'s ordering artifact: the dimensional-toon clause no longer '
                   'ends with a two-option list naming `anime` first. '
                   'VERIFICATION THAT SHAPED IT: the azumanga pair was first argued to be '
                   'unfixable by proportion, on the strength of the inventory\'s claim that it '
                   'was the "same 3 schoolgirls differing only in rendering". Looking at the '
                   'images falsified that -- two of three characters are shared, and _anime has '
                   'naturalistic proportions with glinted irises while _toon has noodle limbs '
                   'and small flat pupils. L-CLAIM-ROWS-ARE-UNRELIABLE, caught mid-design; the '
                   'inventory carries a corrections row and the pair is promoted from a "loose" '
                   'probe to the sharpest anime-vs-western-toon probe in the corpus.'),

    # --- v4d: THE ENTRY GATE, run as a 2x2 factorial (session 20) ----------------------------
    # Three states from one session because the two edits were run as SEPARATE ARMS and only the
    # combination shipped. Both losers are kept: arm A is the only direct evidence that gating
    # the ladder in isolation REGRESSES it, and that fact is what makes the interaction below
    # readable rather than a lucky guess.
    'a18a0bffa0': ('describer_style_class_v4d-flat', 'reverted', 'describer_style_class_v4c',
                   'ARM A -- THE FLAT DOOR ALONE. DEAD BRANCH, and instructive. Gives the '
                   'anime-vs-western-toon ladder an admission test ("are the THINGS IN THE SCENE '
                   'shaded, however hard-edged and flat that shading is?") and stops the '
                   'flat-two-tone clause pointing unconditionally at a two-option ladder that '
                   'contains neither `flat graphic` nor `realist`. '
                   'RESULT sweep130 104 -> 107, s18 51 -> 52. It fixed its four targets '
                   '(forest_day, forest_night, sanfran_evening, sanfran_night) plus '
                   'ghibli_painting_reference_painterly -- AND COST april_1987, gwen, molly and '
                   'ivy_toon, all western toon -> anime, i.e. v4c\'s signature win partly undone. '
                   'THE REAL COST IS WORSE THAN THE COUNT: april_1987 and ivy_toon are STRICT '
                   'CONTROLS for the `western toon | anime` accept-set, and both COLLAPSED while '
                   'avatar_1 and avatar_2 fired it -- so two of the three "gained" cases were '
                   'unearned passes. Under v4c all four controls read ok. Net credible movement '
                   '~+1 for the loss of an archetypal western cartoon. '
                   'DIAGNOSIS: a long admission paragraph inserted between the ladder header and '
                   'step 1, ending on a licence to ENTER, cost step 1 ("proportions pushed away '
                   'from life -> western toon, stop") its salience. A positional effect, the same '
                   'family as L-AN-ENUMERATION-IS-A-RANKING, arriving from a new direction.'),
    'fbd600f8ee': ('describer_style_class_v4d-stroke', 'reverted', 'describer_style_class_v4c',
                   'ARM B -- THE EYE GUARD ALONE. DEAD BRANCH. Rewrites ladder step 2, whose '
                   'anime tell ("a large eye with a defined iris standing as its own shape apart '
                   'from the pupil, usually with a specular glint") DESCRIBES A REAL HUMAN EYE -- '
                   'so any naturalistically painted person reaching the ladder resolved to '
                   '`anime`. The guard asks whether the eye is DRAWN (flat shapes bounded by a '
                   'line, enlarged beyond life) or RENDERED (continuous tone, wet surface, light '
                   'falling across it), and sends the rendered case out to `realist`. '
                   'RESULT sweep130 104 -> 106, s18 51 -> 51. Flat on its own and it did NOT fix '
                   'the painterly cluster it was aimed at -- blonde/saber/uniform _painterly all '
                   'still answer `anime`. It fixed girl_painting and, jointly, is what makes arm '
                   'C work. Format 130/130, the only state ever to clear annie2_cropped. '
                   'AN ADMISSION TEST ON VISIBLE BRUSHWORK WAS DRAFTED AND REJECTED BEFORE '
                   'RUNNING: ghibli_painting_reference_anime reads "soft-edged forms without hard '
                   'outlines", exactly like the painterly four, so excluding on stroke would have '
                   'evicted genuine painted anime. The eye guard cannot touch a figureless plate '
                   'at all, which is why it was chosen.'),
    'e4ac4b22b1': ('describer_style_class_v4e', 'live', 'describer_style_class_v4d',
                   'v4d WITH `vintage Technicolor` REMOVED from [[TREATMENT]] (3,740 -> 3,732 '
                   'tokens). A separate state rather than a v4d edit because the three v4d arms '
                   'were measured with the term still present, and this is the text the '
                   'full-corpus two-pass confirmation actually ran on -- collapsing them would '
                   'attribute that run to a prompt it never saw. '
                   'THE REMOVAL was agreed in session 12, reaffirmed in 17 and executed in 20. '
                   '`vintage Technicolor` named a PROCESS on an axis that otherwise answers '
                   '"which colour system", the same category error that removed `archival`, and '
                   'reading a dye-transfer process off pixels is a provenance call that '
                   'tie-break 4 forbids everywhere else in the same vocabulary. It had exactly '
                   'two samples and the model never held it: session 11 had p5_first and p5_last '
                   'SWAPPING it between rounds, and the session-12 split lost it on both at '
                   'once. [[TREATMENT]] is now a two-term axis. '
                   'CONFIRMED BY THE ROUND: under v4d both p5 frames still answered `vintage '
                   'Technicolor` and were scored as misses against the new key -- an artifact of '
                   'scoring an old run across a vocabulary boundary. Under v4e both come back '
                   '`colour` and PASS, which is what the removal predicted.'),
    'e7972414f1': ('describer_style_class_v4d', 'superseded', 'describer_style_class_v4c',
                   'ARM C -- BOTH DOORS. SHIPPED (3,432 -> 3,740 tokens; arm A alone was 3,629 '
                   'and arm B alone 3,543). sweep130 104 -> 110, '
                   's18 51 -> 52; 155 -> 162 over the whole 187-image corpus. '
                   'THE FINDING, and the reason the factorial was worth three arms: THE TWO DOORS '
                   'REPAIR EACH OTHER. april_1987 and molly go PASS -> miss (A) -> PASS (B) -> '
                   'PASS (C) -- the eye guard restores exactly the western/anime discrimination '
                   'that the flat door\'s placement weakened. C beats max(A, B) by 3 cases, so '
                   'this is a positive INTERACTION, not addition. Shipping "both" without running '
                   'the arms would have shown 110 and never revealed that A alone regresses an '
                   'archetypal western cartoon and collapses two strict controls. '
                   'CONTROLS: all four IDIOM controls read ok, identical to v4c; the 3 remaining '
                   'collapses are the pre-existing MEDIUM ones (gromit, castle) v4c already had. '
                   'IDIOM net +5 (7 fixed, 2 lost: gwen, supergirl2), which is exactly the '
                   'pre-agreed ship threshold. Third loss pjs is SUB_MEDIUM, off-axis. '
                   'ALL FIVE REMAINING MISSES WERE RULED FORGIVABLE BY THE USER and none was '
                   'given an accept-set -- forest_day_night explicitly so ("doing an accept would '
                   'be harmful"). The user\'s summary: "we went from having a nominally better '
                   'prompt that broke what was important, to having one whose only mistakes are '
                   'forgivable."'),
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
                        'The repo is LF everywhere as of session 23 (.gitattributes, '
                        '`* text=auto eol=lf`), so a fresh checkout now matches these hashes '
                        'directly -- no normalisation step needed. Before that it did not, '
                        'because core.autocrlf=true handed out CRLF copies.',
        'counts': {'archived': len([r for r in records if r.get('file')]),
                   'missing': len(MISSING)},
        'records': records,
    }
    if not a.dry_run:
        (OUT / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8',
                                           newline='\n')

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
