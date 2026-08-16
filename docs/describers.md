# Describer prompts

Design and version history for the standalone describer prompts — the per-image passes that
produce structured `[[FIELD]]` records for FL2VA and REF2VA composition.

Roles built so far: **frame** (v8), **character** (v1), **setting** (v5, locked), and **style**
(split into look v3 + class **v4e**, **locked session 20**). `object` is not built yet; it was
deliberately blocked behind `style` so it would not harden conventions that were still moving, and
that block is now **lifted**. See
`.claude/TODO.md`. Lessons cited by slug (`L-...`) are defined in
`.claude/lessons_learned.md`. The test corpus these were validated against is documented in
`docs/image_inventory.md`.

Moved out of `.claude/CLAUDE.md` in session 8 — that file is gitignored, so this reasoning had
no backup while the prompts it justifies did.

## Frame describer (v8, session 4)

Two v4-era bans the model never actually obeyed are now permitted: naming a held object in
`[[POSE]]`, and stating `[[POSITION]]` purely relative to another described person (must still
pair with a frame-absolute term, e.g. "background centre, partially occluded by the girl in
the foreground"). Added: a `[[CHAR]]` label must agree with its own `[[CLOTHING]]` line.
Rationale reconstructed from the pre-repo v1–v7 version history (now at
`reference/retired/prompts/`) and a discussion transcript the user dropped in mid-session (not
kept — its content is now captured here) since neither session memory nor the handoff had the
actual reasoning. Both relaxed bans were confirmed **already violated 6/6 in the unpatched v7
output** before this change — legalizing them changed nothing in model behavior.
Regression-tested across 8 cases
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

Prompt text for these versions: `reference/prompt_archive/`, except where `ARCHIVE.md` records it
as lost — which for `setting` is **v1–v4**, so only v5 can be read back.

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

**It generalises, and applies to every role still to come:** where a role's closed drift field is
coarse, the automated drift check is a formality and the eye is doing the work. Weigh that when
choosing the drift field for `object` and `style` — a two-value field buys nothing.

**`style` is the payoff of that warning** — its drift field has 11 values and it caught two real
failures on its first round. See below.

## Object describer (v3, session 22; `[[SCALE]]` vocabulary settled session 24) — the last describer before the composer

`prompts/describer_object.txt` — the fourth REF2VA describer role, covering **object / prop /
clothing** in one prompt. **One thing, durably**: what it permanently is, never how this picture
happens to present it. Nine fields, condensations last:

```
[[OBJECT_KIND]] [[FORM]] [[MATERIAL]] [[TEXT]] [[DISTINGUISHING]] [[SCALE]] [[KIND]] [[LABEL]] [[DEFINITION]]
```

`[[LABEL]]` + `[[DEFINITION]]` splice downstream exactly as `character`'s and `setting`'s do.
`[[OBJECT_KIND]]` leads because it is a closed two-value discriminator; `[[KIND]]` sits eighth
because it is a *condensation* and `L-JUDGMENTS-LAST` applies to it just as it does to
`setting`'s `[[PLACE]]`.

### Presentation is EXCLUDED, not quarantined — the design decision

`setting` kept transient conditions and quarantined them in `[[ATMOSPHERE]]`. `character` excluded
pose outright. **`object` follows `character`.** An object's transient axis is presentation and
state — worn, laid flat, folded, held, hung, open, full, switched on, and what is inside it — and
none of that has a downstream use, so there is no `[[STATE]]` field to hold it. The positive twin,
per `L-SAY-WHAT-TO-WRITE`, is **NAME THE THING, NEVER ITS ARRANGEMENT** ("a wide woven shoulder
strap", never "a strap slung over the shoulder") plus **THE FLAT-AND-WORN TEST**.

**It works.** The `kasia_swimsuit` group (flat lay → worn in 2D → worn in 3D) agrees across all
three on *black one-piece, high neck collar, sleeveless, deep yellow V-panel*, with no arrangement
language anywhere. That group is the direct analogue of `city_day`/`city_night` for `setting`.
Caveat recorded in `docs/image_inventory.md`: the flat-lays are **derived** from the 2D image, so
this is a floor on difficulty rather than a ceiling.

### This role REPRODUCES text — a deliberate divergence from `setting` and `character`

`[[TEXT]]` carries visible lettering verbatim in double quotes, on `describer_frame`'s exact
wording. Official guide § 4.5 requires it downstream, and an object's lettering is frequently
constitutive of its identity. **So the four roles split two-and-two**: `frame` and `object`
reproduce text; `setting` and `character` suppress it, because a room record has no business
carrying a cereal brand.

It is the strongest result of the first rounds — `lincoln_money` returned seven quoted strings,
`gromit`'s van `"GNOME IMPROVEMENTS"` / `"No job too small"`.

### Version history

| round | result |
|---|---|
| v1 | **29/35 format.** Three defects diagnosed, one mechanism each: the SUBJECT line overrode the image; printed names laundered out of `[[TEXT]]`; the tail line fired empty ×6 |
| v2 | **32/35.** Subject-override **fixed**, `[[SCALE]]`-on-garments **fixed**, laundering unmoved at 4 |
| v3 | **31/35 raw.** Removing the phrase the tail line was stealing only moved the theft; inside noise vs v2 |
| v3 + graph mechanic, +4 cases | **38/39.** Same prompt; the tail line is now stripped in code |

### Three findings worth carrying forward

**1. The SUBJECT line was supplying content, not just selecting it.** v1 answered
`SUBJECT: the yellow jumpsuit` against `april_fanart` — a *different* outfit — with a full jumpsuit
record, "one-piece … full-length legs", against an image of a cropped jacket over jeans. The fix
was a positive rule (`THE SUBJECT LINE SELECTS; IT NEVER SUPPLIES`) plus the instruction that
`[[KIND]]`/`[[LABEL]]` name what was *actually described*. Confirmed on the hardest available case:
`SUBJECT: the telephone` against `maggie_grandpa_cat` — same room, phone genuinely present in the
sibling frame — correctly described the litter box and emitted the tail line.

**2. `L-NAME-THE-CASE` bit, twice, in its documented form.** v2's new rule quoted
`"the yellow jumpsuit"`; the tail line then emitted exactly that on cases with no SUBJECT at all.
v3 removed the phrase, and the theft **moved to `"the red kettle"`** — the MATCH GENEROUSLY worked
example. Three rounds, three different stolen phrases, all on SUBJECT-less cases. A banned quote is
still an example, and so is an unbanned one.

**3. That is what forced the tail line into code.** See `docs/graph_mechanics.md`. The judgement
is only real when a SUBJECT line exists, and whether one exists is something the *caller* knows for
certain — `L-OFFLOAD-BOOKKEEPING`. `validate.py` still errors on an unsolicited line, which is what
catches a consumer that forgets.

### Known limitations, not chased (`L-KNOW-WHEN-TO-STOP` — four rounds in one session)

- **Printed names launder into identification. UNMOVED across three rounds, 4 cases.** The model
  reads `"HEATH"` and writes `[[LABEL]] the beige and blue Heathkit computer`; `"ALPINE A 310 V6"`
  becomes "the blue Alpine coupe"; `"LINCOLN"` becomes "a portrait of Abraham Lincoln". The rule
  exists, names the banned outputs verbatim, and is not followed — the same *unfollowed-rule* shape
  as the `digital` over-attractor. **This is the top open defect.**
- **Colour drifts between renderings of one thing**, twice and in the same direction: the gordon
  trench coat (`brown` vs `mustard-yellow`) and the Simpsons couch (`mustard-yellow` vs `brown`).
  The user ruled the coat *defensible* — it is a night scene — but two instances on one axis is a
  pattern. **The cheap fix to try first is `setting`'s, transposed**: name the colour of the
  material, not the colour the light makes it, which is `NAME THE FORM, NEVER THE GLOW` for hue. A
  closed colour vocabulary was considered and deferred: colour is genuinely multi-axis
  (`L-ONE-AXIS-PER-VOCABULARY`), it would mean re-adding a `[[COLOUR]]` field to be enforceable,
  and there is no colour ground truth to measure it against.
- **`[[OBJECT_KIND]]` called a sofa a `garment`** on `ob_couch_clear` while its sibling got it
  right. One case, split within a pair, so read as marginal until it repeats
  (`L-MOVING-FAILURE-IS-NOISE`).
- **The tail line still contradicts itself on a plausible absent garment.** `ob_notfound_slippers`
  emitted `[[KIND]] a pair of slippers` *and* `[[SUBJECT NOT FOUND]] the slippers`, and dropped
  `[[DEFINITION]]`. The telephone probe next to it passed, so the garment direction is the harder
  one.
- **`[[SCALE]]` was in doubt at v3.** Fixed to `"worn on the body"` for garments (15/15 consistent
  after v2), but the object side had little to test it on beyond the figures, and dropping it was
  live. **Resolved the other way in session 24** — the field is saved by *closing* its vocabulary.
  See the next section.

### `[[SCALE]]` — the nine-term size ladder (settled session 24, not yet in the prompt)

**Status: the vocabulary, the answer key and the corpus exist; `describer_object.txt` does not yet
implement it.** v3 still emits free text. Writing it in is v4, deliberately sequenced alone.

**Why close it at all.** A paper pre-test mapped the v3 round's 24 free-text answers onto candidate
buckets at zero model cost, and the result decided it: **`"larger than a person"` alone carried 10
of 24** — a Kaypro, a CRT TV, a cannon, four cars, a sofa and a van. Four distinct sizes collapsed
into one phrase, so the field could not be wrong *legibly*. The same pass found `ob_bag_1` and
`ob_bag_2` answering `forearm-length` and `hand-sized` for one object at two angles.

**One axis: bulk compared to an adult body.** The bottom four rungs use the hand and forearm as
**rulers**; the top five use the whole adult body.

| rung | from | to | exemplars |
|---|---|---|---|
| `minuscule` | — | fits inside a **closed adult fist** | a coin, a key, a ring |
| `tiny` | — | no bigger than an **open adult hand** | a phone, a banknote |
| `small` | bigger than a hand | about a **forearm** | a cereal box, a frying pan, a shoulder bag, a portable radio |
| `modest` | bigger than a forearm | **plainly less bulk than an adult body** | a suitcase, a tower computer, a microwave, an end table, a small dining chair, a child's ride-on car |
| `medium` | **comparable to an adult body** — ~¾ adult height or more, or big enough to enclose or seat one adult | | an adult human, an executive office chair, a wheelie bin, a bumper car |
| `large` | clearly more than one adult | **up to a car** | any car, a sofa, a horse |
| `huge` | **bigger than a car** | **smaller than a house** | a van, a lorry, a bus |
| `gargantuan` | **a house** | up to a large building | an apartment block, a ship, an airliner |
| `colossal` | **bigger than any ordinary building** | — | a skyscraper, a mountain |

Four rules carry the design, and **every one of them comes from a defect found only when real
images were mapped onto the draft.** None was visible while the ladder was a list of words. That is
the transferable finding here, and it is why the key was built before the prompt.

**1. No rung is defined by how a thing is HELD.** The draft read `small` as *"needs two adult
hands"* and `modest` as *"carried with both arms"*. That is an **affordance, not a size**: a frying
pan spans about two hands but has a handle and is held with one; a cereal box likewise; a suitcase
needs both arms without a handle and one with. Worse, it **contradicts this role's own headline
rule** — the prompt bans recording how a thing is shown and names *"held, carried"* explicitly, so
the model would have been told never to note how a thing is held and then asked to size it by
exactly that. The bottom rungs use the hand and forearm as **rulers**, never as grips.

**2. Every comparison is to an ADULT.** The words *"a person"*, *"a human"* (unqualified),
*"someone"* and *"a child"* must never appear in a rung definition. A child **is** a person, so
"plainly smaller than a person" silently admits "smaller than a toddler" — which **inverts** the
`modest`/`medium` boundary. The two cases that force that boundary are the ones with a child sitting
in the vehicle, so the failure would have landed exactly where it was hardest to see.

**3. Every boundary is named from both sides, by the same object.** *A car* closes `large` and opens
`huge`; *a house* closes `huge` and opens `gargantuan`. The draft defined the bottom rungs by
physical reference and the top rungs by **occupancy count**, leaving `huge` with a floor and no
ceiling at all, and making `gargantuan`'s "holds hundreds of adults" contradict its own "a house"
exemplar — where hundreds would be a crush. **Occupancy is a tell, never a definition.**

**4. Occupancy is the tell, bulk is the axis.** *"Could an adult be enclosed or seated by it"*
decides hollow things; solid things go on comparable bulk. This separates a **small dining chair**
(seats an adult, nowhere near their bulk → `modest`) from an **executive office chair** (≈ ¾ adult
height and encloses one → `medium`). A pure occupancy test fails that pair; a pure *height* test
fails the bumper car, which is adult-**length** but low.

Rules 1–3 are one lesson, `L-A-RUNG-BOUND-MUST-BE-A-FIXED-SIZE`.

**`large`/`huge` keeps a statable test** — `large` tops out at a car, any body style; `huge` begins
above one. The rejected alternative was coupe-`large` / SUV-`huge`, a **fine and confusable**
discrimination of the kind that forced the `puppet`/`figure` merge.

**Garments now take their WEARER's size**, superseding v3's fixed `"worn on the body"`. That value
was 15/15 consistent, so it is traded for informativeness **deliberately** — watch it for the drift
the fixed value removed.

#### The depiction case — resolved, and no longer moot

`[[SCALE]]` describes the physical thing photographed, never what it depicts: a toy is toy-sized.
`april_1987_figure` answered `forearm-length` in v2, the intended reading, and the user flagged the
depicted-scale reading (person-sized) as a stubborn alternative likely to return.

Under v3 that fixture was **moot** — the jumpsuit classified as a `garment` either way and took the
fixed garment value, so the disagreement had nowhere to show. **Making garments take their wearer's
size removes the escape hatch**, and the case becomes live and scorable, which is an argument for
the change rather than against it.

It is now an **accept-set `{tiny | medium}`** in `tests/describer_object_scale.json`, `tiny` primary
— `docs/image_inventory.md` classifies that file `stop-motion / figure` *"classified by the
objects"* — with `medium` forgiven for the in-scale-diorama reading. Its strict controls, required by
`L-AN-ACCEPT-SET-IS-A-HYPOTHESIS`, are `obsc_phone` (unambiguously `tiny`, no depiction reading
available) and `obsc_jumpsuit_real` (**the same garment and the same `SUBJECT:` line** on a
full-size adult). The wider family where the split can arise is `stop-motion / figure` — `lego1`,
`lego2`, `coraline1`, `coraline2`, `skellington`, `rudolf`, `laika`, `pjs` — none in either test yet.

**Keep two rules apart here.** *World knowledge may determine physical size* when the frame offers
no reference — a banknote is `tiny` because banknotes are hand-sized, and that is what stops
`not determinable` absorbing every isolated shot (it took 4 of 24 in the v3 round). *Depiction vs
physical* is a different question and applies only to miniatures, models and figures. Conflating
them was a live error during the session-23 design and is corrected on the record.

#### `colossal` has no sample, deliberately

Everything colossal is terrain or architecture, which `describer_setting` owns; the only conceivable
filler is a sci-fi spaceship, with no real-world example — even the ISS reads `gargantuan`.
Admissible under `docs/image_inventory.md` § "Adding a term the corpus cannot exercise", whose
precondition is a **statable** tell, and here it is: "bigger than any ordinary building".

The same reasoning is why `car_building_gargantuan` and `car_mountain_colossal` are keyed **`large`**
rather than by their filenames: a palace is a place and a mountain is terrain, so asking this role to
describe either contradicts its own `WHAT YOU LEAVE OUT` rule. They probe instead that an enormous
backdrop does not drag `[[SCALE]]` up a ladder anchored on absolute adult comparison rather than on
share of frame.

#### Where the key lives

`tests/describer_object_scale.json` — 27 cases, `"_gate": "enriched"`, full `_expected` on
`[[SCALE]]`. Score with `--fields SCALE`. Eleven cases are imported from the main object test and
were keyed **independently twice** (the user's session-22 ground-truth fill-in, and the ladder's rung
definitions); **all eleven agree**.

## Style describer — LOCKED session 20 at look v3 + class v4e

**Final state:** `describer_style_look.txt` v3 (1,876 tokens, untouched since session 12) feeding
`describer_style_class.txt` **v4e** (3,732 tokens). Full-corpus two-pass confirmation:
**159/187 content**, format **186/187** on pass A and **186/187** on pass B.

### What session 20 changed, and how it was measured

The classifier's `ANIME vs WESTERN TOON` ladder had **no entry condition** — a two-way choice that
contains neither `flat graphic` nor `realist`, with nothing saying when an image is eligible for
it. Two doors led in, and each explains a miss cluster:

- **The flat door.** The flat-two-tone clause ended *"decide between the flat idioms on their own
  evidence below"*, routing every flat image into that ladder. Vector landscapes with no figure
  landed on `western toon`.
- **The stroke door.** Step 2's anime tell — *"a large eye with a defined iris standing as its own
  shape apart from the pupil, usually with a specular glint"* — **describes a real human eye**, so
  naturalistically painted people resolved to `anime`.

**Both were run as separate arms, and that is the durable finding.** On frozen pass A over the
130-image sweep: v4c 104, flat-only 107, stroke-only 106, **both 110**.

**The doors repair each other.** `april_1987` and `molly` go PASS → miss (flat alone) → PASS
(stroke alone) → PASS (both): the eye guard restores exactly the western/anime discrimination the
flat door's placement weakened. Arm C beats `max(A, B)` by three cases, so this is a positive
*interaction*, not addition. Shipping "both" without the arms would have shown 110 and concealed
that the flat door alone regresses an archetypal western cartoon **and collapses two strict
controls** (`april_1987`, `ivy_toon`), which would have made two accept-set passes unearned.

IDIOM net +5 (7 fixed, 2 lost). All four IDIOM controls hold, identical to v4c. The user ruled all
five surviving misses **forgivable** and declined an accept-set for each — explicitly so for
`forest_day_night` ("doing an accept would be harmful").

`vintage Technicolor` was then removed from `[[TREATMENT]]`, which is the only difference between
v4d and the shipped v4e.

### The noise floor is wider than session 17 measured — read small movements accordingly

The confirmation run re-ran pass A live for the first time since session 17 Round 0, against the
identical classifier. **12 of 187 cases moved (6.4%)**, net −2, and several movers
(`car_interior_toon`, `girl_painting`, `city_day`) are *not* in the five documented-marginal cases
Round 0 identified at 3.8%. `look_rugrats` also produced a spontaneous format failure from an
**unchanged** prompt.

So a 1–2 case swing on a two-pass round is noise. The v4d evidence survives this because it was
measured on **frozen** pass A, where the evidence set is held byte-identical across arms — which is
precisely what that harness exists for.

### `digital` — recorded as a capability ceiling, not an open task

Three attempts have now failed to move it: `look` v4 (reverted), `class` v4b (inert), and the
structural option below (declined on evidence). It remains the largest cluster — about 11 of the
remaining misses (`ink→digital` ×4, `marker→digital` ×4, `oil→digital`, plus MEDIUM cascades).

**Do not re-open it without new evidence, and know that two standing rationales are dead:**

- *"`digital` appears in 5 of the 6 sub-lists, so it is the highest-prior term by construction"* is
  **stale**. After session 17 dropped `2D cel`'s sub-list and merged `puppet` into `figure`, it is
  **3 of 5**.
- *"Remove `digital` from `drawing`'s sub-list"* — the one untried structural lever — would
  **re-break `kiki`**. `drawing / digital` has exactly two samples, `kiki` and
  `car_interior_sketch`, and `kiki` is the session-16 correction where the model was right and the
  answer key was wrong. Breaking it to fix four marker cases trades a known-correct call for a
  guess.

Session 20 declined the third attempt deliberately, on `L-KNOW-WHEN-TO-STOP`.

### Other surviving misses, all previously ruled

`annie2` (nesting is never perceived — a capability ceiling), `castle`, `gromit` (clay/figure),
`lincoln_money` (treatment), `kasia_swimsuit`, and the painterly cluster
(`blonde_`/`saber_`/`uniform_reference_painterly`), which the eye guard did **not** fix.

## History — the v3 split (session 12)

The third REF2VA describer role, and **the inverse of the other three**: it records how an image is
rendered and never what it depicts. The other roles all ban style words; this one bans everything
else, which is the harder direction, because an image invites you to say what is in it.

**It is the only role that is two prompts.** Ten fields were more than one prompt could hold — see
"Why it is two passes" below. Condensations still come last, and the ten fields and their order are
unchanged from v2; only the seam between them is new:

```
pass A — prompts/describer_style_look.txt      (role style_look,  1,876 tokens)
  [[EXECUTION]] [[PALETTE]] [[LIGHTING]] [[DISTINGUISHING]] [[LABEL]] [[DEFINITION]]

pass B — prompts/describer_style_class.txt     (role style_class, 2,584 tokens)
  [[MEDIUM]] [[SUB_MEDIUM]] [[IDIOM]] [[TREATMENT]]
  input: the image AND pass A's whole record
```

The consuming graph concatenates the two into the same ten-field record v2 emitted, so nothing
downstream changes.

### Why it is two passes

v2 measured **3,740 tokens against this model's ~3,700 adherence ceiling** — over the line, with the
`L-PROMPT-TOKEN-BUDGET` failure signature to prove it (a 171-token rule took format from 43/45 to
39/45, emitting `[[DISTINGISHING]]` with correct content underneath). Both remaining fixes needed
*more* room, so the only move that made room instead of consuming it was to split.

The seam is not arbitrary — each half's bulk is dead weight to the other. The vocabulary is 1,651
tokens and irrelevant while describing; `CONTENT IS NOT STYLE` (461) and the examples are irrelevant
while classifying. Two things follow that no amount of prose could buy:

- **Derivation became architectural.** Pass B *receives* the description, so "classify from what you
  described" is the shape of the task rather than a rule competing for attention. v2 tried to buy
  this with a rule and paid four format failures for it.
- **The content ban stops binding the classifier.** Pass B emits four closed-vocabulary terms and
  cannot leak content, so it can later be licensed to judge facial proportion and caricature —
  which is what the `western toon` collapse needs and what v2 structurally could not allow.

`[[LABEL]]` and `[[DEFINITION]]` went to **pass A**, which is what keeps that true. The accepted
cost: in v2 the label was written *after* the four terms and so could not contradict them; now it
is written without them, and nothing checks the coherence. Two inference calls per image, ~5s → ~10s.

The four classification fields carry **three independent axes** — `[[MEDIUM]]`+`[[SUB_MEDIUM]]`
are one axis at two levels. Full vocabulary and rationale in `docs/image_inventory.md`
§ "Style vocabulary"; the short version is that the session-9 two-level vocabulary mixed five
axes inside its sub-lists, and that coupling was dragging the *coarse* term to the wrong value.

`[[LABEL]]` + `[[DEFINITION]]` splice as the other roles' do:
`<Subject 1> is the flat anime cel style of <Picture 1>, with thick uniform black outlines, ...`.
The record also feeds the §5.2 style opening, the one or two sentences that precede `[Shot 1]` in
`detailed_description`.

**`[[MEDIUM]]` comes after the descriptive fields, never before them**, unlike `[[SUBJECT_KIND]]`
and `[[SETTING_KIND]]`. Those are binary discriminators; `[[MEDIUM]]` is an 11-value *condensation
of the look*, so it behaves like `[[PLACE]]` and `L-JUDGMENTS-LAST` applies. Naming "2D cel / anime"
first invites generic anime descriptors instead of a reading of this image. It sat seventh of ten in
v2; in v3 it is the first line pass B writes, which is the same thing — the description is already
finished and on the page in front of it. The split *hardens* this ordering rather than relaxing it:
the classifier physically cannot run before the describer.

**All four classification fields are always emitted**, with `none` and `not determinable` as
permitted `[[SUB_MEDIUM]]` values. This is `L-DECLARED-FIELD-IS-AN-OBLIGATION` used deliberately *for* us: a listed
field gets filled, so the sub-term cannot quietly go missing the way an optional element would.
It worked — **39/39 records emitted it**, `none` was correct for all four sub-less coarse terms,
and no record invented or borrowed a sub-term. `validate.py` checks the pairing mechanically
(`coarse_sub`), the strongest content check any role has.

### Version history

Prompt text for these versions: `reference/prompt_archive/`, except where `ARCHIVE.md` records it
as lost — which for `style` is the **derivation-rule round** (4,054 tokens, 39/45), the one point
of real degradation behind `L-PROMPT-TOKEN-BUDGET` and now unrecoverable.

| round | result |
|---|---|
| v1 | **36/39 format-clean, 27/33 exact on scorable cases** (6 unscorable — 5 `amb` plus contested `kasia`). Zero franchise or real-place names across the whole round. 6/39 leaked a garment or body part. Tie-breaks: 1 ✓, 2 ✗, 3 half, 4 ✓ |
| v2 | **REVERTED. 23/33** — two added tie-break rules fixed **none** of their four targets and broke three unrelated cases. See `L-KNOW-WHEN-TO-STOP` and the note below |
| v1 repeat | **27/33, identical `[[MEDIUM]]`/`[[SUB_MEDIUM]]` on all 39 cases.** Confirms the revert and proves the v2 regressions were the prompt, not sampling |
| v1 full sweep | All 100 images, `tests/describer_style_sweep.json` (generated from the master table). **95/100 format-clean · coarse 86/95 · sub 77/84 where coarse was right.** Higher than the targeted round because that one was deliberately loaded with hard probe pairs |
| v2 baseline ×2 (s11) | 45-case targeted test. **27/45 content, 43/45 format — byte-identical across two runs**, on all 45 records. Attribution is clean; a one-case delta is real, not drift |
| v2 + derivation rule (s11) | 4,054 tokens. Content 29/45 but format **39/45**, with corrupted field tokens over correct content — the budget signature. Reverted |
| v2 compressed (s11) | Prose tightened, no rule changed. 3,740 tokens, **27/45 content, 45/45 format** — the best format recorded. Kept. Its baseline moved to `reference/retired/tests/describer_style_targeted-BASELINE-s12.txt` when the targeted test was retired in session 17 |
| **v3 split (s12)** | Pure refactor, same vocabulary and tie-breaks. **Format: look 45/45 · class 44/45. Content 29/45** (30 after the `coraline1` ruling), from 27. Movement: fixed 6 · regressed 4 · changed 4, `R=4` vs threshold 7 → adjudication. **`western toon` 1/7 → 6/7**, see below |

**Two findings from session 11 outrank any single round above.** First, determinism is not
stability (`L-DETERMINISM-IS-NOT-STABILITY`): the compression round changed no rule, term or
tie-break and still moved **10 of 45 cases** — `p5_first` and `p5_last`, two frames of one film,
*swapped* `vintage Technicolor` with each other. So "this change fixed 3 cases" is weak evidence on
this prompt; prefer changes with a mechanism behind them over changes with a case count. Second,
**`western toon` is collapsing at 1/7 (14%)**, losing evenly to `anime` (×3) and `dimensional toon`
(×3), while every other idiom scores 82–100% and `dimensional toon` is 5/5 when it *is* the answer —
a pure over-attractor, not a confused term.

**Not locked.** v3 splits the prompt so those fixes become affordable; it was written as a pure
refactor and expected to be a new baseline rather than an improvement.

### What the split actually did to `western toon` — the session-12 surprise

**It went from 1/7 (14%) to 6/7 (86%) on the same seven images, with no rule changed.** Only
`supergirl2` still misses, and that is the one the user had already called genuinely blurry. The
proportion licence that the split existed to make affordable **was never written** — the planned
anime stylization band is on hold, because the problem it targeted did not survive the refactor.

Per-idiom on that round: realist 88% · western toon 86% · anime 83% · dimensional toon 100% ·
flat graphic 0/1.

**Do not attach a mechanism to this.** `L-CAUSAL-STORIES-ARE-WEAK` has cost this project three
rounds, and a plausible story about *why* separating description from classification helps is
exactly the shape of the ones that were wrong. What stands is the measurement: five cases moved
one way on an axis that had been stuck across four session-11 rounds and both session-10 sweeps,
which is well past the ~20% marginal churn `L-DETERMINISM-IS-NOT-STABILITY` documents.

**The caveat that matters:** the targeted test is *enriched* and holds only seven `western toon`
images, so 86% is measured on the hardest slice of the corpus, not a representative one.

### The largest remaining cluster: `digital` over-attracts

14 emitted against 10 expected, taking one each from `oil`, `ink`, `marker` and `traditional cel`.
**It is carried over, not caused by the split** — the word "digital" appearing in the description
predicts a `digital` sub-term in 13/20 split records and 12/18 pre-split records, so the
association is pre-existing and essentially unchanged. This is the same defect the older
"`painting / digital` is a sink" note describes.

The user's ruling is that the asymmetry matters: failing *toward* the physical term is acceptable,
failing toward `digital` is not. Before writing anything, note that **tie-break 4 already says
exactly that** — so this is an unfollowed rule, not a missing one, and restating it is the
`L-KNOW-WHEN-TO-STOP` treadmill. `digital` also appears in 5 of the 6 sub-lists, which makes it
the highest-prior term by construction.

> **Superseded, session 20.** The "5 of the 6 sub-lists" figure above was true when written and is
> **no longer** — session 17 dropped `2D cel`'s sub-list and merged `puppet` into `figure`, leaving
> `digital` in **3 of 5**. See "`digital` — recorded as a capability ceiling" near the top of this
> section for the current position and for why the remaining structural option was declined.

### v2 — the three-axis rebuild (session 10)

The vocabulary work is documented in `docs/image_inventory.md`. What changed in the *prompt*:

- Field list 8 → 10; `[[IDIOM]]` and `[[TREATMENT]]` added between `[[SUB_MEDIUM]]` and
  `[[LABEL]]`, keeping `L-JUDGMENTS-LAST` intact — every condensation still follows the
  descriptive fields.
- A new vocabulary preamble stating the axes are **independent**, with the concrete claim the
  old vocabulary could not express: *"There is anime drawn in pencil, anime built from pixels,
  anime rendered in 3D."*
- Old tie-break 3 (idiom vs substrate) was **absorbed into tie-break 4**, which now reads as one
  general rule — judge on presentation, not provenance, *on every axis* — rather than two rules
  that happened to point the same way.
- Two new tie-breaks: **5** archival needs age visible on the surface, and **6** visible drawing
  process beats flat colour when choosing between `drawing` and `2D cel`.
- `2D cel` and `drawing` **definitions tightened**. `2D cel` had read "areas of flat colour
  bounded by outlines", which admits any flat-filled art; it now requires *finished* animation
  artwork. `drawing` now names the evidence — varying line weight, contours that do not close,
  construction lines.

#### Two results worth carrying forward

**The headline prediction was wrong, and the fix still worked.** Session 9 concluded that
`car_interior_sketch` was forced to `2D cel` *because* `anime` lived only there. Given
`[[IDIOM]]` as its own field, it said `2D cel` anyway — its own `[[DISTINGUISHING]]` named "the
rough, hand-drawn quality of the outlines and the visible construction lines" and it still chose
`2D cel`, weighing flat colour over linework. **The coupling was not the cause.** What fixed it
was tightening the `2D cel` definition. Worth remembering before trusting a single-round causal
story about *why* a model chose a term: the diagnosis was wrong even though the round it came
from was real.

**`L-NAME-THE-CASE` bit again, in its documented form.** A rewritten tie-break 5 named the case
as a *negative* example — "an old warship … is monochrome" — and the next run flipped
`destroyer_photo` from correct `monochrome` to `archival`. Naming a judgement you do not want
makes it more available, not less. Reverted to wording closer to the version that measured
correctly.

### What the sweep found — the vocabulary, not the prompt

**`drawing` was emitted once in 100 images** against five true `drawing` files, and all four misses
trace to the *sub*-term rather than the coarse term: the model correctly identified an idiom
(`anime` on `car_interior_sketch`, `digital` on `marker` and `supergirl1`, `watercolour` on
`annie1`) that only exists under a *different* coarse term, and the sub-term dragged the coarse term
with it. `painting / digital` is a sink for the same reason — 10 emitted against 7 true, because
`digital` is the only home for a digitally-made image.

**So the fix is a third vocabulary axis, not a prompt rule.** Full design note in
`docs/image_inventory.md` § "The sub level needs a third axis"; execution is the top item on
`.claude/TODO.md`. This conclusion came out of the adjudication pass (`L-CONTESTED-IS-A-VERDICT`) —
scoring those four as plain misses had already produced v2, which hammered rules at fixed
categories and made things worse.

### Why v2 failed — the most instructive result of the session

v2 added a drawing-vs-painting tie-break and a nested-image instruction, targeting `supergirl1`,
`annie1`, `annie2` and `woman_oil`. All four still failed. Three unrelated cases broke, each toward
a word the new rules introduced: `supergirl2` `sketch`→`marker`, `azumanga_toon` and
`peter_griffin_toon` `western toon`→`anime`, `girl_painting_reference` `live-action film`→
`photograph`.

The drawing-vs-painting rule quoted the offending record verbatim as banned, per `L-NAME-THE-CASE`.
The next round reproduced **near-verbatim the banned `[[EXECUTION]]` line** and kept the wrong
verdict. That produced the new limit now recorded on `L-NAME-THE-CASE`: **quote a bad output, never
a bad judgement.** A banned quote is still an example.

### Known limitations, not chased

- **Tie-break 2 (nested images) does not fire, and may not be fixable by wording.** `annie2` is a
  photograph of a watercolour held in a hand in a defocused hall; across v1 and v2 the model
  described only the inner artwork and never mentioned the hand or the hall. The nesting is not
  being weighed and rejected — it is not being *perceived*. Treat as a capability ceiling.
- **`painting / digital` is a sink.** Anything smooth lands there, including `woman_oil`
  (a photorealist oil) and `supergirl1` (marker). The cause is structural, not a wording problem —
  see the sub-list axis note below.
- **The `drawing` and `painting` sub-lists mix axes**, exactly the defect the two-level coarse
  vocabulary was designed to remove. `marker`/`ink` are instruments while `sketch` is a degree of
  finish; `oil`/`watercolour`/`gouache` are media while `digital` is a substrate. Documented in
  `docs/image_inventory.md` § "The sub-lists inherit the axis problem the coarse list was built to
  fix", with a decision pending on `.claude/TODO.md`. **Until it is settled, score the coarse term
  with confidence and treat a lone `drawing`/`painting` sub-term miss as contested.**
- **`2D cel`'s sub-list is the weakest in practice** — `anime` acts as the default. `ivy_toon` is a
  real miss; `kasia` is contested by the user's own read.
- Content leak is real but minor: 6 of 39 records named a garment or body part. Generic reference
  is used correctly in the majority ("the figure" ×19, "the background" ×13).
