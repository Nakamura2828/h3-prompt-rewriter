# Describer prompts

Design and version history for the standalone describer prompts — the per-image passes that
produce structured `[[FIELD]]` records for FL2VA and REF2VA composition.

Roles built so far: **frame** (v8), **character** (v1), **setting** (v5). `object` and `style`
are not built yet; see `.claude/TODO.md`. Lessons cited by slug (`L-...`) are defined in
`.claude/lessons_learned.md`. The test corpus these were validated against is documented in
`docs/image_inventory.md`.

Moved out of `.claude/CLAUDE.md` in session 8 — that file is gitignored, so this reasoning had
no backup while the prompts it justifies did.

## Frame describer (v8, session 4)

Two v4-era bans the model never actually obeyed are now permitted: naming a held object in
`[[POSE]]`, and stating `[[POSITION]]` purely relative to another described person (must still
pair with a frame-absolute term, e.g. "background centre, partially occluded by the girl in
the foreground"). Added: a `[[CHAR]]` label must agree with its own `[[CLOTHING]]` line.
Rationale reconstructed from `reference/old_describer_versions/` (pre-repo v1–v7, kept in the
repo) and a discussion transcript the user dropped in mid-session (not kept — its content is
now captured here) since neither session memory nor the handoff had the actual reasoning. Both
relaxed bans were confirmed **already violated 6/6 in the unpatched v7 output** before this
change — legalizing them changed nothing in model behavior. Regression-tested across 8 cases
reconstructed from a one-off prior test-result file (also not kept, absorbed into the
git-tracked `tests/describer_v8_regression.json`), archived at
`reference/test_archive/Describer/DescriberTest8-v8-regression.txt` and
`DescriberTest9-v8-clothing-probe.txt`.

## Character describer (v1, session 5)

`prompts/describer_character.txt` — the first new REF2VA describer role. **Identity only**: it
records what a subject durably looks like, never what this photograph shows them doing. Fields,
condensations last per `L-JUDGMENTS-LAST`:

```
[[SUBJECT_KIND]] [[APPEARANCE]] [[CLOTHING]] [[DISTINGUISHING]] [[LABEL]] [[DEFINITION]]
```

`[[LABEL]]` + `[[DEFINITION]]` are spliced downstream into the guide's own §2.1 phrasing:
`<Subject 1> is [[LABEL]], with [[DEFINITION]].`

**Deliberately absent**: POSE, POSITION, FRAMING, GAZE, EXPRESSION, HOLDING, ENVIRONMENT,
LIGHTING, PALETTE, TEXT. The guide treats poses, actions, and expressions as their own subject
type, so anchoring the generated video to a reference pose would be wrong. A pose-reference role
can be added later if `subject_definitions` ever needs one. Rendering style is also excluded —
that is `describer_style`'s job.

**Closed age vocabulary**, the fix for the drift flagged as a known limitation since session 3:

```
person: infant · toddler · child · pre-teen · teenager · young adult · adult · middle-aged · older adult
animal: young · adult · old · not visible
```

The closed list alone was **not** enough. First round: the same girl across two frames of one
shot came out `pre-teen` and `child` — stable across 3 repeats, so a real property of the images,
not sampling noise. Fix was to give each term an explicit apparent-age span *in the rules only*
(spelled out in words, never digits, with an explicit ban on writing the span). That settled it:
`child` in both, and no span or digit has leaked into any output since.

**Test round**: `tests/describer_character.json`, 20 cases, archived at
`reference/test_archive/REF2VA/Describer-Character-v1.txt` (drift evidence before/after the
calibration change archived alongside it). **20/20 format-clean, all five drift probes stable.**
Zero pose/position/gaze/environment/style leakage, and no franchise name from `miya.jpg`'s
printed title, `kasia.png`'s watermark, or the two well-known film stills.

Two kinds of drift probe, both driven by a `same: ...` group name:

- **Same image, different SUBJECT wording** (`pancakes.png`) — isolates prompt-side instability
  with image variation removed. Produced byte-identical `[[APPEARANCE]]` lines.
- **Different images, same person** (`jacket`/`jacket2`, `p4_first`/`p4_last`) — the real stress
  case. **Caveat recorded in the test file**: the p4 girl is genuinely borderline (~12–13, sitting
  on the child/pre-teen/teenager boundaries), so a disagreement there is ambiguity in the subject
  as much as a defect in the prompt. Read the pancakes pairs first.

Accepted cosmetics, not worth chasing (`L-KNOW-WHEN-TO-STOP`):

- `[[LABEL]]` copies the user's SUBJECT wording when given one, so a scene-specific phrase like
  "the girl with braids at the right-hand desk" can end up in a durable label. User-requested, so
  arguably correct.
- Free-text `build` still drifts between records of one person ("lean"/"medium", "slim"/"slender").
  Only `[[APPEARANCE]]`'s age is closed-vocabulary. Candidate for the same treatment if it ever bites.
- `miyu.png` (heavily occluded, pixel art) produced some invention where "not visible" was wanted —
  consistent with the known "dim/occluded scenes degrade object-state reading" limitation.

Bracket coverage in the current round: child, adult, young adult, teenager, older adult, and
`young` (animal). Untested: infant, toddler, pre-teen, middle-aged, `old` (animal).

## Setting describer (v5, session 6)

`prompts/describer_setting.txt` — the second REF2VA describer role. **One place, durably**: what
the place permanently is, never what is happening in it. Eight fields, condensations last:

```
[[SETTING_KIND]] [[STRUCTURE]] [[CONTENTS]] [[DISTINGUISHING]] [[PLACE]] [[ATMOSPHERE]] [[LABEL]] [[DEFINITION]]
```

`[[LABEL]]` + `[[DEFINITION]]` splice downstream exactly as `character`'s do, into the guide's
own §7 phrasing: `<Subject 1> is the coffee-shop environment in <Picture 1>, with ...`.

**`[[PLACE]]` sits fifth, not second.** Naming "a classroom" *before* describing it invites the
model to fill in a stereotype of a classroom rather than report this one. It is a condensation,
so `L-JUDGMENTS-LAST` applies to it as much as to `[[LABEL]]`. `[[SETTING_KIND]]` stays first because it
is a closed two-value discriminator, not a condensation.

**`[[SETTING_KIND]]` is decided by where the CAMERA is**, not by what is visible — a shopfront
from the pavement is `exterior` however much shop interior shows through the glass; a room with
a street outside its window is `interior`. Verified on `bookshop`, which got it right in every
round. Images with no environment at all (a studio backdrop, a black void) are **always
`interior`**, an arbitrary tie-break that exists only so two records of one blank ground cannot
disagree — v1 had them split `exterior`/`interior`/`exterior`.

### The atmosphere quarantine — the session's main design decision

The user chose to keep light and weather in the reference rather than exclude them the way
`character` excludes pose. The risk is obvious: the same place at a different hour yields a
conflicting record. So the design **quarantines** rather than mixes:

- everything transient lives in `[[ATMOSPHERE]]` and nowhere else
- `[[DEFINITION]]` may never draw on it, so the spliced subject-definition sentence holds by day
  and by night
- `[[ATMOSPHERE]]` sits last among the descriptive fields, so it can be deleted later without
  unpicking prose if it proves unworkable

**A one-line ban was not enough — this is `L-SAY-WHAT-TO-WRITE` in a third costume.** v1 leaked
transient conditions into `[[DEFINITION]]` five times, and the `city_day`/`city_night` probe
failed outright: the two records shared only "a dense cluster of high-rise buildings". The
diagnosis was not the brand-signage confound that was predicted, but something more basic —
**by day the model describes forms, by night it describes lights.**

Two rules fixed it, both of the same kind that fixed age drift (say what to write, not just what
to avoid):

- **NAME THE FORM, NEVER THE GLOW** — "a cross-shaped mast on the roof", never "a glowing cyan
  cross"; "a row of tall windows", never "thousands of lit windows"
- **THE DAY-AND-NIGHT TEST** — before writing `CONTENTS`, `DISTINGUISHING`, and `DEFINITION`, ask
  of every item whether you would still write it twelve hours later

`validate.py` gained a matching check: it warns when `[[DEFINITION]]` carries a word from
`ATMOSPHERE_WORDS`. A warn, not an error — a snow-covered park is arguably structural, so a
human decides.

### Version history

| round | result |
|---|---|
| v1 | 25/26 format-clean. Five atmosphere leaks; city probe failed; example-bleed emitted `[[SUBJECT NOT FOUND]] the ringing chamber` (a SUBJECT line from the prompt's own example 2); "corn flakes" printed text leaked; movable clutter (gun oil, ammunition) in `CONTENTS`; `set_notfound` silently failed to emit its line; no-place `SETTING_KIND` inconsistent |
| v2 | Leaks 5→1, city probe now shares a landmark, printed text and clutter fixed, `set_notfound` correct, no-place kind consistent. **But 21/26** — a paragraph added to catch the v1 `set_notfound` miss made the conditional line salient and handed it the word "kitchen"; five records emitted invented subjects, including `[[SUBJECT NOT FOUND]] the kitchen` against a kitchen. **`L-KNOW-WHEN-TO-STOP` exactly: the added rule cost another.** |
| v3 | The v2 paragraph reverted and replaced with a mechanical gate: look for the characters `SUBJECT:` in the input first; if absent, the line cannot exist; the line may only repeat text copied from the input. **23/26** — better, still wrong, and diagnostically decisive (below) |
| v4 | **`[[SUBJECT NOT FOUND]]` removed from this role entirely.** **25/26**, zero spurious tail lines, both `SUBJECT:` cases correct. The one failure was unrelated — `set_forest` omitted `[[CONTENTS]]`, which unlike `[[DISTINGUISHING]]` had never offered `"none"` |
| v5 | `[[CONTENTS]]` gained the `"none"` option, with open country/forest/water named as the cases that need it. **25/26** — `set_forest` fixed; the one failure was `set_miya` repeating its own `[[DEFINITION]]` line verbatim, a stutter rather than a rule violation |

**v4 and v5 both scored 25/26 and failed on *different* cases** — v4 on `set_forest` (a real gap,
fixed), v5 on `set_miya` (a duplicated line, not a rule). That is the session-4 reproducibility
caveat showing up exactly as documented: a lone moving failure is sampling noise, not a defect to
chase. The locked version is **v5**.

### Why `setting` has no `[[SUBJECT NOT FOUND]]` line — a deliberate divergence from `character`

Across v1/v2/v3 that one optional line caused **every single format failure** — 1, then 5, then
3 cases — always by confabulating a subject that was never in the input (`the kitchen` against a
kitchen, `the snowy park`, and `the girl`, which is not even a place).

v3 was the decisive round. On the two cases that actually carry a `SUBJECT:` line it got both
**backwards**: it fired on `set_p6_outside`, where the named view through the window *is*
visible, and stayed silent on `set_notfound`, where the beach genuinely is not. Zero for two on
the only cases the mechanism exists to serve, while breaking three that never needed it.

The role does not need it. `character` must choose among six people in a classroom, so a
"couldn't find them" signal is real. A setting image has **one** place the camera is standing
in; a `SUBJECT:` line here is a refinement ("the street outside the window"), not a
disambiguation, and the model handles refinements correctly by simply describing. `validate.py`
now treats the line as an error for this role (`not_found: False`, the flag originally added for
`describer_style`).

Generalisable: **an optional output element that fires on judgement is a liability unless the
role genuinely needs the judgement.** Worth weighing before giving `object` or `style` one.

**Known residuals, not chased** (`L-KNOW-WHEN-TO-STOP`):

- a cereal carton still survives the movable-clutter ban in `p3`, and is still described as
  having "green lettering" — the brand name is suppressed, but the fact of text is not
- one `[[DEFINITION]]` per round still carries a banned transient word (`fog` in `set_forest`)
  despite an explicit list — 25/26 compliance against v1's 21/26
- **the city day/night pair still only partly agrees.** v4 shares "a dense cluster of high-rise
  buildings" and the stepped tower; the day record additionally names gold cladding and a copper
  roof that the night image genuinely does not show. That last gap may be irreducible: it is a
  limit of the photograph, not of the prompt
- **reframing costs more than relighting.** The `p6` wide/close pair agrees less well than the
  `city` day/night pair does. A tighter shot simply contains less place. Worth knowing before
  trusting any single frame as an environment reference

**The automated drift check is near-worthless for this role, by construction.** Its drift field
is `[[SETTING_KIND]]`, which is only interior/exterior, so all six `same:` groups passed it in
every round while `[[DEFINITION]]` drifted badly in v1. The real signal is `[[DEFINITION]]`
stability across a `same:` group and **nothing automated checks it** — read those lines by eye.
Recorded in `tests/describer_setting.json` itself so it cannot get lost.
