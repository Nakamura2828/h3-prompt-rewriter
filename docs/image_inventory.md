# Image inventory — `images/`

Ground truth for the test corpus, built by **reading every file directly**, not by running a
describer over them. `validate.py` checks format and cannot see content; this document is what
lets us judge whether a describer said something *true*.

**187 active files.** `door_first` / `door_last` are **not** duplicates of `p1` despite once having
been filed that way — they are a different shot, and one of them is the most useful failure case in
the corpus (see "Known describer limitations").

**Session 15 added 30 files** in a targeted enrichment pass — see "What session 15 added" for what
they close and what they deliberately do not. **Session 18 added 57 more** — see "What session 18
added", which closes `drawing / pencil`, `toddler` and `pre-teen`, and finally gives the corpus
figureless anime and cartoon frames.

## How to maintain this document

Reorganised in session 8. It had previously grown one section per pass — three image tables, two
pair tables, two medium tallies, three gap lists — so answering "what do we have with vehicles in
it" meant reading the whole file. The rules below exist to stop that recurring.

- **New images append rows to the master table and the contents table.** Never open a new
  per-session table; the `added` column carries that information.
- **A correction edits the master/contents row in place *and* adds a row to
  "Corrections & superseded findings".** The tables are always current-truth; the corrections
  table is the audit trail. Do not leave struck-through prose behind.
- **`docs/` is git-tracked**, so superseded content can be *deleted* rather than carried — git
  has it. Keep only what still changes a decision.
- **The medium tally is generated**, not hand-edited. Run `scripts/inventory.py` (see TODO —
  not built yet) to regenerate it and to cross-check `images/` against the master table.
- The `medium`, `sub`, `idiom` and `treatment` columns use the **closed three-axis vocabulary**
  defined below — the vocabulary for `describer_style`'s four classification fields. Free-text
  nuance goes in `detail`, never in a vocabulary column, or the tally stops grouping.

**Flags:** `text` printed/legible text in frame · `real` real identifiable person or place ·
`franchise` recognisable licensed fictional character · `derived` derived from another corpus
file · `corr` has a row in the corrections table · `amb` **medium is not visually determinable** —
the classification rests on provenance the describer cannot see, so **do not score `[[MEDIUM]]`
on this image either way**.

**`added`:** `s6` session 6 · `s7a` session 7 first batch · `s7b` session 7 second batch ·
`s8` session 8 · `s15` session 15 · `s18` session 18 · `-crop` suffix for files derived in that session.

---

## Style vocabulary — closed, three axes

Adopted session 8 as a two-level medium list; **rebuilt on three axes in session 10** after the
full-corpus sweep showed the two-level version was itself causing coarse misclassification. This is
the vocabulary for `describer_style`'s four classification fields, not just an inventory
convention — classifying the corpus and designing those fields are the same job.

### The three axes

Every list below answers exactly one question. That is the whole design, and the reason the
previous version failed is that its sub-lists answered five.

| field | question it answers |
|---|---|
| `[[MEDIUM]]` | **how was it made**, coarsely |
| `[[SUB_MEDIUM]]` | **what do the marks read as being made with** — same axis, finer grain |
| `[[IDIOM]]` | **which tradition does the stylisation descend from** |
| `[[TREATMENT]]` | **which colour system / era does it present in** |

`[[MEDIUM]]` and `[[SUB_MEDIUM]]` are one axis at two levels, so there are three axes across four
emitted fields. All four are **always emitted**; `[[SUB_MEDIUM]]` takes `none` where its coarse
term has no sub-list.

### `[[MEDIUM]]` — 11 coarse terms, unchanged since session 8

`photograph` · `live-action film` · `3D CG` · `stop-motion` · `2D cel` · `comic` · `painting` ·
`drawing` · `vector` · `pixel art` · `print`

This column was **not** touched by the session-10 rebuild. It is the column that scored 86/95 on
the full sweep, and leaving it fixed is what makes the rebuild a re-derivation rather than a
restart.

### `[[SUB_MEDIUM]]` — what the marks read as made with

| coarse term | sub-terms |
|---|---|
| `stop-motion` | `clay` · `figure` · `model` |
| `comic` | `ink` · `screentone` · `digital` |
| `painting` | `oil` · `watercolour` · `digital` |
| `drawing` | `marker` · `pencil` · `ink` · `digital` |
| `print` | `engraving` · `halftone` |
| `photograph`, `live-action film`, `3D CG`, `vector`, `pixel art`, **`2D cel`** | *(none)* |

**Two merges landed in session 17**, both ratified by the user on their merits rather than on a
score. See "Session 17 — the vocabulary merges" for the full reasoning.

- **`puppet` merged into `figure`.** The two were not distinguishable in practice; `figure` is the
  more general term, covering a sculpted film puppet, an articulated plastic toy and a rigid
  set-clay sculpt alike. Agreed session 12, executed session 17.
- **`2D cel` lost its sub-list entirely** — it held `traditional cel` and `digital`. Measured
  recall on `traditional cel` was **2/7, with all five losses going to `digital`**, and the user
  ruled the era distinction not worth teaching. Dropping only `traditional cel` would have left a
  one-value list, which is not a vocabulary; worse, it would have made every `2D cel` record
  **assert** digital production downstream — including of hand-drawn cel animation like
  `april_1987` and `pocahontas`. `none` asserts nothing, which is the honest answer.

**`digital` is an instrument here, not a provenance claim.** It means the marks read as made with
digital brushes or fills — no medium physics, no wet edges, no canvas weave, uniform fills, even
line weight. An image that convincingly imitates a physical medium takes that medium's term
regardless of how the file was really produced, per tie-break 4. This is what stops `digital`
being the sink it was in session 9: it now has to win on marks, because tradition has its own field.

Terms defined by material rather than by origin, so they stay decidable from pixels:

- `clay` — **hand-remodelled deformable clay**: fingerprints and tool marks, irregular or
  asymmetric surfaces, contours that squash and bulge rather than holding a fabricated edge. The
  tell is **evidence of remodelling**, and it is present in a single frame — it does not require
  motion. Wallace & Gromit's Newplast and Gumby's plasticine are both non-drying and stay soft, so
  both show it.
- `figure` — **any fabricated character figure that does not deform.** Two families of surface,
  one term since the session-17 merge:
  - built film puppets — fabric, fibre hair, sculpted and painted matte surfaces, visible
    replacement-face seams;
  - moulded plastic toys — glossy injection-moulded surfaces, mould seams, articulated joints,
    printed or fixed facial features.

  **Rigid set clay (Fimo and similar) belongs here, not in `clay`** — once baked it is a
  fabricated rigid sculpt that does not deform. The single test across all of these is
  *fabricated and rigid*, which is what makes the merged term decidable where `puppet` vs
  `figure` was not.
- `model` — built miniature objects and sets with no character figure at all.

> **Why `clay` got a definition in session 15, and what it cost to notice.** It was the *only*
> sub-term in this list that never had one. Its siblings were each given a visual tell; `clay`
> silently fell back to "made of clay" — a **provenance** claim, which is precisely what this axis
> exists to avoid, and what tie-break 4 forbids everywhere else.
>
> It surfaced through `pjs` (foam) and `gromit` (Newplast). The describer inverted them: it reported
> *"painted foam and fabric… fibrous textures"* for the real clay and *"physically constructed clay
> figures… visible clay texture"* for the foam. That inversion first looked like image ambiguity,
> and `pjs` was nearly ruled `UNSCORABLE` on the theory that only motion can separate clay from
> foam. **That would have been wrong, and permanently so** — the ruling never expires. The user's
> observation is what saved it: deformation is the discriminator, rigid clay does not deform, and
> a rigid clay figure therefore is not `clay` at all.
>
> **The general trap:** an undefined term does not read as undefined. It reads as obvious, and it
> quietly answers a different question than the axis is asking. Check that every term in a closed
> vocabulary carries its own tell — a missing one is invisible until an image lands on it.

### `[[IDIOM]]` — which tradition the stylisation descends from

`anime` · `western toon` · `flat graphic` · `dimensional toon` · `realist`

- `dimensional toon` — caricatured, unrealistically proportioned character design rendered with
  **real dimension, material and light** rather than flat fills. Added session 10. It is what
  connects `coraline1`/`coraline2` to `shrek_cg`/`woody_cg`: the same tradition, one built as a
  puppet and one rendered digitally. That it survives a change of medium is precisely what makes
  it an idiom rather than a medium.

  > **Clarified session 15, after four images lost to this term in one round.** Flat two-tone
  > highlight-and-shadow shading is **not** dimension, however carefully it is placed. The user's
  > ruling on `boondocks`: *"it's the typical flat highlight and shadow shading common to 2D art,
  > no dimensionality at all."* The test is whether form is carried by **material and light** —
  > a surface that could be photographed — not whether the drawing has more than one tone.
  > `boondocks`, `car_interior_toon`, `beauty_beast` and `april_fanart` were all wrongly given
  > `dimensional toon` in the s15 round; all four are flat-shaded 2D.
- `realist` is the default and will be roughly half the corpus. That is a large bucket but a
  *correct* one, unlike the old `painting / digital`, which was large because it was the only
  available answer.

  > **Session 15:** `realist` extends to drawn and printed work that is *drawn realistically* —
  > it is not a synonym for photographic capture. The user's ruling on `gordon_comic`: *"it is
  > fairly realistic, and I'm not sure traditional comic book style is `toon`."* Mainstream
  > comic-book rendering with naturalistic proportion and anatomy is `realist`, not
  > `western toon`.

### `[[TREATMENT]]` — which colour system

`colour` · `monochrome`

**`vintage Technicolor` was dropped in session 20**, agreed session 12 and reaffirmed session 17.
It was a *process* term sitting on an axis that otherwise answers "which colour system", which is
the same category error that got `archival` dropped one paragraph below. It had exactly two
samples (`p5_first`, `p5_last`, both now `colour`) and the model never held it: session 11 had the
two frames swapping it between rounds, and the session-12 split lost it on both at once. Judging
a dye-transfer *process* from pixels is also a provenance call, which tie-break 4 forbids
everywhere else in the same vocabulary.

**`archival` was dropped after the first three-axis sweep.** It named an aged photographic
surface — sepia, foxing, scratches — and it looked reasonable on paper, but it never scored:
one wording over-fired it onto a clean well-preserved print (`destroyer_photo`), and the
correction under-fired it off the two images that genuinely are aged (`lincoln_photo`,
`teddy_taft`). A term that inverts on each rewording is under-specified, not nearly-right.

The decisive argument was the user's and it is about *purpose*, not accuracy: `monochrome` is
not wrong for an aged black-and-white photograph, only less precise, and a prompter who wants
grain and age can ask for it in words. `[[EXECUTION]]` already records grain and surface
damage in prose. Three images did not justify a fourth value on this axis.

### Tie-break rules

These exist so that two records of one image cannot legitimately disagree — the same job the
"no environment → interior" tie-break does for `[[SETTING_KIND]]`.

1. **`stop-motion` beats `photograph`.** A stop-motion frame is literally a photograph of physical
   objects, so without this rule `coraline1`/`coraline2` are defensibly photographic and will
   drift. What is photographed is a constructed miniature; that wins.

   **Extended session 15 — it is the objects that win, not the fact of animation.**
   `april_1987_figure` is a snapshot of moulded plastic figures on a shelf in a real room: not an
   animation frame at all, and the room is not a constructed set. It is still filed
   `stop-motion / figure`, because the sub-terms are defined by *material* precisely so they stay
   decidable from pixels, and the material here is unmistakable. This is what gives `figure` its
   only sample. It is the weakest member of the coarse term and a describer answering `photograph`
   is not being stupid — see "Rulings that may need revisiting".
2. **Nested images report the OUTER medium — but only when the outer image is a scene.** `annie2`
   is a photograph *of* a watercolour and is filed `photograph`, with `annie2_cropped` serving as
   the clean watercolour sample. Same rule `tv` needs for its CRT and any poster, phone screen or
   television in frame.

   **Qualified session 15.** `annie2` earns that ruling by being a *photograph of something*: a
   hand, a convention hall, an environment, a scene that exists in its own right. `april_comic` is
   not — it is a flat-on capture of a drawn comic cover filling the frame, contributing no scene,
   only vignetting and uneven exposure. It is filed `drawing / marker`. So the rule is:

   > **Report the outer medium when the outer image is itself a scene. When the outer layer is
   > pure capture of a flat artwork, report the artwork's medium.**

   The user's reason is the one that generalises, and it is the same instinct as the `digital`
   asymmetry under `[[SUB_MEDIUM]]`: *what we care about is the source of the art depicted.* A
   describer that answers `photograph` for a photographed drawing has told the downstream graph
   nothing it can use.

   **Extended session 15 to composites — layers side by side rather than nested.** `april_fanart`
   is a marker drawing of the figure laid over a separately-sourced manhole cover on a digital
   white ground; the layers were made by different means and none of them frames the others. The
   ruling:

   > **In a composite, classify by the subject** — the layer the image is *of*. Background plates,
   > cut-out grounds and pasted-in elements do not vote.

   This is the corpus's only acknowledged composite, and it is the reason `april_fanart` was
   corrected from `painting / digital` to `drawing / marker`. Note the failure mode it creates: a
   describer that averages the layers will land on `digital`, because a composite's *assembly* is
   always digital even when nothing in it was drawn digitally. That is the `digital` over-attractor
   arriving by a new route.
3. **Flat beats dimensional on `[[IDIOM]]`.** `anime` and `western toon` are for flat,
   outline-bounded, non-dimensional rendering. `dimensional toon` is for caricatured forms carrying
   real dimension and material. This is what keeps `shrek_cg` off `western toon` and
   `peter_griffin_toon` off `dimensional toon`.
4. **Judge on presentation, not provenance — on every axis.** Grain, a graded palette, shaped
   cinematic lighting and aspect bars point to `live-action film`; a clean, evenly lit, ungraded
   camera image is `photograph`. The same rule governs `digital` on `[[SUB_MEDIUM]]` and the
   `[[IDIOM]]` call. Where presentation genuinely cannot settle `[[MEDIUM]]`, the image is flagged
   `amb` and `[[MEDIUM]]` is not scored — see "The `amb` images".
5. **Visible drawing process beats flat colour.** Flat colour alone does not make an image
   animation artwork. Where construction lines, unclosed contours or stroke-to-stroke weight
   variation are still on the surface, the medium is `drawing`, however flat the colour under it
   and however strongly the character design reads as anime or cartoon. Added session 10; it is
   what finally moved `car_interior_sketch` off `2D cel`, which the axis split alone did not do.

### Adding a term the corpus cannot exercise

Settled session 10, because that session both dropped `painting / gouache` for having no sample
and added four terms that have none either. The rule that reconciles those:

> **Add an untestable term when the discrimination is coarse and unmistakable. Drop it when the
> discrimination is fine and confusable.**

`clay` vs `figure`, and `screentone` vs `ink`, are unmistakable on sight — a term we cannot test is
still one a model can apply correctly, and these are common real-world inputs once this reaches
ComfyUI.

> **This claim has now been wrong twice, in the same direction, and that is the pattern to
> remember.** It originally read "`clay` vs `puppet` vs `figure`". Session 15 disproved the `clay`
> half — the describer inverted `gromit` and `pjs`, and the term turned out never to have had a
> definition at all. Session 17 disproved the `puppet`/`figure` half by merging them: they were not
> distinguishable in practice either. **Both times, "unmistakable on sight" was asserted about a
> term nobody had yet written a visual tell for.** The rule above survives, but it needs a
> precondition: a discrimination is only "coarse and unmistakable" once you can *state the tell*.
> If you cannot write it down, you do not know that it is coarse — you know that it feels obvious,
> which is [[L-UNDEFINED-TERMS-READ-AS-OBVIOUS]].

> **Session 15 partly disproved the `clay` half of that.** Once samples arrived, the describer
> inverted `gromit` and `pjs`, and the user misread `pjs` too. The discrimination is real but it
> is **not** available on sight from the material — it runs on deformation evidence, which had to
> be written into the `clay` definition before the term was usable. The rule above survives, with
> a caveat it should have carried from the start: *"unmistakable on sight"* is a claim about a
> **stated tell**, not about a term that merely feels obvious. See
> `L-UNDEFINED-TERMS-READ-AS-OBVIOUS`. `gouache` vs `watercolour` is not: it is a fine call between similar-looking
media, so an untestable term there is an invitation to guess. `drawing / ink` has no sample either
and is kept for the same reason `screentone` is.

### Why the rebuild happened — the session-9 finding

Kept because it is the evidence for the design, and because it is the cleanest example the project
has of a *vocabulary* defect masquerading as a *prompt* defect.

`L-ONE-AXIS-PER-VOCABULARY` was applied to the coarse list in session 8 and never to the sub-lists.
The full-corpus sweep made the cost measurable: **`drawing` was emitted once in 100 images**,
against five true `drawing` files, and every one of the four misses is explained by the sub-term
rather than the coarse term.

| image | idiom the model saw | the only coarse term that owned it | what it emitted |
|---|---|---|---|
| `car_interior_sketch` | anime | `2D cel` | `2D cel / anime` |
| `marker`, `supergirl1` | digital | `painting` | `painting / digital` |
| `annie1` | watercolour | `painting` | `painting / watercolour` |

The model was not failing to see a drawing. **It saw the idiom correctly, and the vocabulary gave
it nowhere to put that idiom except under a different coarse term** — the sub-term dragged the
coarse term with it. The same coupling explains `painting / digital` being a sink at 10 emitted
against 7 true: `digital` was the only place a digitally-made image could go, so everything digital
landed in `painting`.

The old sub-lists mixed at least five axes:

| old sub-list | what it mixed |
|---|---|
| `2D cel` — anime · western toon · flat illustration | idiom / tradition |
| `drawing` — marker · sketch · ink | instrument vs degree of finish |
| `painting` — oil · watercolour · gouache · digital | medium vs substrate |
| `photograph` — colour · archival | property vs era |
| `live-action film` — modern · vintage Technicolor | era vs a specific process |
| `3D CG` — product render · character render · feature animation | purpose / what is depicted |
| `print` — engraving · technical plate | process vs purpose |

### What session 10 changed, and what it gave up

| old | new | why |
|---|---|---|
| `2D cel / anime`, `/ western toon`, `/ flat illustration` | `[[IDIOM]]` values | tradition, not instrument |
| `3D CG / product render`, `/ character render` | `[[IDIOM]] realist` / `anime` | purpose was a fourth axis |
| `3D CG / feature animation` | `[[IDIOM]] dimensional toon` | production tier renamed onto the tradition axis |
| `photograph / colour`, `/ archival` | `[[TREATMENT]] colour` / `monochrome` | era and colour, not instrument; `archival` itself was then dropped after the first sweep |
| `live-action film / modern`, `/ vintage Technicolor` | `[[TREATMENT]] colour` (both) | same; `vintage Technicolor` survived the rebuild as a treatment term and was then **dropped entirely in session 20** |
| `print / technical plate` | `print / halftone` | purpose replaced by process |
| `painting / gouache` | **dropped** | no sample and a fine, confusable call |
| `drawing / sketch` | **dropped** | degree of finish; `[[EXECUTION]]` prose already covers it |
| — | `2D cel / traditional cel` · `digital` | closes the `ivy_toon`/`peter_griffin_toon` gap — **both removed session 17; `2D cel` now has no sub-list** |
| — | `comic / ink` · `screentone` · `digital` | `annie3` and `comic` were undifferentiated before |
| — | `stop-motion / clay` · `puppet` · `figure` · `model` | real-use coverage — **`puppet` merged into `figure` session 17** |
| — | `drawing / pencil` | absorbs what `sketch` was doing for `car_interior_sketch` |

**Deliberately given up: `supergirl1` vs `supergirl2` as a scorable pair.** They differ in *finish*,
not instrument — session 9 established that — and finish is not one of the three axes. Both are now
`drawing / marker`, agreeing on all four classification fields and differing only in
`[[EXECUTION]]` prose, which is unscored. That is the honest reading of the pair rather than a
distinction the vocabulary was inventing.

**Deliberately given up: a 2D-theatrical-feature versus 2D-TV-cartoon distinction.** `feature
animation` would have carried it, but it names a production tier rather than a tradition, and for
every image the corpus actually holds `[[MEDIUM]]` already separates the cases (`shrek_cg` is
`3D CG`, `peter_griffin_toon` is `2D cel`).

**Revisited and closed in session 15**, on the terms this paragraph set: three 2D theatrical
features entered the corpus (`beauty_beast`, `pocahontas`, `fern_gully`) and the user ruled that
`2D cel` is sufficient — *"I'm ok with conflating TV vs Cinema here."* So the distinction is
given up permanently rather than pending a sample. The three sit alongside `ivy_toon`, a 90s TV
cartoon, under `2D cel / … / western toon`, and that collapse is intended. **Do not reopen this
because a describer fails to distinguish them — it is not being asked to.**

**Session 17 went one step further in the same direction**, and it is worth seeing as the same
decision twice: having conflated TV with cinema, we then conflated *cel with digital production*
by emptying `2D cel`'s sub-list. Both times the reasoning was that the era/production distinction
is not what the downstream graph needs, and both times the measured recall said we could not
deliver it anyway.

### Contested rulings that expire here

Per `.claude/CLAUDE.md`, `CONTESTED` is provisional and expires when the vocabulary that caused it
changes. These re-enter scoring in session 10 and must not stay excluded:

- **`car_interior_sketch`** — now expressible as `drawing` + `anime`.
- **`supergirl2`** — resolved by dropping `sketch`; it is `drawing / marker` like its pair.
- **`kasia`** — the anime-vs-western-toon question moves to `[[IDIOM]]`, which is where it belongs.
  It may well still be contested, but now on the right axis.

`UNSCORABLE` rulings do **not** expire — the pixels will not change. `chair`, `car_1` and `car_2`
stay `amb`. **But session 17 changed what `amb` *does*:** the flag now emits an accept-set rather
than an exclusion, so those three score again. That is not the ruling expiring; it is a different
verdict about the same permanent ambiguity. See "The `amb` images" below.

### Rulings that may need revisiting

Session-15 calls the user made **knowing they might not survive contact with a test round**. They
are recorded here so that a later reversal is a planned outcome rather than a rediscovery. None of
these is `CONTESTED` today — they are live, scored answers.

- **`avatar_1`, `avatar_2`, `boondocks`, `titans1` → `[[IDIOM]] western toon`.** All four are
  western TV animation drawn in an explicitly anime idiom. The user's reasoning is that the two
  traditions are genuinely converging in the real world, so the honest move is to try to
  discriminate and see what happens: *"If they fail consistently maybe we reverse that decision and
  reclassify or state they are contested."* **Reversal condition:** consistent failure across
  rounds, not a single bad round — `western toon` is a documented high-variance term.
- **`april_1987_figure` → `stop-motion / figure`.** See tie-break 1. It is the only sample of
  `figure`, and it is the least typical thing that term will ever have to cover. If it fails while
  the rest of `stop-motion` holds, the fault is this file, not the sub-term.
- **`scooby` → `2D cel / digital`.** Sits between `2D cel` and `vector`: uniform outlines and flat
  fills, but gradient shading on the background. The user leaned `2D cel`; a `vector` answer is not
  unreasonable.

- **`car_interior_toon` → `[[IDIOM]] western toon`, and it is now a strict CONTROL.** Ruled
  session 16 after it answered `dimensional toon` in one round and `anime` in the next — wrong in
  two directions on one axis. The user's ruling: *"another case of styles converging, but solidly
  on the western side of it."* That combination is what makes it valuable. It is **itself** a
  convergence image, so it tests the western/anime call under the conditions that make the call
  hard, which an easy control cannot — unlike `ivy_toon` and `april_1987`, whose westernness is
  never in doubt. It is named in the `control` list of all four `avatar`-family accept-sets.

**These four anime-idiom cases are also the motivating example for a harness feature we do not
have** — see "Multiple acceptable answers" below. *(Session 16: we have it now. The section is
kept because its reasoning is still the design rationale.)*

#### Outcome of the first round against them (s15, `runs/run-20260812-232352.txt`)

One round is not the reversal condition for any of these. Recorded so the second round has
something to compare against.

| ruling | result | note |
|---|---|---|
| `avatar_1`, `avatar_2` | **failed → `anime`** | exactly the predicted failure |
| `boondocks` | **failed → `dimensional toon`** | **not** the predicted failure. Its own look record says "the modern western animated series style" in plain text, so the anime idiom is not what cost it — the flat-shading confusion above is. The reversal condition was written for the wrong failure mode |
| `titans1` | **passed** | |
| `scooby` | **passed** | the `2D cel` vs `vector` worry did not materialise |
| `april_1987_figure` | **now `CONTESTED`** — see below | the user conceded the model's `photograph` reading |

**The most damaging single result is not in this table.** `april_1987` — cited two paragraphs below
as an image on which `western toon` is *unambiguous*, and used as the strict control for the whole
accept-set argument — was also classified `anime`, despite a look record explicitly naming 1980s
television cel animation. The user's ruling: *"Definitely no, it's a very western style."* **The
discrimination this vocabulary asks for is not currently working even where we were confident it
was**, which is a stronger finding than any of the provisional cases.

### Contested from session 15 — RESOLVED session 17

Both were cases where the vocabulary **has no legal way to state the true answer** — not model
defects, and not image ambiguity:

- **`april_1987_figure`** — the model answered `photograph / none`. The user: *"I can't argue with
  it, it's a `photograph` of a `figure`, which is an invalid pairing."* `figure` is a sub-term of
  `stop-motion`; `photograph` takes `none`. Both halves of the truth are sayable, but not together.
- **`april_comic`** — the model answered `comic / digital` against an expected `drawing / marker`.
  Notably it *did* look through the photograph as tie-break 2 now requires; it then had to choose
  between the artwork's instrument and its publication form. The user: *"a marker drawing as a
  comic cover… again two things at once."*

**Session 17 ruled both, per the user: *"both images' alternatives should be acceptable for each of
them."*** They are now **pairs of per-field accept-sets** rather than exclusions:

| | `[[MEDIUM]]` | `[[SUB_MEDIUM]]` |
|---|---|---|
| `april_1987_figure` | `stop-motion \| photograph` | `figure \| none` |
| `april_comic` | `drawing \| comic` | **`marker`, strict** |

Two things about that table are load-bearing.

**Session 16 ruled this shape — "two fields each holding half a true answer" — out of accept-set
scope, and session 17 did not overturn that; it accepted the known limitation instead.** Because
sets are per-field, the cross terms `stop-motion / none` and `photograph / figure` also pass, and
the second is the very pairing the user called invalid. That is the same limitation already
accepted on `annie2_cropped` and `april_fanart`, and it was taken deliberately rather than adding
cross-field constraints to `score.py`.

**`april_comic`'s `[[SUB_MEDIUM]]` stays strict at `marker` on purpose.** Opening it would forgive
`digital` on a marker drawing — the project's largest single defect, and the exact direction the
user ruled unacceptable in session 12 (*"`marker` → `digital` is not so much"*). This mirrors
`april_fanart`, which likewise has an open `[[MEDIUM]]` and a strict instrument. **An accept-set
must never be drawn loosely enough to absorb a real defect**, and this is where that rule bites.

**Control gap, recorded rather than papered over:** `tests/describer_style_added_s15.json` contains
no unambiguous `drawing` case, and `drawing` is the side `april_comic`'s set can erode. Only the
reverse direction is guarded (`gordon_comic`). Fix that by adding an unambiguous drawing to the
file, not by loosening the set.

### Session 17 — the vocabulary merges

Two sub-term merges, both ratified by the user **on their merits rather than on a score**. That
framing is the important part and it changed how the session was run: *"the judgements as to the
new shape of the output and definition changes we are adopting I feel are valid and should be
respected anyway… I'm ok with this setting a new baseline."* So neither merge is on trial. If the
numbers get worse we work from the result as the new base.

| | before | after |
|---|---|---|
| `stop-motion` | `clay` · `puppet` · `figure` · `model` | `clay` · **`figure`** · `model` |
| `2D cel` | `traditional cel` · `digital` | **(no sub-terms — `none`)** |

**`puppet` → `figure`.** Agreed session 12, executed here. The two were not distinguishable in
practice: `coraline1` was ruled `CONTESTED` on exactly this, and a round emitted `figure` where the
table said `puppet` with the record supporting either. `figure` survives as the more general term —
it covers a sculpted film puppet, an articulated plastic toy and a rigid set-clay sculpt alike, and
the merged term has one statable test (*fabricated and rigid*) where the split pair had none.

**`2D cel` emptied.** `traditional cel` scored **2/7, with all five losses going to `digital`**, and
the user ruled the era distinction not worth teaching. Two things made `none` the right shape rather
than "merge `traditional cel` into `digital`":

- A one-value sub-list is not a vocabulary. The field would carry no information and would be
  correct 100% of the time by construction, which inflates a score while measuring nothing.
- More importantly, it would make every `2D cel` record **assert digital production** downstream —
  including for `april_1987` and `pocahontas`, which are hand-drawn cel animation. The record goes
  to the composer and then to H3; a false claim there is worse than silence. `none` asserts nothing.

**What this costs, stated plainly.** It kills the corpus's tightest era probe (`gordon-era`, 90s cel
vs 2000s digital), narrows the `gordon` and `april` ladders by a rung, and rewrites 25 master rows
and both test files. Git holds the history and these rows record the reasoning, but a later reversal
is a real re-derivation, not a revert. Accepted deliberately.

**And it splits the measurement history.** Every archived `describer_style` round before Round 1 of
this session is scored against a vocabulary that no longer exists — those runs stay valid as
*history*, but cross-boundary score comparison is gone. Same trade as a server-config change, taken
knowingly. `reference/baselines/describer_style_sweep_frozen.txt` and its s15 counterpart are the
comparison points from here on.

### Session 17 — every outstanding ruling cleared, and what that exposed

Session 17 put **all seven** remaining `CONTESTED` / `UNSCORABLE` cases to the user before touching
the vocabulary, on the timing rule that a ruling made *after* a prompt change is tuning the answer
key to the prompt's behaviour. Both test files now have **zero exclusions**: every one of the 130
images scores.

`april_1987_figure`, `april_comic` and the three `amb` files are covered in their own sections
above. The remaining three are the interesting ones, because they turned out not to be three cases.

#### The `flat graphic` over-attractor — three exclusions that were one defect

| case | master | v3 answered | had been contested because |
|---|---|---|---|
| `fish_pixel` | `realist` | `flat graphic` | a shaded but heavily simplified sprite on a flat ground |
| `lincoln_money` | `realist` | `flat graphic` | flat guilloche border and ground dominate the frame |
| `mountain_rain` | `realist` | `flat graphic` | painterly and dimensional, but posterised into flat bands |

**All three are the same miss in the same direction**, and `kasia_bag` and `destroyer_drawing` are
already-scored misses of exactly that shape — five cases, split across three exclusions and two
anonymous misses, which is precisely the accumulation effect `.claude/CLAUDE.md` warns about. Each
one individually looked like image ambiguity; together they are a term over-attracting on images
that have a flat or banded *ground* behind a *modelled subject*.

The classifier already carries a rule aimed at this — "JUDGE `[[IDIOM]]` ON THE SUBJECT, NOT THE
GROUND BEHIND IT", and `[[IDIOM]]`'s own definition says *"anything that renders its subject the way
it actually looks is `realist`, however few colours it uses and however little detail it carries."*
So this is an **unfollowed** rule, not a missing one — the same shape as the `digital` problem, on a
different axis.

All three were cleared to the master value and now score as ordinary misses. **Deliberately not
fixed in session 17**: it is a third defect on a third axis, and folding it into the round that
measures `[[SUB_MEDIUM]]` would have made the result unreadable. It is on `.claude/TODO.md` as a
named open defect rather than as three ambiguities.

> **The general lesson, which cost three separate rulings to see:** a `CONTESTED` pile is evidence
> about the vocabulary, not a tidy-up queue. Cases excluded one at a time never get compared with
> each other, so a shared failure direction stays invisible for as long as the exclusions stand.

### Multiple acceptable answers — a gap in the scoring mechanics

Raised by the user in session 15, and worth building before the next vocabulary round. The scoring
harness has exactly two states for a hard case: score it against one right answer, or exclude it
(`CONTESTED` / `UNSCORABLE`). Both are wrong for the anime-idiom western cartoons.

- Scoring one answer punishes a defensible reading.
- Excluding them throws away real signal, **and it throws away too much**: on `avatar_1`, either
  `western toon` *or* `anime` is defensible, but `stop-motion` is flatly wrong and should still
  fail. Exclusion cannot express that.

What is wanted is an `_expected` entry that accepts a **set** of answers on one field while leaving
every other value wrong. Note this is a per-image property, not a property of the terms: the same
`western toon` / `anime` pair that is ambiguous on `avatar_1` is **not** ambiguous on `ivy_toon` or
`april_1987`, which are simply `western toon`. So it cannot be implemented as a vocabulary-level
alias. Tracked on `.claude/TODO.md`.

### What session 15 added

30 files, collected against named gaps rather than opportunistically. What they close:

| gap | before | after |
|---|---|---|
| `stop-motion / clay` | **no sample** | `gromit`, `gumby` |
| `stop-motion / figure` | **no sample** | `april_1987_figure` (and see the caveat above) |
| `stop-motion / puppet` | 2, both Coraline | 4, spanning silicone, flocked felt and foam — **term merged into `figure` session 17**, so these count toward `figure` now |
| `2D cel / traditional cel` | **1** (`ivy_toon`) | 7 — **term removed session 17**; all 25 `2D cel` files now take `none`. The enrichment is what made the 2/7 recall measurable, which is what got the term dropped |
| `western toon` at realistic proportions | the session-12 corpus gap | ~9 realistic-proportion samples; the idiom goes 8 → 25 |
| a photographic, signage-free day/night set | standing gap 1 | `shed_day` / `shed_dusk` / `shed_night` |
| `infant`, `middle-aged`, `older adult` age brackets | untested | `baby_middle_aged`, `maggie_grandpa_cat`, `gordon_*`, `pjs` |
| darker skin tones | near-absent, unremarked until session 15 | `boondocks`, `pjs`, `nadia`, `titans*`, `pocahontas`, `molly`, `avatar_2` |

Live-action drops 47% → **39%**, and `dimensional toon` doubles (5 → 11).

**What this batch is not:** it is **not a representative sample of the corpus**, and that has a
direct consequence for scoring. It is heavily `2D cel` and `western toon` by construction, so a
high failure rate on these 30 alone carries no information about the corpus as a whole — the
`enriched` gate in `.claude/CLAUDE.md` applies, not the level-based one. Appending them to
`tests/describer_style_sweep.json` would change both `N` and the medium mix, invalidating
comparison against the 100-image baseline. See `.claude/TODO.md` for the agreed sequencing.

### What session 18 added

57 files, collected against the gaps named in `SIDE_HANDOFF_images_2.md` plus the user task
carried over from session 17. What they close:

| gap | before | after |
|---|---|---|
| **figureless anime / cartoon frames** | **none** — the blocker named in `HANDOFF_session17.md` | 14, spanning shaded and flat, anime and western toon, interior and exterior |
| a **same-scene figure vs no-figure** control | none | `grass_anime_scenery` / `grass_anime_girl` — one shot, characters added |
| `drawing / pencil` | **no sample** (standing gap 4) | **5** — two paired with their source photograph |
| `print / halftone` in colour | 1, monochrome (`destroyer_drawing`) | 2 — `misato_car_technical_print` is the colour sample |
| `stop-motion / figure` typicality | 5, the s15 note calling its first sample atypical | **9**, and `laika` is a textbook member |
| `toddler`, `pre-teen` age brackets | **untested** (both) | `toddler` ×3 · `pre-teen` ×15 (4 new + the 11-file mathilda set) |
| `older adult` | 3 | 4, and `wayne-age` makes it an age-progression pair with a real person |
| an object medium-ladder | none — `april` is a character, `destroyer` only two rungs | **misato-car**, one vehicle across four media |
| same-pose photo→rendering sets | 1 (`girl-painting`) | **6** — `ghibli-ref`, `saber-ref`, `uniform-ref`, `blonde-ref`, `woman-ref`, `fruit-ref` |
| a no-person medium pair | 1 (`destroyer`) | 2 — `fruit-ref`, and in colour on one side |
| darker skin tones | covered s15 | extended: `cleo_slingshot`, `sam_jackson_jurassic_middle_aged` |

**What this batch is not.** As with session 15 it is **not a representative sample** — it is
stocked against named gaps and is heavily `2D cel` and `anime` by construction. The `enriched`
gate applies to `tests/describer_style_added_s18.json`, not the level-based one, and the full
sweep must **not** be regenerated over it without a deliberate re-baseline
(`L-DONT-REGENERATE-A-BASELINED-TEST`).

#### The figureless-plate accept-set

Ten of the new plates have **no figure and no cel line work**, and on those `[[MEDIUM]]` rests on
provenance rather than pixels: a cel-era background *is* a painting, so `2D cel` and `painting`
are both defensible. The user's ruling (session 18) is an **accept-set `2D cel | painting`**, on
the same grounds as `car`/`chair` — *"if the eye can't differentiate, then we're judging on
provenance, not pixels."*

Three constraints came with it, and each one narrows the set deliberately:

- **It applies only where line work is genuinely absent.** Plates with visible outlines
  (`backyard_anime`, `garden_pond_anime`, `pavilion_anime`, `classroom_anime_empty`,
  `shoes_anime`, `simpsons_couch_toon`, `spongebob_tree_toon`) stay **strict `2D cel`** — the eye
  can tell, so the set would be forgiving a real answer.
- **The `ghibli-ref` pair is exempt, both sides strict.** That pair exists to test cel-gouache
  against digital painting, and an accept-set covering its source half would let a model answer
  `painting` for both, collapse the discrimination, and still score two passes.
- **`grass_anime_girl` is the named control** for `grass_anime_scenery`: the same background with
  characters added, which must still come back `2D cel`.

**It is NOT expressed with the `amb` flag.** The user's direction is to **stop using `amb`
altogether** and let `_expected` carry these rulings, revisiting the flag only if something turns
out genuinely ambiguous. The mechanism is `ACCEPT_MEDIUM` in `scripts/gen_style_sweep.py`,
parallel to the existing `ACCEPT_SUB`. Migrating the three legacy `amb` files off the flag is
recorded as follow-up work, not done here.

#### `[[IDIOM]]` on a figureless frame — recorded strict, on purpose

Every figureless plate carries its true idiom (`anime` or `western toon`), **not** an accept-set
spanning `flat graphic`. v4c's tie-break reaches the idiom through body proportion and then eye
construction, and a frame with no figure offers neither — so the prompt currently has **no path**
to the right answer on these. That is a prompt defect to measure, not something to encode into
the answer key.

`simpsons_couch_toon` is the sharpest instance and the mirror of the three v4c regressions
(`forest_day`, `forest_night`, `sanfran_night`, all `flat graphic → western toon`): those were
figureless scenes wrongly pulled *to* `western toon`, and this is a flat figureless scene where
`western toon` is correct. The accept-set `HANDOFF_session17.md` predicted was therefore **not**
written — the corpus now holds the image to revisit it with if a round shows the model splitting.

---

---

## Age vocabulary — the `age` column

Added session 19. Until then age lived as free prose in `people` and **nothing checked it**,
which is how the eleven-file mathilda set ended up with a bracket on exactly one member
(`window`) that disagreed with the other ten. `[[MEDIUM]]`, `[[IDIOM]]` and `[[TREATMENT]]` are
closed vocabularies `inventory.py` enforces; age now is too.

### The tokens

The nine brackets, spelled **exactly** as `prompts/describer_character.txt` spells them —
`infant`, `toddler`, `child`, `pre-teen`, `teenager`, `young adult`, `adult`, `middle-aged`,
`older adult` — plus three non-bracket tokens:

| token | means |
|---|---|
| `n/d` | a **human** figure is present but the depiction does not determine an age — a 20px face in a wide shot (`forest_autumn`, `p5_first`), a figure turned away (`room_anime`), a body part only (`boondocks`'s partly-visible adult) |
| `n/a` | figures are present but **none is human**: animals (`pooh`, `bird_vector`), and humanoids that carry no human age at all (`gumby`'s clay slab, `lego1`, `skellington`, `woody_cg`) |
| `crowd` | an un-individuated mass. Recorded **alongside** any bracket that is legible: `stage` is `young adult, crowd`, `ghibli_street` is `child, adult, crowd` |
| `—` | no figure of any kind |

**`—` and `n/a` are not interchangeable.** `—` says the frame is empty of figures; `n/a` says it
holds figures the age axis does not reach. Collapse them and `pooh` becomes indistinguishable
from `cannon`.

### Four rules that keep it honest

1. **The vocabulary is IMPORTED, not copied.** `inventory.py` does `from validate import
   AGE_PERSON`, which is the same list `validate.py` enforces on describer output, which is the
   list the prompt states. Change the prompt's brackets and the answer key follows automatically
   — no hand-sync of the kind the `VOCAB` ↔ `MEDIUM_VOCAB` note still warns about.
2. **It is a multiset, not an ordered list.** The cell claims *these brackets appear*, not which
   figure is which. Order-matching two free-text columns is unenforceable, and the per-subject
   claim a character test needs gets built from a `SUBJECT` line instead.
3. **`age` and `people` must agree about whether a figure is present**, in both directions. This
   is the check that would have caught the mathilda set.
4. **Age is a judgement about the DEPICTION, not the person.** `saber_reference_photo` is
   `young adult`; `saber_reference_anime`, drawn from it, is `teenager`. Both are correct, and
   the saber triplet is **not** an age-consistency set.

### Deliberate exclusions

**Animals get no bracket.** `describer_character` gives them a different four-term list
(`young`/`adult`/`old`/`not visible`) whose `adult` would collide with the human bracket inside
the same cell. `people` already records them; the age axis stays human-only.

### The boundary cases already ruled

- **The five-file Léon set** (`p1_first`, `p1_last`, `p4_first`, `p4_last`, `door_last`) is one
  man, recorded `adult`. He is **canonically 45–46**, i.e. a hair over the 44/45 line, and reads
  mid-40s. `adult` was chosen as the better default; it is a boundary call, not a confident one,
  and re-opening it costs five rows at once — the mathilda failure shape exactly.
- **`kiki`** is `pre-teen` and uncertain; the round face reads younger than the canonical 13.
- **`p5_first`/`p5_last`** are `n/d`. Same source film as the Léon set, but the figure is a
  different, distant man whose face is ~20px.

## Master table — classification

| image | medium | sub | idiom | treatment | detail | int/ext | people | age | sets | added | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `airliner_gargantuan` | photograph | none | realist | colour | narrow-body airliner in an all-over red livery on an apron; ground vehicles and a terminal block behind | ext | 2 adults (distant, on the apron) | n/d | scale-ladder | s24 | text |
| `annie1` | drawing | ink | anime | colour | ink and marker, digital | none | **2 distinct characters**: a girl (full figure) + a masked male hero (head and shoulders) | teenager | annie | s7a | text, franchise, corr |
| `annie2` | photograph | none | realist | colour | + ink, photographed in a hand | **nested** — int (photo) / none (drawing) | 1 girl (drawn) + 1 hand (real) | teenager, n/d | annie | s7a | franchise, nested |
| `annie2_cropped` | painting | watercolour | western toon | colour | clean page, hand and hall removed | none | 1 girl (drawn) | teenager | annie | s7a-crop | franchise, derived |
| `annie3` | comic | digital | western toon | colour | 4 panels | ext | **3 distinct**: 1 girl, 2 costumed heroes (a boy, a woman) | teenager, young adult | annie | s7a | text, franchise, corr |
| `annie3_panel1` | comic | digital | western toon | colour | leftmost panel | ext | 1 girl + 2 costumed heroes | teenager, young adult | annie | s7a-crop | text, franchise, derived |
| `april_1987` | 2D cel | none | western toon | colour | 80s TV cel, VHS-grade | ext | 1 young adult woman + 1 humanoid turtle | young adult | april | s15 | franchise |
| `april_1987_figure` | stop-motion | figure | dimensional toon | colour | **a photograph of moulded plastic figures on a shelf**, not an animation frame — classified by the objects, see tie-break 1 | int | 5 figures (1 woman, 4 humanoid turtles) + 1 rat figure behind | n/a | april | s15 | text, franchise |
| `april_comic` | drawing | marker | western toon | colour | original marker art on a blank sketch cover, photographed — **classified by the art, not the capture**, see tie-break 2 | none | 1 young adult woman | young adult | april | s15 | text, franchise |
| `april_fanart` | drawing | marker | realist | colour | **a composite**: a marker drawing of the figure laid over a separately-sourced manhole cover, on a digital white ground — classified by the figure, which is the subject. Corrected s15, see corrections | none | 1 young adult woman | young adult | april | s15 | franchise |
| `avatar_1` | 2D cel | none | western toon | colour | western TV series drawn in an anime idiom — **provisional**, see the convergence note | ext | 2 children | child | avatar, anime-toon | s15 | franchise |
| `avatar_2` | 2D cel | none | western toon | colour | as `avatar_1`; night camp. A foreground pole crosses the lower frame | ext | 5 children and teenagers | child, teenager | avatar, anime-toon | s15 | franchise |
| `ayanami_oil` | painting | digital | anime | colour | **digital**, oil/gouache idiom | int | 1 girl, blue hair, red eyes | teenager | oil-idiom | s7b | franchise |
| `azumanga_anime` | 2D cel | none | anime | colour | flat cel, thick outline, sticker border; **naturalistic head-to-body ratio, large irises with a specular glint, iris distinct from pupil** | none | 3 schoolgirls, **two shared with `azumanga_toon`** | teenager | azumanga | s7a | franchise, corr |
| `azumanga_toon` | 2D cel | none | western toon | colour | flat toon over textured paint; **heavily disproportionate bodies -- noodle limbs, oversized heads, hands and feet -- small flat black pupils with no iris, and a stylised non-realistic background** | ext | 3 schoolgirls, **two shared with `azumanga_anime`; the third differs** | teenager | azumanga | s7a | franchise, corr |
| `baby_middle_aged` | photograph | none | realist | colour | — | int | 1 middle-aged man + 1 infant | infant, middle-aged | age-family | s15 | — |
| `backyard_anime` | 2D cel | none | anime | colour | cel-era TV BG, 4:3, VHS-grade; hard-edged boulders over airbrushed lawn, day | ext | none | — | garden-daynight | s18 | — |
| `beauty_beast` | 2D cel | none | western toon | colour | **2D theatrical feature** — deliberately not distinguished from TV cel | ext | 1 young adult woman + 1 beast | young adult | feature-2d | s15 | text, franchise |
| `bird_vector` | vector | none | flat graphic | colour | — | none | 1 bird (no people) | n/a | bird | s7a | — |
| `bird_watercolor` | painting | watercolour | realist | colour | on textured paper | none | 1 bird (no people) | n/a | bird | s7a | — |
| `blonde_reference_painterly` | painting | digital | realist | colour | flat hard-edged shapes, limited palette, brush grain in hair and cloth | int | 1 young adult woman | young adult | blonde-ref | s18 | — |
| `blonde_reference_photo` | photograph | none | realist | colour | **the source**; studio fashion shot on a pale green sweep | int | 1 young adult woman | young adult | blonde-ref | s18 | text, real |
| `boo_toddler` | 3D CG | none | dimensional toon | colour | feature CG; oversized head and eyes on a real-material body | int | 1 toddler girl | toddler | age-bracket | s18 | franchise |
| `bookshop` | photograph | none | realist | colour | — | **ext (int visible)** | 1 adult man | adult | setting-boundary | s6 | — |
| `boondocks` | 2D cel | none | western toon | colour | western TV series drawn in an anime idiom — **provisional** | int | 2 children + 1 partly visible adult | child, n/d | anime-toon | s15 | franchise |
| `bumper_car_medium` | photograph | none | realist | colour | fairground bumper car driven at speed on an airfield apron; a frame from an online video | ext | 1 adult man | adult | scale-ladder | s24 | text, real |
| `cannon` | photograph | none | realist | colour | — | ext | none | — | — | s7a | — |
| `captain` | photograph | none | realist | colour | — | ext | 1 adult man | adult | — | s6 | — |
| `car_1` | photograph | none | realist | colour | user: automaker press shot. Photo vs render **not visually determinable** | none | none | — | car-angle | s7b | text |
| `car_2` | photograph | none | realist | colour | as `car_1` | none | none | — | car-angle | s7b | text |
| `car_building_gargantuan` | photograph | none | realist | colour | red gullwing coupe on a gravel drive before a baroque palace. **AI-generated but reads photographic — medium not visually determinable**, the same shape as `car_1`/`car_2` | ext | none | — | scale-ladder | s24 | — |
| `car_interior_mecha_driver` | 2D cel | none | anime | colour | painted, desaturated green-grey | **int (vehicle)** | 1 teenage girl + 1 humanoid robot | teenager | car-interior | s7a | text, franchise |
| `car_interior_photo` | photograph | none | realist | colour | press/product shot | **int (vehicle)** | none | — | car-interior | s7a | text |
| `car_interior_sketch` | drawing | digital | anime | colour | digital, construction lines visible | **int (vehicle)** | 2 young women | young adult | car-interior | s7a | — |
| `car_interior_toon` | 2D cel | none | western toon | colour | night, driver's seat | **int (vehicle)** | 1 adult woman | adult | car-interior | s15 | franchise |
| `car_mountain_colossal` | photograph | none | realist | colour | red sports coupe on a wet mountain road, snow-covered peak behind. **AI-generated but reads photographic — medium not visually determinable**, the same shape as `car_1`/`car_2` | ext | none | — | scale-ladder | s24 | — |
| `castle` | photograph | none | realist | colour | — | ext | 1 young adult woman | young adult | — | s6 | — |
| `chair` | photograph | none | realist | colour | user: Amazon listing. Photo vs render **not visually determinable** | none | none | — | — | s7a | — |
| `chips_hotdog_dr_pepper_painting` | painting | oil | realist | colour | traditional, alla prima | int-ish | none | — | — | s7a | text |
| `city_day` | photograph | none | realist | colour | — | ext | none | — | city-daynight | s6 | text |
| `city_night` | photograph | none | realist | colour | blue hour | ext | none | — | city-daynight | s6 | text |
| `classroom1` | photograph | none | realist | colour | — | int | 5 children | child | classroom | s6 | — |
| `classroom2` | photograph | none | realist | colour | — | int | 6+ children | child | classroom | s6 | — |
| `classroom_anime_empty` | 2D cel | none | anime | colour | cel BG, outlined desks; low sun through the left windows | int | none | — | classroom | s18 | text |
| `cleo_slingshot` | 2D cel | none | western toon | colour | modern flat digital toon; **darker skin tones** | ext | 1 pre-teen girl + 1 pre-teen boy | pre-teen | — | s18 | franchise |
| `cloud` | painting | digital | anime | colour | painterly, deckle border | ext | none | — | — | s6 | text |
| `comic` | comic | ink | anime | colour | 5 panels | int | 6+ children, 1 adult teacher, 1 costumed figure | teenager, adult, n/d | comic-page | s7a | text |
| `comic_panel2` | comic | ink | anime | colour | top-right panel, 335x429 | int | 1 girl (close-up) | teenager | comic-page | s7a-crop | text, derived |
| `comic_panel3` | comic | ink | anime | colour | middle panel, 1161x460 | int | 2 adults | middle-aged, n/d | comic-page | s7a-crop | text, derived |
| `comic_panel4` | comic | ink | anime | colour | bottom panel, 1249x904 | int | 6+ children | child | comic-page, classroom | s7a-crop | derived |
| `coraline1` | stop-motion | figure | dimensional toon | colour | puppet on a **transparent** ground — reaches the model as black, see gotchas | none | 1 girl (puppet) | pre-teen | coraline | s7a | franchise, corr |
| `coraline2` | stop-motion | figure | dimensional toon | colour | film still | int | 2 puppets (girl + adult woman, button eyes) | pre-teen, adult | coraline | s7a | text, franchise |
| `couple_middle_aged` | photograph | none | realist | colour | bright high-key stock photography, blown-out window behind | int | 1 middle-aged man + 1 middle-aged woman | middle-aged | age-bracket | s18 | real |
| `destroyer_drawing` | print | halftone | realist | monochrome | halftone recognition plate, line and wash | none | none | — | destroyer | s7a | text |
| `destroyer_photo` | photograph | none | realist | monochrome | — | ext | a few tiny indistinct crew | n/d | destroyer | s7a | text |
| `door_first` | live-action film | none | realist | colour | **first frame** — door shut, corridor empty | int | **none** | — | door, first-last | s8 | text |
| `door_last` | live-action film | none | realist | colour | **last frame** — same door open, room and man revealed | int | 1 adult man | adult | door, first-last | s8 | text |
| `fern_gully` | 2D cel | none | western toon | colour | **2D theatrical feature** | ext | 6+ | child, young adult | feature-2d | s15 | franchise |
| `fish_pixel` | pixel art | none | realist | colour | flat sprite | none | none | — | — | s7a | — |
| `forest_autumn` | photograph | none | realist | colour | — | ext | **1 tiny distant figure** | n/d | — | s6 | — |
| `forest_day` | vector | none | flat graphic | colour | upper panel, 947x739 | ext | none | — | forest-daynight | s7b-crop | derived |
| `forest_day_night` | vector | none | flat graphic | colour | **composite**, 2 stacked panels | ext | none | — | forest-daynight | s7b | — |
| `forest_night` | vector | none | flat graphic | colour | lower panel, 947x738 | ext | none | — | forest-daynight | s7b-crop | derived |
| `fruit_reference_photo` | photograph | none | realist | colour | **the source**; a studio still life, raking light, no person | int | none | — | fruit-ref | s18 | — |
| `fruit_reference_sketch` | drawing | pencil | realist | monochrome | **graphite study of the same arrangement**, full tonal rendering | none | none | — | fruit-ref | s18 | — |
| `fruitbowl` | 3D CG | none | realist | colour | synthetic still life | int | none | — | — | s7a | text |
| `fuji` | photograph | none | realist | colour | — | ext | none | — | — | s6 | real |
| `garden_pond_anime` | 2D cel | none | anime | colour | **the same garden as `backyard_anime`, at night and from another viewpoint**; the stone lantern now right-foreground and lit | ext | none | — | garden-daynight | s18 | — |
| `ghibli_grass` | 2D cel | none | anime | colour | painted BG plate, no line work — takes the figureless-plate accept-set | ext | none | — | — | s18 | — |
| `ghibli_kitchen` | 2D cel | none | anime | colour | painted BG, light contour only — takes the figureless-plate accept-set | int | none | — | — | s18 | — |
| `ghibli_painting_reference_anime` | 2D cel | none | anime | colour | gouache BG plate, no line work; **STRICT — exempt from the accept-set**, it is the source half of the pair | ext | none | — | ghibli-ref | s18 | — |
| `ghibli_painting_reference_painterly` | painting | digital | realist | colour | a digital painterly study made **from** the plate opposite — same rock, hillside and cloud bank, looser brushwork | ext | none | — | ghibli-ref | s18 | text |
| `ghibli_street` | 2D cel | none | anime | colour | **cel figures over a painted street** — strict `2D cel`; period cars, a crowd | ext | ~25 assorted adults and children, none individuated | child, adult, crowd | — | s18 | text, franchise |
| `girl_painting` | painting | digital | realist | colour | oil-style, soft edges | none | 1 pre-teen girl | pre-teen | girl-painting | s7a | text |
| `girl_painting_reference` | live-action film | none | realist | colour | film still | int | 1 pre-teen girl | pre-teen | girl-painting | s7a | real |
| `gordon_1996` | 2D cel | none | western toon | colour | 90s TV cel | **int (vehicle)** | 1 older adult man | older adult | gordon, toon-era | s15 | franchise |
| `gordon_2004` | 2D cel | none | western toon | colour | digital ink and paint, angular design | ext | 1 middle-aged man | middle-aged | gordon, toon-era | s15 | franchise |
| `gordon_comic` | comic | digital | realist | colour | single panel | ext | 1 middle-aged man | middle-aged | gordon | s15 | text, franchise |
| `grass_anime_girl` | 2D cel | none | anime | colour | **the same shot as `grass_anime_scenery` with characters added**; cel figures over that plate — strict, and its partner's control | ext | 1 child + 1 small animal | child | grass-anime | s18 | — |
| `grass_anime_scenery` | 2D cel | none | anime | colour | cel-era painted plate, VHS-grade, **no line work** — takes the figureless-plate accept-set | ext | none | — | grass-anime | s18 | — |
| `gromit` | stop-motion | clay | dimensional toon | colour | plasticine, thumbprint surfaces; set and vehicle are built models, but character figures are present so `clay` wins | **int (ext visible)** | 1 man + 1 dog, both clay | adult | stopmo-sub | s15 | text, franchise |
| `gumby` | stop-motion | clay | dimensional toon | colour | classic clay, VHS-grade | int | 3 clay figures — 1 humanoid, 1 **anthropomorphised horse**, 1 in the background | n/a | stopmo-sub | s15 | franchise |
| `gwen` | 2D cel | none | western toon | colour | — | **int (vehicle)** | 2 girls | teenager | gwen | s15 | text, franchise |
| `gwen_cg` | 3D CG | none | dimensional toon | colour | low-resolution render; same character design as `gwen` | int | 1 young woman | teenager | gwen | s15 | text, franchise |
| `hermione_preteen` | live-action film | none | realist | colour | graded film still, warm key, practical candle | int | 1 pre-teen girl | pre-teen | age-bracket | s18 | text, real, franchise |
| `ivy_toon` | 2D cel | none | western toon | colour | 90s cel animation still | int | 1 young woman, red bob | young adult | toon-era | s7b | franchise |
| `jacket` | photograph | none | realist | colour | — | ext | 1 young adult woman | young adult | jacket | s6 | — |
| `jacket2` | photograph | none | realist | colour | — | ext | same woman | young adult | jacket | s6 | — |
| `kasia` | 2D cel | none | anime | colour | the original drawing; an anime-inspired toon idiom, leaning slightly western — **the sub-term is contested, the coarse term is not** | none | 1 girl | teenager | kasia | s6 | corr |
| `kasia_bag` | photograph | none | realist | colour | AI-rendered, but **classified by presentation**, which is photographic | none | none | — | kasia, bag-angle | s7a | corr |
| `kasia_bag_2` | photograph | none | realist | colour | as `kasia_bag`, second angle, re-render | none | none | — | kasia, bag-angle | s7b | corr |
| `kasia_outfit` | photograph | none | realist | colour | **flat-lay**, derived from `kasia`; AI-rendered, classified by presentation | none | none | — | kasia | s7a | corr |
| `kasia_render` | 3D CG | none | anime | colour | stylised anime character render | none | 1 girl | teenager | kasia | s7a | — |
| `kasia_swimsuit` | photograph | none | realist | colour | **flat-lay**, derived from `kasia_swimsuit_worn`; AI-rendered, classified by presentation | none | none | — | kasia | s7a | corr |
| `kasia_swimsuit_render` | 3D CG | none | anime | colour | AI render, anime idiom | ext | 1 girl (same character) | teenager | kasia | s7b | — |
| `kasia_swimsuit_worn` | 2D cel | none | anime | colour | the original commission | none | 1 girl (same character) | teenager | kasia | s7b | text |
| `kaypro_ii` | photograph | none | realist | colour | — | none | none | — | — | s7a | text |
| `kiki` | drawing | digital | anime | colour | a signed digital illustration, **not an animation still** — soft airbrushed shading, gradient blush, tapered stroke-weight in the hair. Corrected s16, see corrections | none | 1 girl + 1 black cat | pre-teen | — | s6 | franchise, corr |
| `laika` | stop-motion | figure | dimensional toon | colour | feature stop-motion; resin faces, **real knitted and woven fabric**, visible hair fibre — the term's most typical sample | int | 1 pre-teen boy + 4 figures behind | pre-teen, n/d | stopmo-sub | s18 | franchise |
| `lego1` | stop-motion | figure | dimensional toon | colour | **LEGO brickfilm**; moulded ABS, printed faces, a built facade set | ext | 5 minifigures | n/a | lego, stopmo-sub | s18 | text, franchise |
| `lego2` | stop-motion | figure | dimensional toon | colour | LEGO; a single minifigure on a brick-built street, plate studs visible | ext | 1 minifigure | n/a | lego, stopmo-sub | s18 | — |
| `lincoln_money` | print | engraving | realist | monochrome | banknote | none | a portrait *within an object* | n/a | lincoln | s7a | text, real |
| `lincoln_photo` | photograph | none | realist | monochrome | albumen portrait | none | 1 older adult man | older adult | lincoln | s7a | real |
| `maggie_grandpa_cat` | 2D cel | none | western toon | colour | flat, heavy stylisation | int | 1 older adult man + 1 infant + 1 cat | infant, older adult | age-family | s15 | text, franchise |
| `marker` | drawing | marker | anime | colour | — | int | 1 young woman | young adult | — | s7b | text |
| `misato_car_1` | 2D cel | none | anime | colour | cel car over a painted mountain-road BG, head-on, VHS-grade | ext | none | — | misato-car | s18 | franchise |
| `misato_car_2` | 2D cel | none | anime | colour | cel car over a painted tunnel-mouth BG, from behind | ext | none | — | misato-car | s18 | text, franchise |
| `misato_car_real` | photograph | none | realist | colour | the real car at a classic-car show, flash-lit, high three-quarter front | int | 2 adult men seated behind, background | n/d | misato-car | s18 | text, real |
| `misato_car_technical_print` | print | halftone | realist | colour | **four orthographic views** — side, front, top, rear — airbrushed, on white; classified as `destroyer_drawing` is | none | none | — | misato-car | s18 | text |
| `miya` | 2D cel | none | anime | colour | — | ext | 1 teenage girl | teenager | — | s6 | text, franchise |
| `miyu` | pixel art | none | anime | colour | — | none | 1 girl (heavily occluded) + 1 shadow figure | n/d | — | s6 | franchise |
| `molly` | 2D cel | none | western toon | colour | flat, heavy stylisation | int | 3 children | child | — | s15 | franchise |
| `mountain_rain` | painting | digital | realist | colour | matte-painting style | ext | none | — | — | s6 | — |
| `nadia` | 2D cel | none | anime | colour | promotional card with a title overlay | ext | 1 girl + 1 boy + 1 lion cub | child, teenager | — | s15 | text, franchise |
| `nerv` | 2D cel | none | anime | colour | painted BG, shaded; aerial — no line work, takes the figureless-plate accept-set | ext | none | — | — | s18 | franchise |
| `newspaper` | photograph | none | realist | colour | — | int | 1 adult man | adult | — | s6 | — |
| `p1_first` | live-action film | none | realist | colour | very dim | int | 1 adult man | adult | p1 | s6 | — |
| `p1_last` | live-action film | none | realist | colour | far brighter and closer | int | 1 adult man | adult | p1 | s6 | — |
| `p2_first` | live-action film | none | realist | colour | — | int | 1 pre-teen girl | pre-teen | p2 | s6 | text |
| `p2_last` | live-action film | none | realist | colour | near-identical light | int | 1 pre-teen girl | pre-teen | p2 | s6 | text |
| `p3_first` | live-action film | none | realist | colour | — | int | 1 pre-teen girl | pre-teen | p3 | s6 | text |
| `p3_last` | live-action film | none | realist | colour | near-identical | int | 1 pre-teen girl | pre-teen | p3 | s6 | text |
| `p4_first` | live-action film | none | realist | colour | heavy bokeh | ext | 1 pre-teen girl + 1 adult man | pre-teen, adult | p4 | s6 | — |
| `p4_last` | live-action film | none | realist | colour | same bokeh | ext | 1 pre-teen girl + 1 adult man | pre-teen, adult | p4 | s6 | — |
| `p5_first` | live-action film | none | realist | colour | night | ext | 1 adult man | n/d | p5 | s6 | — |
| `p5_last` | live-action film | none | realist | colour | tighter, heavy dissolve | ext | 1 adult man (+1 ghosted) | n/d | p5 | s6 | — |
| `p6_first` | live-action film | none | realist | colour | — | int | 1 pre-teen girl | pre-teen | p6-window | s6 | corr |
| `p6_last` | live-action film | none | realist | colour | same window, tighter | int | 1 pre-teen girl | pre-teen | p6-window | s6 | corr |
| `pancakes` | photograph | none | realist | colour | — | int | 1 adult man + 1 child girl | adult, child | char-drift | s6 | — |
| `pavilion_anime` | 2D cel | none | anime | colour | cel-era BG; roofed open-sided pavilion over water, soft airbrushed sky | ext | none | — | — | s18 | — |
| `peter_griffin_painting` | painting | digital | dimensional toon | colour | flat-cartoon character rendered painterly | none | 1 adult man | adult | peter-griffin | s7a | franchise |
| `peter_griffin_toon` | 2D cel | none | western toon | colour | modern flat digital | int | 2 adult men | adult | peter-griffin, toon-era | s7b | franchise |
| `phone` | photograph | none | realist | colour | cut out on pure white | none | 1 adult woman | middle-aged | — | s6 | — |
| `pjs` | stop-motion | figure | dimensional toon | colour | foam puppets; cast poster with a logo overlay | ext | 11+, including 1 older adult woman and 3 children | child, older adult, crowd | stopmo-sub | s15 | text, franchise |
| `pocahontas` | 2D cel | none | western toon | colour | **2D theatrical feature** | ext | 2 adults + 2 animals + 1 bird | young adult | feature-2d | s15 | franchise |
| `pooh` | 2D cel | none | western toon | colour | **figure present, non-human** — a stylised bear at naturalistic proportion, flat fills over a painted wood | ext | 1 bear (stylised, anthropomorphic) | n/a | — | s18 | franchise |
| `pre-teen1` | photograph | none | realist | colour | outdoor available light, shallow focus | ext | 1 pre-teen girl | pre-teen | age-bracket | s18 | real |
| `ramen_pixel` | pixel art | none | realist | colour | hi-fi, shaded, anti-aliased | none | none | — | — | s7a | — |
| `riley_preteen` | 3D CG | none | dimensional toon | colour | feature CG; large eyes, soft caricature, real hair and cloth | ext | 1 pre-teen girl | pre-teen | age-bracket | s18 | franchise |
| `river_mountain_anime` | 2D cel | none | anime | colour | painterly, visible brush texture, no line work — takes the figureless-plate accept-set | ext | none | — | — | s18 | — |
| `roadway_toon` | 2D cel | none | western toon | colour | painted BG, soft-edged, VHS-grade 4:3, no line work — takes the figureless-plate accept-set | ext | none | — | — | s18 | — |
| `room_anime` | 2D cel | none | anime | colour | cel BG; cluttered workshop-bedroom, heavy foreground machinery. **NOT figureless** — a small distant figure lies on the bed, facing away; excluded from the figureless evidence set as a confound | int | 1 distant figure (female, facing away, age not determinable) | n/d | — | s18 | — |
| `rudolf` | stop-motion | figure | dimensional toon | colour | flocked and felt over armature, fibre hair — a very different puppet from `coraline*` | ext | 1 elf figure + 1 reindeer | n/a | stopmo-sub | s15 | franchise |
| `rugrats` | 2D cel | none | western toon | colour | flat cel, VHS-grade; **heavily disproportionate** — huge heads, tiny limbs, flat pupils | int | 5 infants/toddlers + 1 adult's legs | infant, toddler, n/d | age-bracket | s18 | franchise |
| `saber_reference_anime` | 3D CG | none | anime | colour | **a 3D render, not a painting** — corrected s19: hair reads as rigid geometry, the bow/bowls/table carry render shading, and the background blur is true DOF. **Reads a bracket younger than its own source** — see the saber-ref note | int | 1 teenage girl | teenager | saber-ref | s18 | text, franchise |
| `saber_reference_painterly` | painting | digital | realist | colour | loose brushwork, semi-realistic face, background reduced to wash | int | 1 young adult woman | young adult | saber-ref | s18 | franchise |
| `saber_reference_photo` | photograph | none | realist | colour | **the source**; cosplay shot in a tatami room, soft window light | int | 1 young adult woman | young adult | saber-ref | s18 | text, real, franchise |
| `sam_jackson_jurassic_middle_aged` | live-action film | none | realist | colour | graded film still, cool key, CRT glow | int | 1 middle-aged man + 1 partial man at right | middle-aged, n/d | jurassic | s18 | text, real, franchise |
| `san_fransisco_day_evening_night` | vector | none | flat graphic | colour | **composite**, 3 stacked panels | ext | none | — | sanfran-daynight | s7b | — |
| `sanfran_day` | vector | none | flat graphic | colour | 1039x487 | ext | none | — | sanfran-daynight | s7b-crop | derived |
| `sanfran_evening` | vector | none | flat graphic | colour | 1039x487, golden sky | ext | none | — | sanfran-daynight | s7b-crop | derived |
| `sanfran_night` | vector | none | flat graphic | colour | 1039x487 | ext | none | — | sanfran-daynight | s7b-crop | derived |
| `scooby` | 2D cel | none | western toon | colour | modern flat promotional art; gradient shading on the background only | ext | 4 adults + 1 dog | young adult | — | s15 | text, franchise |
| `shed_day` | photograph | none | realist | colour | overcast daylight | ext | none | — | shed-daynight | s15 | — |
| `shed_dusk` | photograph | none | realist | colour | the intermediate state | ext | none | — | shed-daynight | s15 | — |
| `shed_night` | photograph | none | realist | colour | **night-mode composite** — foliage far brighter than a true night exposure, but far detail genuinely lost | ext | none | — | shed-daynight | s15 | — |
| `ship_gargantuan` | photograph | none | realist | colour | red-hulled product tanker under tow by two tugs, aerial view over a forested inlet; a frame from an online video | ext | several deck crew (tiny) | n/d | scale-ladder | s24 | text |
| `shoes_anime` | 2D cel | none | anime | colour | modern cel; ink outlines and hatching over flat fills — an **object** close-up, not a scene | int | none | — | — | s18 | — |
| `shrek_cg` | 3D CG | none | dimensional toon | colour | — | ext | 1 green ogre, close-up | adult | — | s7b | franchise |
| `simpsons_couch_toon` | 2D cel | none | western toon | colour | **entirely flat, unshaded, hard-outlined digital toon** — the figureless scene where `western toon` is the right answer, mirroring the v4c regressions | int | none | — | — | s18 | text, franchise |
| `skellington` | stop-motion | figure | dimensional toon | colour | feature stop-motion; matte moulded surfaces, stitched mouth, shallow focus | ext | 2 figures — 1 skeleton, 1 snowman | n/a | stopmo-sub | s18 | franchise |
| `sketch_boat` | drawing | pencil | realist | monochrome | graphite landscape, fine directional hatching, paper left as light | ext | none | — | sketch | s18 | — |
| `sketch_man` | drawing | pencil | realist | monochrome | **loose portrait study**; construction lines left on the surface, blunt soft-pencil hatching | none | 1 middle-aged man | middle-aged | sketch | s18 | — |
| `sketch_woman` | drawing | pencil | realist | monochrome | portrait study, lightly stylised lashes and lip; hatched shoulder | none | 1 young adult woman | young adult | sketch | s18 | — |
| `sleeping` | photograph | none | realist | colour | — | int | 1 young adult woman | young adult | — | s6 | — |
| `smart_car_large` | photograph | none | realist | colour | red and black two-seat city car at a suburban kerb. **The same model as `toy_car_minuscule`**, at full size | ext | 2 adults (seated in the car) | adult | scale-ladder | s24 | — |
| `spongebob_tree_toon` | 2D cel | none | western toon | colour | painted BG w/ dark contours and visible brush texture; strict | ext | none | — | — | s18 | franchise |
| `stage` | photograph | none | realist | colour | — | int | 1 woman + ~100 audience | young adult, crowd | — | s6 | — |
| `supergirl1` | drawing | marker | western toon | colour | copic-style on board | ext-ish (drawn panel) | 1 young woman | young adult | supergirl | s7a | text, franchise |
| `supergirl2` | drawing | marker | western toon | colour | **marker colour over an un-inked pencil sketch** — the colour medium is the same as `supergirl1`; only the linework differs. **Sub-term contested**, see the axis note under "Medium vocabulary" | none | same character | young adult | supergirl | s7a | text, franchise, corr |
| `suv_large` | photograph | none | realist | colour | red compact SUV on a rotating motor-show stand | int | several adults (stand staff and visitors) | adult | scale-ladder | s24 | text |
| `teddy_taft` | photograph | none | realist | monochrome | — | ext | 2 adult men | middle-aged | — | s7a | real |
| `temple_day` | painting | digital | anime | colour | high-key, painterly | ext | 1 young woman | young adult | temple | s7a | text |
| `temple_grounds_anime` | 2D cel | none | anime | colour | **modern digital** anime BG, near-photographic detail, no line work — takes the figureless-plate accept-set | ext | none | — | — | s18 | — |
| `temple_night` | painting | digital | anime | colour | low-key, same hand | ext | 1 young man | young adult | temple | s7a | text |
| `third_rock` | photograph | none | realist | colour | **a posed, flat-lit publicity still**, not a frame from the show — tie-break 4 | ext | 5: 1 middle-aged man, 1 middle-aged woman, 1 young adult man, 1 young adult woman, 1 teenage boy | teenager, young adult, middle-aged | age-bracket | s18 | real, franchise |
| `titans1` | 2D cel | none | western toon | colour | western TV series drawn in an anime idiom — **provisional** | int | 5 | teenager | titans, anime-toon | s15 | franchise |
| `titans_go` | 2D cel | none | western toon | colour | chibi proportions, heavy stylisation | ext | 5 | teenager | titans | s15 | franchise |
| `toddler` | photograph | none | realist | colour | warm domestic available light, shallow focus | int | 1 toddler girl | toddler | age-bracket | s18 | real |
| `town_tower_anime` | 2D cel | none | anime | colour | modern digital, heavy bloom, no line work — takes the figureless-plate accept-set | ext | none | — | — | s18 | — |
| `toy_car_minuscule` | photograph | none | realist | colour | die-cast city car pinched between finger and thumb over a cutting mat. **The same model as `smart_car_large`**, in toy form | int | 1 adult hand | n/d | scale-ladder | s24 | — |
| `toy_car_modest_1` | photograph | none | realist | colour | moulded plastic toddler ride-on car pushed along a park path | ext | 1 adult woman + 1 toddler | toddler, adult | scale-ladder | s24 | text |
| `toy_car_modest_2` | photograph | none | realist | colour | battery-powered child's ride-on go-kart on a city pavement | ext | 1 girl | child | scale-ladder | s24 | text |
| `toy_car_small_1` | vector | none | flat graphic | colour | flat vector illustration of a child holding a toy car; **the batch's only non-photograph** | none | 1 girl | child | scale-ladder | s24 | — |
| `toy_car_small_2` | photograph | none | realist | colour | large 1980s moulded toy sports car held in two hands, collectible shelving behind. **Text appears BOTH on the object (a franchise name on the trunk) and off it (the holder's t-shirt)** — the corpus's only such split | int | 1 middle-aged man | middle-aged | scale-ladder | s24 | text |
| `toy_car_tiny_1` | photograph | none | realist | colour | die-cast saloon held flat on one palm, model-car collection shelving behind | int | 1 young adult man | young adult | scale-ladder | s24 | text |
| `toy_car_tiny_2` | photograph | none | realist | colour | die-cast convertible held in the fingers above grass | ext | 1 adult hand | n/d | scale-ladder | s24 | — |
| `truck_huge` | photograph | none | realist | colour | red tri-axle dump truck at dusk with its running lights lit | ext | none | — | scale-ladder | s24 | text |
| `tv` | photograph | none | realist | colour | — | int | 1 older adult woman | older adult | — | s6 | — |
| `uniform_reference_anime` | painting | digital | anime | colour | semi-realistic anime face, flat-ish brush, same pose and light | ext | 1 teenage girl | teenager | uniform-ref | s18 | — |
| `uniform_reference_painterly` | painting | digital | realist | colour | very loose slabby brushwork, background broken into strokes | ext | 1 teenage girl | teenager | uniform-ref | s18 | — |
| `uniform_reference_photo` | photograph | none | realist | colour | **the source**; backlit late-afternoon sun, shallow depth of field | ext | 1 teenage girl | teenager | uniform-ref | s18 | real |
| `van_huge` | photograph | none | realist | colour | candy-red custom panel van on a rural road | ext | 1 adult woman (at the driver's window) | adult | scale-ladder | s24 | — |
| `van_pixel` | pixel art | none | anime | colour | PC-98 style, dithered, 16-colour | ext | 1 girl | teenager | — | s7a | text |
| `vector_city` | vector | none | flat graphic | colour | — | ext | none | — | — | s6 | — |
| `wayne_knight_jurassic_adult` | live-action film | none | realist | colour | graded film still, low key, banks of CRTs | int | 1 adult man | adult | jurassic, wayne-age | s18 | text, real, franchise |
| `wayne_knight_older_adult` | photograph | none | realist | colour | flat event/press lighting on a branded backdrop | int | 1 older adult man | older adult | wayne-age | s18 | text, real |
| `will_preteen` | live-action film | none | realist | colour | graded night still, low key | ext | 1 pre-teen boy | pre-teen | age-bracket | s18 | real, franchise |
| `window` | live-action film | none | realist | colour | tighter and blown out | int | 1 pre-teen girl | pre-teen | p6-window | s6 | corr |
| `woman_oil` | painting | oil | realist | colour | **traditional**, photorealist | int | 1 young woman, asleep | young adult | oil-idiom | s7b | — |
| `woman_reference_photo` | photograph | none | realist | colour | **the source**; close portrait, shallow focus, turned over the shoulder | int | 1 young adult woman | young adult | woman-ref | s18 | real |
| `woman_reference_sketch` | drawing | pencil | realist | monochrome | **graphite study on toned paper**, dense directional hatching; signed | none | 1 young adult woman | young adult | woman-ref | s18 | text |
| `woody_cg` | 3D CG | none | dimensional toon | colour | early CG | int | 1 male doll/figure | n/a | — | s7b | franchise |

---

## Contents table — what is in the frame

| image | setting | prominent objects | notable garments |
|---|---|---|---|
| `airliner_gargantuan` | airport apron, cloudy sky, terminal block and ground vehicles behind | **narrow-body airliner**, all-over red livery, white "SAT" titles, tail registration; ground power unit, baggage tug | (none legible) |
| `annie1` | no environment, cream paper ground | (none) | **girl**: coral open jacket, yellow tank, black skirt, black knee boots, choker · **hero**: black/red tunic w/ yellow bar fasteners, black cape, black glove, domino mask |
| `annie2` | **nested** — inside the drawing, a giant reptilian creature looming over a small girl; outside it, a defocused convention hall w/ black grid shelving | the sketchbook itself | coral jacket, pale yellow top, black shorts, choker, white socks |
| `annie2_cropped` | the painted page only — the creature and the girl, ink line over watercolour wash on textured paper | (none) | as `annie2` |
| `annie3` | alley between buildings; rooftop/street | (none) | **girl**: coral coat, tan top, black skirt, choker · **boy hero**: red/black tunic w/ yellow bars, black cape · **woman hero**: black/purple suit, yellow gloves and boots · **man**: tan shirt, striped trousers |
| `annie3_panel1` | alley, girl near-full-figure | (none) | as `annie3` |
| `april_1987` | night city; dark blue sky, a lit office tower at right | (none) | **woman**: yellow jumpsuit w/ zip front and shoulder yoke · **turtle**: orange eye mask, shell, brown straps |
| `april_1987_figure` | a wood-veneer shelf in a room; cabinet panelling behind, stacked books at right | **articulated plastic action figures** — a woman and four humanoid turtles, a rat figure behind; shoulder camcorder marked 6, pizza slice, katana, nunchaku, sai, bo staff; belt discs lettered L, M, R, D; lettered book spines | yellow jumpsuit w/ white belt and white boots; coloured eye masks, brown belts |
| `april_comic` | painted sky and a news truck behind the figure; printed comic trade dress framing the art | **shoulder camcorder marked 6**, wristwatch, news van w/ roof mast; publisher logo, issue number, creator credits, artist signature | yellow jumpsuit, unzipped, w/ white belt |
| `april_fanart` | no environment, white ground; a manhole cover behind the figure, **composited in — it is not drawn in the same medium as the figure** | **four stacked pizza boxes**, a bundle of coloured cloth, a wrist cuff | cropped yellow zip jacket, blue jeans, white belt |
| `avatar_1` | dry rocky canyon; red-brown stone walls, dirt floor. Pillarboxed | (none) | **boy**: red-orange robe over yellow, shaved head w/ an arrow marking, wrist bands · **girl**: pale green sleeveless tunic over dark green, wide black belt, headband |
| `avatar_2` | grass headland at night; sea and clouded sky behind, a canvas tent | **campfire**, bowls, cups; a foreground pole crosses the lower frame | green tunic, dark red robes, orange-and-yellow robe, blue-grey wrap |
| `ayanami_oil` | tiled washroom or pool edge; pale green tiles, dark floor tiles, green ledge | (none) | pale school swimsuit |
| `azumanga_anime` | no environment, white ground | (none) | coral sailor-style school jumpers, white collars, dark red pleated skirts, orange socks / white socks + brown loafers |
| `azumanga_toon` | school grounds; chain-link fence, clipped hedges, trees, grass, concrete path, brick edging, outline clouds — **all stylised into flat shapes, no real depth** | (none) | same coral uniforms; one w/ black over-knee socks |
| `baby_middle_aged` | pale room corner; large houseplants on a black metal stand, white wall, light switch | potted yucca and croton, **wristwatch on a green strap** | **man**: dark grey polo w/ a striped placket · **infant**: white long-sleeved bodysuit |
| `backyard_anime` | Japanese garden from above; lawn, boulders, pond at right, a walkway/bridge edge along the top | stone lantern at left | — |
| `beauty_beast` | stone balcony terrace at night; blue moonlit garden, balustrade, two large urns w/ willow trees | **stone urns**, balustrade; a site watermark at lower left | **woman**: off-shoulder gold ballgown, gold earrings, hair up · **beast**: blue tailcoat w/ gold trim, white cravat, black trousers, blue hair ribbon |
| `bird_vector` | no environment, white | (none) | — |
| `bird_watercolor` | no environment, paper ground | branch | — |
| `blonde_reference_painterly` | no environment, flat pale blue ground | the same gold glasses | navy pinstripe blazer, navy pinstripe trousers w/ red topstitching |
| `blonde_reference_photo` | no environment, pale green studio sweep | **a pair of gold wire-rimmed glasses** held to the mouth; **`CHUU` brand mark, upper left** | navy pinstripe blazer, navy pinstripe trousers w/ red topstitching |
| `boo_toddler` | a dim workroom; shelving and machinery behind, defocused | (none) | a loose pink smock over lilac leggings, pale socks |
| `bookshop` | Paris-style bookshop frontage from the pavement; shop interior through the open door | tiered book displays, ceiling strip lights (on), downpipe, vent grille, doormat | black sweater, dark jeans |
| `boondocks` | suburban living room; cream walls, crown moulding, brown sofa, wood display cabinet, framed pictures, table lamp | sofa, display cabinet, framed photographs, lamp | brown work shirt over a white tee; white ribbed vest |
| `bumper_car_medium` | airfield apron, grass and hangars behind | **fairground bumper car**: red body, white bumper skirt, chrome trim, ceiling pickup pole, steering wheel | white shirt, dark tie, dark trousers |
| `cannon` | stone-walled terrace/battery over woodland; limestone rubble walls, pale flagstones | **muzzle-loading cannon on a four-wheeled wooden carriage** | — |
| `captain` | deck of a sailing yacht at sea, clear sky | **ship's wheel** (large, varnished), boom, furled sail, rigging, blocks, guardrail | **captain's uniform**: white peaked cap w/ gold emblem, navy double-breasted jacket, 4 cuff stripes, ribbon bar |
| `car_1` | no environment, white | **white crossover SUV, front three-quarter**; roof rails, black wheel arches, maker emblem | — |
| `car_2` | no environment, white | **the same SUV, pure side view** — identical vehicle, lighting, ground and background | — |
| `car_building_gargantuan` | formal parterre garden before a baroque palace, gravel drive, box hedging and roses | **red gullwing coupe**; the palace facade, twin curved staircases, stone statuary | (none) |
| `car_interior_mecha_driver` | van/MPV cabin; city skyline through the windows | steering wheel, headrests, roof vent, **magazine w/ Japanese cover text** | school sailor uniform w/ blue neckerchief |
| `car_interior_photo` | front cabin of a modern electric car | steering wheel w/ **maker emblem**, large landscape touchscreen showing a map, wood dash trim, centre console | — |
| `car_interior_sketch` | car cabin, windows blown out white | steering wheel, headrest, seatbelt | olive short-sleeve shirt; pink tee |
| `car_interior_toon` | **front cabin of a car at night**; road barrier and trees through the glass | **steering wheel**, illuminated green dash controls, green seat backs, wing mirror | dark red sweater over a white collared shirt |
| `car_mountain_colossal` | wet mountain switchback road, snow-covered peak, larches, low cloud | **red sports coupe**, headlights lit | (none) |
| `castle` | castle grounds; round crenellated tower, curtain wall, cloudy sky | pennant flag, arrow-slit, partial wooden shield edge | **plate armour**: pauldrons, engraved cuirass, gorget, mail sleeves, gauntlets, brown belt |
| `chair` | no environment, pure white | **executive office chair**: black ribbed leather, gold-tone arms and five-star base, castors | — |
| `chips_hotdog_dr_pepper_painting` | painted backdrop and tabletop | **chip bag, glass soda bottle, hot dog in a bun, loose chips** — all w/ **painted brand text** | — |
| `city_day` | **downtown skyline from above**, daylight, blue sky w/ cirrus; glass and masonry towers, a gold curtain-wall tower, a stepped-crown tower, low-rise grid, distant treeline | rooftop antennas, **rooftop brand signage**, construction scaffolding | — |
| `city_night` | **same skyline, same camera position**, blue hour; orange horizon glow, lit windows throughout | same towers; **illuminated signs and a lit crown** now readable, low-rise detail lost | — |
| `classroom1` | bright modern classroom; cream walls, curtained window | light-wood desks, storage cabinet, world-map bulletin board, open books, orange pencils | blue/white striped shirts, red neckties, navy pleated skirts |
| `classroom2` | older classroom; orange-yellow walls, tall windows | wooden desks, potted plant on sill, blue hardback, blue pencils, framed poster | navy waistcoats, white shirts, striped ties; houndstooth shirt-dress |
| `classroom_anime_empty` | empty classroom; window wall at left w/ low sun, green chalkboard, panelled ceiling, door at right | desks and chairs in rows, wall clock, teacher's lectern, cork noticeboard w/ pinned sheets; **a `4anime.to` site watermark, upper left** | — |
| `cleo_slingshot` | a desert canyon; ochre haze, red rock, carved statues and a stone column | **a wooden slingshot**, carved figures, a column capital | **girl**: white shift, red sash, gold collar and headband, gold armband · **boy**: white wrap w/ a green sash, striped headwrap, dark collar |
| `cloud` | grassy plain under towering cumulus; dirt track, distant blue hills, contrail | wooden fence, small white utility building | — |
| `comic` | classroom; desks, whiteboard w/ geometry diagram, windows, planter boxes | pencil, spider, papers, backpack | black/red/white school uniforms w/ ties; grey blazer; red/black armoured super-suit |
| `comic_panel2` | close-up, classroom behind | (none) | school uniform |
| `comic_panel3` | **same room as `comic_panel4`**; whiteboard | dialogue balloon | grey blazer |
| `comic_panel4` | classroom interior; desks, windows, planter boxes | desks, papers | school uniforms w/ ties |
| `coraline1` | no environment — **transparent ground**, which the model receives as black, not white | forked twig | yellow raincoat, blue jeans, yellow wellingtons, dragonfly hair clip |
| `coraline2` | dim kitchen; sash window, panelled cabinets, deep sink, tiled splashback, round table | open laptop, **mug reading "I love Mulch"**, notebook, pen, a doll | yellow raincoat; grey knitted cardigan |
| `couple_middle_aged` | a bright living room; a white sofa, a tall window w/ a city view and a sheer curtain | **the sofa**, a wedding ring | matching pale blue denim shirts |
| `destroyer_drawing` | no environment | side elevation + plan view of a warship, range scale, rising-sun emblem | — |
| `destroyer_photo` | warship at anchor, calm water, blank pale sky, distant masts | twin funnels making smoke, turrets, torpedo tubes, bridge tower, ensign; **kana + "19" on the hull** | — |
| `door_first` | dim tenement corridor; vertically striped patterned wallpaper, painted timber frames; a green panelled door **numbered 410**, shut but standing a hand's width proud of its frame with a lit gap at the hinge side | brass doorknob, a small placard on the left wall, a glazed inner door at right with dirty glass and a diagonal strap across it, partial lettering low right | — |
| `door_last` | **the same corridor, the 410 door now standing open** onto the room beyond: arched window with pale curtains, wooden chair, papers on a low table | dark travelling case being lifted, same brass knob, same glazed door and lettering at right | black overcoat, dark knit cap, white t-shirt |
| `fern_gully` | rainforest floor; broad green leaves and vines, shafts of light | (none) | leaf and petal garments — green leaf dress, red petal top and skirt, yellow petal wrap, purple armband |
| `fish_pixel` | no environment, dark banded ground | side-on fish, teal-green back, white belly | — |
| `forest_autumn` | **beech forest in fog**, autumn; grey trunks, rust foliage, deep leaf litter, exposed roots, dirt path | (none) | — |
| `forest_day_night` | the two panels above, stacked | (none) | — |
| `forest_day` / `forest_night` | one forest clearing backed by broadleaf trees and low scrub; grass foreground, distant hills | (none) | — |
| `fruit_reference_photo` | a weathered wooden table against a grey cloth backdrop | **an orange w/ leaves still attached** on a **white plaster cube**, a **palette knife** w/ a wooden handle, a kumquat, a pale apple, olive and cream cloths | — |
| `fruit_reference_sketch` | the same table and backdrop, rendered in graphite | the same orange, plaster cube, palette knife, kumquat and apple | — |
| `fruitbowl` | plain warm backdrop, wood tabletop | dark ceramic bowl of fruit (green apple, 2 red apples, grapes, 2 bananas), **2 wine bottles w/ illegible script labels**, 1 loose apple | — |
| `fuji` | **thatched village by a pond, snow-capped volcano behind**; topiary, azaleas, clipped hedge, conifers, deep blue sky | thatched roofs, **water wheel**, stone lantern | — |
| `garden_pond_anime` | the same garden at night; pond, boulder outcrop, dark treeline, grass bank | **a lit stone lantern**, right foreground | — |
| `ghibli_grass` | a meadow at golden hour; treeline behind, flat fields at right, heavy blue-grey cloud over a bright sky | tall grasses and seed heads, **orange day-lilies**, white and mauve flowers | — |
| `ghibli_kitchen` | a domestic kitchen; green tiled walls, olive cabinets, dark red tiled floor, a shuttered window upper right | a white-topped island, **a glass blender**, an enamel kettle, stacked cups, jam jars, a fruit basket, hanging utensils, a copper range hood | — |
| `ghibli_painting_reference_anime` | a grassy hillside falling away to green hills; tall cumulus over a deep blue sky | a pale boulder mid-slope, mauve flowering stems, low shrubs | — |
| `ghibli_painting_reference_painterly` | the same hillside, rock and hills, more loosely brushed | the same boulder; **an `SGRIM ARTZ` signature block, lower left** | — |
| `ghibli_street` | a city street corner; a stone-fronted building w/ awnings, cobbled roadway, street trees | period cars, a yellow flatbed truck, a signpost; **`Valvoline`, `Boss` and `Saima` signage** | summer dresses in pink, red, blue and white; shirtsleeves, braces, sun hats |
| `girl_painting` | no environment, grey painterly ground | (none) | black choker, pale knit |
| `girl_painting_reference` | plain grey-green wall | (none) | black velvet choker, lilac knit |
| `gordon_1996` | dark vehicle interior at night; seat back and window behind | (none) | tan trench coat, grey shirt, black necktie, heavy black-framed glasses |
| `gordon_2004` | night city skyline; dark spired towers w/ lit windows, purple sky | (none) | olive-tan trench coat, pale blue shirt, black necktie, black-framed glasses |
| `gordon_comic` | suspension-bridge cables and a daytime city skyline behind | **speech balloon, partly cropped** | brown leather coat, pale blue shirt, dark blue necktie, thin-framed glasses |
| `grass_anime_girl` | the same meadow and sky | white daisies, mauve flowers | **girl**: white pinafore over a purple puff-sleeved top, gold clasp at the collar · **animal**: red neckerchief |
| `grass_anime_scenery` | meadow against a blue sky; tall grass blades across the lower third, cumulus and wisps above | white daisies, small mauve flowers | — |
| `gromit` | **brick garage interior**, up-and-over door raised onto a sunlit street of brick terraces; tool board, roof beams, paint tins | **beige panel van lettered GNOME IMPROVEMENTS / No job too small**, a green engine, hand tools, saws, terracotta pots, a rope coil, wooden crates w/ printed text, a clipboard, a bicycle wheel | **man**: green knitted tank top, white shirt, red tie, brown trousers |
| `gumby` | diner or saloon interior; wooden floor, red-checked tables, bentwood chairs, a patterned wall hanging, saloon doors | **two tall milkshake glasses w/ straws**, tables, chairs | **red-orange figure, left**: a **horse**, but bipedal, upright and anthropomorphised — see the `character` note · **background figure**: green pointed hat, pink body |
| `gwen` | **interior of a motorhome or bus**; orange ribbed bench seats, a window w/ pale daylight, wood-grain table | **a printed chart headed VACATION SCHEDULE**, coloured blocks | blue raglan top w/ a cat-face motif; purple hoodie over a pink top w/ a dark chevron, goggles on the head |
| `gwen_cg` | living room; pale sofa, wooden shelving w/ books and small elephant figurines, a framed picture | **bookshelf w/ lettered spines**, elephant ornaments, framed art | blue long-sleeved top w/ a cat-face motif |
| `hermione_preteen` | a stone washroom; a ring of basins on a central column, drain grilles in the floor | **a black cauldron** on a stand, a lit burner, glass phials, **a handwritten parchment sheet** | grey V-neck jumper over a white shirt, red-and-gold striped tie |
| `ivy_toon` | blue technological interior; circuit-trace wall panels, yellow door frame | **a white and grey handheld device on a chain** | brown leather jacket, white top, khaki trousers |
| `jacket` | **snowy park** — bare trees, falling snow, snow-covered ground | (none) | **grey quilted puffer jacket** w/ hood |
| `jacket2` | **same snowy park**, seated on a bench; near-featureless snow field behind | **wrought-iron bench** (scrollwork), brown leather handbag | same grey puffer jacket, **fur-trimmed mittens** |
| `kasia` | no environment, plain pale-grey backdrop | **orange shoulder bag** w/ blue strap + **3 pin badges** | black tank, denim cuffed shorts, fingerless gloves, striped knee socks, blue sneakers, **orange** headband |
| `kasia_bag` | no environment, white | **yellow shoulder bag, blue flap w/ pale-blue circular emblem, navy webbing strap, gold slider** — no pin badges | — |
| `kasia_bag_2` | no environment, white | **the same bag upright, three-quarter front**; strap looped over the top | — |
| `kasia_outfit` | no environment, white | — | **black vest top, cuffed blue denim shorts, black/blue fingerless gloves, black-and-grey striped knee socks, blue lace-up sneakers** |
| `kasia_render` | no environment, white studio ground | (none) | black vest top, cuffed denim shorts, black fingerless gloves, grey striped knee socks, navy/white sneakers, **gold-yellow headband** |
| `kasia_swimsuit` | no environment, white | — | **black high-neck one-piece swimsuit, yellow collar and yellow chevron** |
| `kasia_swimsuit_render` | poolside; clipped hedge, handrails, pale coping, blue water | handrails | **the same swimsuit**, worn |
| `kasia_swimsuit_worn` | no environment, stylised water-pattern band on white | (none) | **the same swimsuit**, worn (character: black bob, **yellow** headband, green eyes, freckles) |
| `kaypro_ii` | no environment, white | **vintage portable computer**: blue/grey metal case, green CRT showing text, 2 floppy drives, detached keyboard w/ blue keypad · **brand name on case AND on screen** | — |
| `kiki` | no environment; floating props | **6–7 breads/pastries** (loaf, baguette, rolls, filled bun) | navy long-sleeve top, red bow headband |
| `laika` | a school hall; pale plaster walls, tall barred windows, dark lockers and noticeboards, a water cooler at right | **a wall plaque**, lockers, a flag, a water-cooler bottle | **boy**: rust ribbed cardigan over a pale tee w/ a small badge, backpack straps, jeans · **other boy**: navy varsity jacket over yellow, teal shorts |
| `lego1` | a built restaurant facade; red and green brickwork, gold balustrades, an arched blue window, a brown plank deck | **swords and a rifle**, a turkey leg, lanterns; a **`Baratie`** sign, red hanging banners w/ lettering | striped blue-and-white shirt, red waistcoat, black coat and wide hat, blue sash |
| `lego2` | a brick-built street; grey plate roadway, a red-brick wall at left, buildings behind | **a green crate**, brick wall detail, visible plate studs | red top, blue legs, brown hair piece |
| `lincoln_money` | no environment | five-dollar certificate: portrait vignette, guilloche borders, blue treasury seal, serials, signatures — **almost entirely printed text** | — |
| `lincoln_photo` | no environment, plain studio backdrop | (none) | dark frock coat, white shirt, black bow tie |
| `maggie_grandpa_cat` | pink living room; orange sofa, patterned oval rug, side table w/ lamp, framed sailboat picture, standard lamp | **cat litter tray w/ scattered litter**, a bowl of crisps, a jar lettered CHIP DIP, books, a red wagon | **man**: pale pink cardigan, grey trousers, red slippers · **infant**: blue sleepsuit, blue hair bow |
| `marker` | window with blue sky and clouds behind her; drawn board border | window | off-shoulder cable-knit top, dark high-waisted pleated skirt, black ribbon choker, hoop earrings, hair ribbons |
| `misato_car_1` | a mountain road at dusk; steel guardrail, wooded slope, hazy ridge and streaked sky behind | the blue coupe head-on, pop-up lamps raised; a dashed centre line | — |
| `misato_car_2` | a road tunnel mouth; chain-link fencing, a retaining wall, gantry signage, hazard chevrons | the blue coupe from behind w/ a rear spoiler; **Japanese gantry signs, a speed roundel, a lettered rear plate** | — |
| `misato_car_real` | an indoor classic-car show; carpeted floor, other cars either side, a green chain barrier at lower left | **a blue Alpine A310 coupe**, quad headlamps w/ two yellow; a `FACEL VEGA` book on a table, folding chairs, info placards; **plates `6585 ML 32` and `382-WV`**, a card reading `ALPINE RENAULT A310 1600VE` | **men**: white shirt, checked shirt |
| `misato_car_technical_print` | no environment, white ground | **four views of the blue coupe**; the title `ALPINE A 310 V6`, the year `1979`, an artist signature, lettered plates on the front and rear views | — |
| `miya` | winter hillside road/lookout above a valley town; guardrail, bare trees, snow | guardrail, small trash bin, power pylons | cream double-breasted coat, black fur collar, grey pleated skirt, brown backpack, **cream headphones** |
| `miyu` | no environment, black void; ground litter only | **wheelie bin** (recycling pictograms, lid open), scattered leaves | not readable (occluded) |
| `molly` | attic bedroom; bare wood floor and beams, a bed heaped w/ cushions and soft toys, a patterned rug | **many soft toys** — rabbits, bears, a frog, a clown, a crowned bear; a playing card | three matching pink polka-dot pyjama sets, grey slippers |
| `mountain_rain` | **alpine panorama in driving rain**; snow-capped range, mossy rock ledge, conifers, alpine flowers, snow patches, dead trunk | (none) | — |
| `nadia` | grassy headland above a bay; sea, cumulus sky, a distant wooded point | **title and tagline overlay, lower right** | **girl**: white and red bandeau top, red wrap skirt, gold arm and ankle bangles, gold earrings · **boy**: white shirt, bow tie, blue knee breeches, green cap, round glasses |
| `nerv` | aerial over forest and lake; coast beyond | a black pyramid, a sunken glass-roofed pyramid, a white tower at right | — |
| `newspaper` | bright minimal living room; cream walls, built-in white shelving | **folded broadsheet newspaper**, books, oatmeal armchair | navy shirt, dark trousers, black belt |
| `p1_first` | shabby apartment room, ochre distempered walls, very dim | **transistor radio**, handgun, corduroy couch, leather armchair, pole-mounted shelf + lamp, folding side table, tin ashtray | black top, shoulder-holster straps, round sunglasses |
| `p1_last` | same room, far brighter and closer | same radio, shelf, framed item | same |
| `p2_first` | shabby kitchen; yellow cabinets, maroon splashback, lace-curtained window | disassembled handguns, cloth, 2 solvent bottles, green dish rack, sink+tap, paper-towel roll, **box w/ brand text** | sage sleeveless waistcoat over white vest |
| `p2_last` | same kitchen, near-identical light | same | same |
| `p3_first` | dining room; ivory raised-panel wainscot, dark polished table | **cereal box w/ large brand text** (green lettering), milk carton, pink milkshake glass, cut-glass fruit bowl, floral bowl + spoon, woven placemat | grey/white striped pyjama shirt |
| `p3_last` | same room, near-identical | same | same |
| `p4_first` | city street, **background almost entirely defocused**, blown white sky | **leather case w/ brass latches**, second black case, potted houseplant, paper bag, blurred bus | olive bomber jacket, green/striped dress, choker; long dark overcoat |
| `p4_last` | same street, same bokeh | same | same |
| `p5_first` | studio-backlot city street **at night**; granite building corner, masonry apartments, lit windows | **1950s cars** (black sedan, red/white taxi), terracotta potted shrub, wooden double doors, stone kerb | black suit, white shirt, black tie, pocket square, **fedora**, **roller skates** |
| `p5_last` | same corner, tighter, heavy dissolve/superimposition of a second figure | same | same |
| `p6_first` | room with a **window** (not a doorway); peeling green-cream window frames, **exposed red brick** and a blue panel seen outside through it | 2 framed pictures, curtain, wooden floor | striped knit top, black choker w/ sun pendant, knee socks |
| `p6_last` | same window, tighter | same brick, frames | same |
| `pancakes` | modern kitchen; white tiled splashback, gas hob, extractor | **frying pan + pancakes**, spatula, grey plate of pancakes, whisk, wall control panel | white t-shirt, blue trousers; white floral pyjamas |
| `pavilion_anime` | a roofed open-sided pavilion over water; posts, hanging lamps, a green hillside at right | a wooden bench, hanging lamps | — |
| `peter_griffin_painting` | no environment, dark olive gradient | (none) | white collared shirt |
| `peter_griffin_toon` | office; desk, wall poster, framed wall chart, dark carpet | desktop monitor, keyboard, mouse, phone | white shirt w/ black belt, green trousers, brown shoes; blue polo |
| `phone` | studio white, no environment | **smartphone w/ teal bumper** | sleeveless blue knit top |
| `pjs` | **housing-project courtyard**; brick blocks, bare trees, railings, concrete steps, barred windows, tarmac | **a large embossed manhole-cover logo overlaid on the lower frame**, a walking cane, a window air-conditioner | patterned headwrap and matching robe, pink dress w/ purple top, yellow hooded top, blue floral housecoat, dungarees over a yellow tee, striped tee and sneakers, a cap lettered Nevada |
| `pocahontas` | forest at dusk; a great tree w/ a face-like bark formation, a hanging willow curtain, drifting coloured leaves | **drifting leaves** | **woman**: pale buckskin one-shoulder dress, blue stone necklace · **man**: blue shirt, dark breeches, tall boots |
| `pooh` | a pine wood; tall trunks, a dirt path, a sunlit clearing behind | **a small hammer** in the bear's left hand | red short-sleeved shirt |
| `pre-teen1` | a defocused sunlit exterior; a pale ledge in the foreground | (none) | a red, white and navy horizontally striped vest top |
| `ramen_pixel` | no environment, dark ground w/ drop shadow | **bowl of ramen**: noodles, sliced pork, halved soft egg, spring onion, bamboo shoot, steam | — |
| `riley_preteen` | a residential street; a pale bay-fronted house and street trees behind, defocused | (none) | a mustard-yellow zip hoodie over a dark top |
| `river_mountain_anime` | a mountain valley from above; a braided river, snow-streaked peaks, clouds below the summits | — | — |
| `roadway_toon` | a two-lane road running straight to a distant city skyline; mown grass banks, scattered trees, hazy towers | the dashed white centre line | — |
| `room_anime` | a cluttered workshop-bedroom; plank floor, blue plaster wall, a tall window, shelving and cabinets, tools and drawings pinned above | large machine housings in the foreground, a bench drill, a teddy bear on a cabinet, a bed w/ white bedding | white dress (the distant figure) |
| `rudolf` | snowfield w/ flocked green trees, pale sky | (none) | **elf**: blue tunic w/ white fur trim, black belt w/ a square buckle, blue-and-pink pointed hat |
| `rugrats` | a living room; peach walls, grey carpet, a pink armchair | **the armchair**, a coat draped over it | green pinafores w/ a duck motif, an orange-and-purple top, blue jeans, a nappy, a blue tee w/ green shorts |
| `saber_reference_anime` | the same room; a calligraphy scroll behind, the low table at right w/ stacked bowls | the same striped teacup, stacked white and brown bowls, a red cushion; **Japanese characters on the scroll** | white long-sleeved blouse w/ a stand collar, navy pinafore skirt, navy neck bow, blue hair ribbon |
| `saber_reference_painterly` | the same room, reduced to a soft wash; the table edge at right | the striped teacup | white blouse, navy pinafore skirt, dark neck ribbon, blue hair ribbon |
| `saber_reference_photo` | a tatami room; plaster wall, a hanging scroll w/ a painted fan, a low wooden table at right | **a blue-and-white striped teacup**, a red floor cushion, a woven table mat; a **`COSPLAYSHOTS.COM 2010`** watermark | white long-sleeved blouse w/ a stand collar, navy pinafore skirt, dark neck ribbon, blue hair ribbon |
| `sam_jackson_jurassic_middle_aged` | a control room; a CRT monitor at left showing a map, a circular bulkhead behind | **a wire-boom headset**, aviator glasses, pens in a breast pocket, **a park logo patch** | a white lab coat over a patterned tie and shirt |
| `san_fransisco_day_evening_night` | the three panels above, stacked | (none) | — |
| `sanfran_day` / `sanfran_evening` / `sanfran_night` | grass bank and conifers, a red suspension bridge at left, a white high-rise cluster at right, water across the foreground | (none) | — |
| `scooby` | night woodland; bare twisted trees, a silhouetted castle on a hill, blue mist | **a green and turquoise panel van lettered THE MYSTERY MACHINE**, flower decals, a map | green tee; orange turtleneck w/ dark-framed glasses; purple dress w/ green headband; white shirt w/ orange ascot |
| `shed_day` | **residential back garden, overcast daylight**; mown lawn, clipped hedge, chain-link fence and timber retaining wall, a large spruce, a paved patch, brick houses on a rise behind | **a brown garden shed w/ a shingled roof and an open lean-to**, a glass-topped patio table, a stacked pile of cut branches, a hanging ornament | — |
| `shed_dusk` | **the same garden at dusk** — flat blue-grey light, no cast shadows, house windows not yet lit | the same shed, table and branch pile | — |
| `shed_night` | **the same garden at night**; lit windows in the houses behind, a bright lamp at upper right, far detail lost | the same shed, table and branch pile | — |
| `ship_gargantuan` | forested inlet, grey water and sky | **red-hulled product tanker**: white superstructure, green deck, pipework manifold, foremast; two tugs in yellow and blue | red deck coveralls (crew, tiny) |
| `shoes_anime` | a concrete genkan step, dark wood panelling behind | **two pairs of shoes** — white lace-up trainers, brown leather slip-ons | the shoes themselves |
| `shrek_cg` | open sky, wispy cloud, dry grass at right | (none) | brown leather-look tunic, cream undershirt w/ lacing |
| `simpsons_couch_toon` | a living room; pink walls, teal carpet, two arched doorways, a tiled hall visible at left | **an orange three-seat couch**, a side table w/ a teal push-button phone and a purple lamp, an arc floor lamp, a framed sailboat picture, an oval concentric rug, a TV and console in the foreground; **a `Global HD` bug, lower right** | — |
| `skellington` | a snowy exterior at night; violet drifts, red and green lights blurred behind | **a snowflake held in a twig hand**, a green top hat, coal buttons | black-and-white pinstripe suit w/ a bat bow tie |
| `sketch_boat` | a still mountain lake; layered peaks behind, conifer slopes either side, reflections on the water | **an empty wooden canoe** in the foreground | — |
| `sketch_man` | no environment, white paper | (none) | an open shirt collar |
| `sketch_woman` | no environment, cream paper | (none) | a wide-necked top w/ a hatched shoulder |
| `sleeping` | bedroom; grey tweed upholstered bed frame, white linen, light-wood bedside table | **black-framed eyeglasses**, pillows, duvet | navy top |
| `smart_car_large` | suburban street, kerb, brick houses, parked cars, grass verge | **red and black two-seat city car**: black tridion cell, alloy wheels; a blue hatchback and other parked cars behind | floral shirt (driver) |
| `spongebob_tree_toon` | a grassy rise under a blue sky; a large oak at right | **a door set into the tree trunk**, a purple spoked wheel on a post, yellow five-petal flowers at left, a bench edge at right | — |
| `stage` | **grand theatre auditorium** — two gilded balcony tiers, plaster cartouches, globe lights, red velvet seating, red aisle, stage floor | stage lighting units, recessed downlights, tiered seating | blue sleeveless dress, blue heels |
| `supergirl1` | sky and stylised clouds inside a drawn panel on white board | (none) | white crop tee w/ red-and-yellow chest emblem, blue skirt, red cape, white gloves, red boots, blue headband |
| `supergirl2` | no environment, white | (none) | same costume |
| `suv_large` | motor-show hall, wooden floor, mezzanine stand, video wall | **red compact SUV**: silver roof rails and mirror caps, five-spoke alloys, "XC 60" plate; blue cars on adjacent stands | blue shirt and dark trousers (stand cleaner), suits and a tan coat (visitors) |
| `teddy_taft` | portico/doorway; wet stone step, glazed door, fluted column | (none) | dark overcoats, waistcoat, watch chain, boutonniere, pince-nez |
| `temple_day` | gothic ecclesiastical exterior in bright sun; twin-lancet traceried window, columns, balustraded stair rising, spire beyond, potted agaves, trailing greenery, doves | (none) | strapless cream gown, pale green sash, hair ribbon |
| `temple_grounds_anime` | shrine grounds; a stone path to a green-roofed shrine, two buildings flanking, a dense treeline, clear blue sky | the shrine, the flanking buildings | — |
| `temple_night` | **the same architecture, ruined and dark**: same window and tracery, same stair now broken, rubble, fallen beams, torn red banner, dim violet sky | (none) | cream tunic, brown trousers, tall boots, red cape w/ fur collar, belt; **holding a sword** |
| `third_rock` | a porch set; white French doors, clapboard, ivy, **string lights shaped like carrots and chicks** | the string lights, a shuttered window | a patterned bowling shirt, a blue shirt w/ a red patterned tie, a lilac blouse, a rust cardigan, a gold-and-red striped polo |
| `titans1` | dark interior; grey wall panels, a large blank screen, an orange circuit-trace pattern, red floor | **a grey handheld device** | red and green tunic w/ yellow belt and cape; purple crop top and skirt w/ silver armbands; dark blue hooded cloak over a black leotard; magenta and grey bodysuit; white and grey armour plating |
| `titans_go` | **blue brick wall**, flat, no depth | (none) | as `titans1`, simplified — red and green tunic w/ yellow belt; purple cloak and hood; purple top and skirt; magenta and grey suit; grey armour |
| `toddler` | a narrow galley kitchen; white cabinets, wooden floorboards, a bright window at the end | open shelving w/ pans and lids, a knife block, a plant on the sill | rust corduroy dungarees over a cream floral long-sleeved top |
| `town_tower_anime` | a hillside town at sunrise; red-tiled roofs, a river, hills behind | a stone tower w/ a red conical roof and a spire | — |
| `toy_car_minuscule` | indoor, plain pale ground with a green cutting mat | **die-cast city car**, red with a black roof and tridion cell | (none) |
| `toy_car_modest_1` | park path, mown grass, trees, sunlight | **moulded plastic ride-on car**: orange body, yellow roof and roll bar, moulded eyes, white wheels | pink checked shirt, jeans, black flats (adult); aqua tee (toddler) |
| `toy_car_modest_2` | city pavement, crossing markings, shopfront behind | **child's ride-on go-kart**: red body, black steering wheel, rear wing, white wheels, remote handset | white patterned tee, denim shorts, blue hair bow |
| `toy_car_small_1` | no environment, plain white ground | **toy car**: red body, grey windows, black wheels with grey hubs | blue long-sleeved top |
| `toy_car_small_2` | indoor, shelving of boxed collectibles and lunch boxes | **moulded toy sports car**: red body, black targa panel and louvres, chrome wheels, **a franchise name on the trunk — small but legible**; a small driver figure inside | grey t-shirt with **large printed lettering** |
| `toy_car_tiny_1` | indoor, glass-fronted shelving of model cars | **die-cast saloon**, red with a tan interior and a roof-mounted clear box | grey printed t-shirt, dark-framed glasses |
| `toy_car_tiny_2` | outdoors, mown grass | **die-cast convertible**: red body, chrome windscreen frame and bumpers, black interior, red-hubbed wheels | (none) |
| `truck_huge` | yard at dusk, workshop building, trees, deep blue sky | **red tri-axle dump truck**: chrome grille, stacks and wheels, amber marker lights, raised sides | (none) |
| `tv` | domestic living room; damask wallpaper, dark wood TV stand | **CRT television** (off), DVD/VCR player, cables | navy botanical-print blouse, dark trousers |
| `uniform_reference_anime` | the same track and fields, softened | the same school bag | white short-sleeved sailor blouse w/ navy collar and bow, navy pleated skirt, navy knee socks |
| `uniform_reference_painterly` | the same track, broken into loose strokes | the same school bag | white sailor blouse w/ navy collar and bow, navy pleated skirt, navy knee socks |
| `uniform_reference_photo` | a dirt farm track; grass verges and yellow rapeseed fields behind, low sun | **a navy school bag** w/ pale webbing handles | white short-sleeved sailor blouse w/ navy collar and bow, navy pleated skirt, navy knee socks |
| `van_huge` | rural road, cropped field, trees | **candy-red custom panel van**: chrome slotted wheels, black mirrors, bubble side window, tinted glass | pink top, sunglasses |
| `van_pixel` | roadside; trees, orange-red sky | **blue MPV/van**, front three-quarter, roof rack + luggage, **licence plate** | blue and white outfit, cap |
| `vector_city` | stylised skyline of angular towers in coral and grey, reflected in water; teal sky, stylised clouds, sun flare | foreground rocks | — |
| `wayne_knight_jurassic_adult` | a cluttered workstation; two CRT monitors, stacked papers and sticky notes | **a soft-drink can**, keyboards, a mug, an ID badge, a small dinosaur figure, floppy disks | a grey windbreaker over a teal patterned shirt |
| `wayne_knight_older_adult` | no environment; a pale blue branded step-and-repeat backdrop | **partial lettering on the backdrop**, spectacles | a black zip polo w/ a small crocodile logo |
| `will_preteen` | beside a parked car at night; window glass and body panels behind | **the car** | a red quilted gilet over a navy-and-yellow plaid shirt, backpack straps |
| `window` | **the same window as `p6`**, shot tighter and blown out — environment essentially unreadable | (none legible) | striped knit top, choker w/ pendant, knee socks, stuffed toy |
| `woman_oil` | dark room; black wall, dark bench or piano stool, white drape at right | dark bench/stool w/ visible hinge, crumpled white cloth | cream puff-sleeved blouse, dark skirt |
| `woman_reference_photo` | a defocused pale interior; a grey panel at left, a bright window at right | (none) | white top w/ a textured floral shoulder |
| `woman_reference_sketch` | no environment, toned paper w/ background hatching | **an artist signature, lower left** | the same textured shoulder, lightly indicated |
| `woody_cg` | dim room, brown/ochre ground, indistinct | **holster on the belt**, sheriff badge | yellow check shirt, cow-print waistcoat, blue jeans, brown boots w/ spurs, brown hat |

---

## Probe pairs & sets

Merged from the three per-session pair lists. **Tier** says how much of a control it is:
`exact` = nothing varies but the one thing under test · `tight` · `loose` = same idea, much
else redrawn. Use the top for regression, the bottom for coverage.

**`p1`–`p6` and `door` are first-and-last frames of a single shot** — `*_first` is the opening
frame and `*_last` the closing frame of the same continuous take. That is why they exist: they
were sourced as **FL2VA fixtures**, not as same-place pairs. It was never written down before
session 8, and it changes how they should be read:

- **`setting` and `character` use them as same-place / same-person pairs**, which ignores the
  ordering. A disagreement is drift.
- **The frame describer and the FL2VA delta use them as before/after**, which depends on it
  entirely. A disagreement may be the *content* of the shot rather than a defect — that is the
  whole point of a delta.

So the same pair is a stability probe for one role and a change probe for another. Check which
you are running before scoring anything.

| set | files | holds constant | role | tier |
|---|---|---|---|---|
| girl-painting | `girl_painting_reference` → `girl_painting` | **everything** — the painting was made *from* that still: same subject, pose, crop, framing, expression | style | **exact.** The only true control; any content difference is a defect |
| car-angle | `car_1` / `car_2` | one object, two angles — same medium, lighting, ground, background. **Nothing varies but viewpoint** | object | **exact.** The object-viewpoint control |
| city-daynight | `city_day` / `city_night` | same skyline, same camera, **day vs blue hour** | setting | **the atmosphere-quarantine bar.** See the confound note below |
| shed-daynight | `shed_day` / `shed_dusk` / `shed_night` | one back garden, **three lighting states, photographic AND signage-free** | setting | tight. **The atmosphere bar without the signage confound** — closes standing gap 1; see the note below |
| p2 | `p2_first` / `p2_last` | same kitchen, near-identical light and framing | setting | tight — the clean control |
| p3 | `p3_first` / `p3_last` | same dining room, near-identical | setting | tight — second clean control |
| forest-daynight | `forest_day` / `forest_night` | one vector scene, relit, **signage-free** | setting | tight, but *easier* than `city-*` — see below |
| sanfran-daynight | `sanfran_day` / `_evening` / `_night` | one scene, **three** lighting states | setting | tight; the only series rather than pair |
| supergirl | `supergirl1` / `supergirl2` | same character, costume, near-identical flying pose; marker board vs rough pencil | style | very tight |
| gwen | `gwen` / `gwen_cg` | one character design, same cat-motif top; **2D cel vs 3D CG** | style, character | tight — **the direct test of tie-break 3**: the idiom should move `western toon` → `dimensional toon` while the character holds |
| titans | `titans1` / `titans_go` | same five characters; **anime-leaning vs chibi-stylised western toon** | style | tight — **the proportion-band probe** the session-12 gap asked for |
| gordon-era | `gordon_1996` / `gordon_2004` | one character, one idiom; 90s cel vs 2000s digital production | style | **DEAD for `style` as of session 17** — both are now `2D cel / none`, so there is nothing left to separate. It was the corpus's tightest era pair and the vocabulary no longer asks the question. Still live for `character` (one character, two eras of design) |
| lincoln | `lincoln_photo` / `lincoln_money` | same face, same era; albumen photograph vs line engraving | style, character | tight — an object *containing* a portrait, so `[[SUBJECT_KIND]]` is a live question |
| destroyer | `destroyer_photo` / `destroyer_drawing` | same warship class; archival photo vs technical plate | style, object | tight, and **the only media pair with no person in it** |
| p6-window | `window` + `p6_first` + `p6_last` | one window, **three** framings and exposures | setting | tight — the widest same-place spread. **Reframing costs more than relighting**; this pair agrees less well than `city-*` |
| p1 | `p1_first` / `p1_last` | same room, very different exposure | setting | secondary atmosphere probe (exposure, not time of day) |
| door | `door_first` / `door_last` | same corridor and door; **shut and empty → open, with a room and a man revealed** | frame describer, FL2VA delta | **the corpus's largest single-shot change**, and its most useful failure case — see below |
| kasia (swimsuit) | `kasia_swimsuit` → `_worn` / `_render` | one garment: flat, worn in 2D, worn in 3D | object, character | flat-to-worn; the flat-lay is *derived* from the 2D image, so not independent evidence |
| kasia (everyday) | `kasia_outfit` → `kasia_render` / `kasia` | flat-lay garments ↔ worn | object | same derivation caveat |
| bag-angle | `kasia_bag` / `kasia_bag_2` | one object, two angles, two renders | object | harder than `car-angle` — an AI re-render, strap arranged differently |
| peter-griffin | `peter_griffin_painting` / `peter_griffin_toon` | one character: canonical flat toon vs painterly | style | tests franchise recognition **without a label** |
| oil-idiom | `ayanami_oil` / `woman_oil` | oil idiom, **digital vs traditional** | style | fine `[[MEDIUM]]` discrimination |
| stopmo-sub | `gromit`/`gumby` (clay) · `rudolf`/`pjs`/`coraline1`/`coraline2`/`april_1987_figure`/`laika`/`skellington`/`lego1`/`lego2` (figure) | one coarse medium, **two sub-terms** as of session 17 | style | the `[[SUB_MEDIUM]]` discrimination set, and it narrowed twice. **Clay vs puppet is NOT unmistakable** — s15 disproved that: the describer inverted `gromit` and `pjs`, and the user misread `pjs` too. It is decidable, but only via the deformation tell written into the `clay` definition. **`puppet` vs `figure` was not decidable at all**, and session 17 merged them, which is why `figure` went from one atypical sample to five. What remains is a single question — *does the surface show evidence of remodelling, or is it fabricated and rigid?* — and that is the discrimination this set now tests |
| toon-era | `ivy_toon` / `peter_griffin_toon` | `2D cel / western toon`, **90s cel vs modern flat digital** | style | fine discrimination *below* the sub-term — nothing in the vocabulary separates these two. **Superseded by `gordon-era`**, which the vocabulary can express |
| azumanga | `azumanga_anime` / `azumanga_toon` | **two** shared characters (the third differs), same uniforms; flat anime cel vs western TV-toon | style | **PROMOTED session 17 — it is the sharpest `anime` vs `western toon` probe in the corpus**, not the loose one it was filed as. Both are flat 2D, so medium cannot help; the idiom is carried entirely by proportion, eye construction and background treatment |
| anime-toon | `avatar_1` / `avatar_2` / `boondocks` / `titans1` | **western production, anime idiom** — the convergence cases | style | not a control but a **test set**: these carry the provisional `western toon` ruling. Read "Rulings that may need revisiting" before scoring |
| feature-2d | `beauty_beast` / `pocahontas` / `fern_gully` (vs `ivy_toon`) | 2D theatrical features against a 90s TV cartoon | style | **negative control** — these must NOT be distinguished from `ivy_toon`; the conflation is deliberate |
| coraline | `coraline1` / `coraline2` | same character; figure on a blank ground vs film still | style, character | loose; doubles as isolated-subject vs in-scene |
| bird | `bird_vector` / `bird_watercolor` | a blue-and-orange bird | style | loose — not the same bird, the same *idea* of one |
| annie | `annie1` / `annie2_cropped` / `annie3_panel1` | one character across **three** media: marker sketch, watercolour, comic | style, character | loose, wide spread. **Requires a `SUBJECT:` line** — see below |
| april | `april_1987` / `april_1987_figure` / `april_comic` / `april_fanart` | one character across **three** media: 2D cel, photographed plastic figures, and marker twice — `april_comic` on a comic cover, `april_fanart` composited over a manhole cover | style, character | loose. **No longer the widest medium ladder** — `april_fanart` was corrected from `painting / digital` to `drawing / marker` in s15, which collapsed the fourth rung. The pair it created is arguably more useful than the rung it lost: **same instrument, different presentation**, which is a discrimination nothing else in the corpus tests. **Requires a `SUBJECT:` line** — three of the four have other characters in frame |
| gordon | `gordon_1996` / `gordon_2004` / `gordon_comic` | one character across **two** media as of session 17: `2D cel` twice, then `comic` | style, character | loose, and it lost a rung when `2D cel`'s sub-list was emptied — the `gordon-era` pair inside it is now dead for `style` |
| car-interior | `car_interior_photo` / `_sketch` / `_mecha_driver` / `_toon` | one setting *type* across **four** media; `_toon` is the only night one | setting | loosest — different vehicles |
| age-family | `baby_middle_aged` / `maggie_grandpa_cat` | an infant and an older adult together, **photograph vs flat toon** | character | the age-bracket probe: `infant` and `older adult` in two media, plus an animal in one |
| p4 | `p4_first` / `p4_last` | same street, both heavy bokeh | setting | low-information stress case |
| jacket | `jacket` / `jacket2` | same snowy park, same woman, same puffer jacket | character, object, setting | **weak for setting** — the snow is near-featureless, so durable content is thin by nature. Solid as the garment/identity pair |
| temple | `temple_day` / `temple_night` | same architecture, signage-free, **but ruined in one** | setting | **negative control** — the place really did change; see below |
| classroom | `classroom1` vs `classroom2` (+ `comic_panel4`, `classroom_anime_empty`) | *different* rooms of the same type | setting | **negative control** — must NOT collapse into one record. `comic_panel4` is a third and `classroom_anime_empty` a fourth, each in a different medium; the anime one is also **empty**, so a describer that invents occupants has nowhere to hide |
| comic-page | `comic_panel3` / `comic_panel4` | same room, two panels, one comic medium | setting | the only same-place pair inside a drawn medium |
| comic-page | `comic_panel2` / `comic_panel4` | same girl, two framings, one medium | character | the comic analogue of the `p6` wide/close pair. **Her name is printed in the balloon** — the harshest no-name probe we have |
| char-drift | `pancakes` × several `SUBJECT:` wordings | **the image itself** — isolates prompt-side instability with image variation removed | character | produced byte-identical `[[APPEARANCE]]` lines; read this before any cross-image probe |
| setting-boundary | `bookshop` | camera outside, interior visible through the glass | setting | `[[SETTING_KIND]]` boundary case — correct in every round so far |
| grass-anime | `grass_anime_scenery` / `grass_anime_girl` | **one shot, figure absent vs present** — same meadow, sky, flowers, same frame edge artefact | style | **exact on the figure axis.** The control the v4c figureless defect needs, and the strict control for its partner's medium accept-set |
| ghibli-ref | `ghibli_painting_reference_anime` / `ghibli_painting_reference_painterly` | one composition: **gouache anime BG vs a digital painterly study made from it** | style | **exact.** Moves on **two** axes — `2D cel → painting` *and* `anime → realist` — so unlike `gwen` neither field is held constant. **Both sides strict**; exempt from the figureless accept-set, see below |
| saber-ref | `saber_reference_photo` / `_anime` / `_painterly` | one pose across photograph → digital painting → digital painting | style, character | **exact** on pose and framing. The two paintings share `painting / digital` and differ **only on `[[IDIOM]]`** — the mirror of `gwen`, which moves the medium and holds the character |
| uniform-ref | `uniform_reference_photo` / `_anime` / `_painterly` | as `saber-ref`; a girl on a farm track | style, character | **exact.** Same idiom-isolating structure |
| blonde-ref | `blonde_reference_photo` / `_painterly` | one studio pose: photograph → digital painting | style, character | **exact.** Idiom held (`realist`), medium moves |
| woman-ref | `woman_reference_photo` / `_sketch` | one portrait: photograph → **graphite pencil** | style, character | **exact.** Moves medium *and* treatment (`colour → monochrome`) with idiom held |
| fruit-ref | `fruit_reference_photo` / `_sketch` | one still life: photograph → **graphite pencil** | style, object | **exact.** Only the **second** medium pair in the corpus with no person in it, after `destroyer` — and unlike `destroyer` it is colour on one side, so it tests colour→monochrome without a period-photography confound |
| simpsons-room | `simpsons_couch_toon` / `maggie_grandpa_cat` | **the same living room in two framings** — same brown three-seat couch, purple side table with books beneath, purple lamp, sailboat picture, pleated wall lamp, concentric-oval rug. Near-minimal on **object presence**: the empty frame has a teal telephone and a television and **no people**; the occupied frame has a litter tray, chips and a dip jar, **two figures with garments**, and no telephone | object, setting, character | **the corpus's only object-presence pair**, found by the user in session 22. Two uses nothing else supports. (1) A **hard `[[SUBJECT NOT FOUND]]` probe**: naming the telephone against the occupied frame asks for a thing genuinely absent that nonetheless belongs in that room and sits in the sibling shot, so confabulation is actually tempting — unlike a bicycle against a kitchen. (2) An **occlusion drift pair** on the couch: once clear, once with two figures and a cat on it. Both directions ran in session 22 and **they split** — the telephone probe passed, the garment probe (`the slippers`, against the empty room) confabulated. **The couch is `brown`** (user ruling, session 22); the describer has answered `mustard-yellow` for it once, which is the colour-drift defect on `.claude/TODO.md`, not a second opinion to be adopted |
| misato-car | `misato_car_real` / `_1` / `_2` / `_technical_print` | **one vehicle across four media** — photograph, 2D cel ×2, technical print | style, object | loose (different angles and settings). **The corpus's first object medium-ladder**; `april` is a character ladder and `destroyer` only two rungs. `_1`/`_2` inside it are the cel analogue of `car-angle` |
| garden-daynight | `backyard_anime` / `garden_pond_anime` | one Japanese garden, **day vs night** | setting | loose — **relighting and reframing move together**, so it is harder than `p6-window`. The first day/night pair in an anime medium |
| wayne-age | `wayne_knight_jurassic_adult` / `wayne_knight_older_adult` | **one real person ~30 years apart**, `adult` → `older adult` | character, style | loose. The live-action counterpart to `gordon-era`, and unlike that pair it is still live for `style` too (`live-action film` vs `photograph`) |
| jurassic | `sam_jackson_jurassic_middle_aged` / `wayne_knight_jurassic_adult` | two characters, one production, one interior type | character, setting | loose |
| lego | `lego1` / `lego2` | one material: a built set with five figures vs a single figure on a plain street | style, character | loose. Both are `stop-motion / figure`, so this is a consistency check rather than a discrimination |
| sketch | `sketch_boat` / `sketch_man` / `sketch_woman` | one instrument (graphite): a landscape, a loose study, a finished portrait | style | loose. The `drawing / pencil` sample set, and a **finish** spread — the axis `supergirl` turned out to be about, which nothing else tests deliberately |
| age-bracket | `toddler` · `boo_toddler` · `rugrats` · `pre-teen1` · `hermione_preteen` · `riley_preteen` · `will_preteen` · `couple_middle_aged` · `third_rock` | the age brackets, deliberately **spread across media** | character | not a control but a **coverage set** — a bracket must not be learnable from one medium's conventions |
| scale-samecar | `toy_car_minuscule` / `smart_car_large` | **one car model, real and as a die-cast toy** — same body shape, same red-over-black livery, same tridion cell. Nothing varies but physical size | object | **exact.** The size-ladder control: five rungs apart (`minuscule` vs `large`) on near-identical subjects |
| scale-ladder | the 16 `s24` files, `toy_car_minuscule` → `car_mountain_colossal` | subject family held near-constant (almost all red vehicles) while size runs the whole ladder | object | loose **by design** — the uniformity is the point, so that size is the only variable. Consequence: it evidences nothing about non-vehicles |
| scale-distractor | `car_building_gargantuan` / `car_mountain_colossal` | a `large` car placed against an enormous backdrop (a palace, a mountain) | object | tight. Tests that **frame share** does not drag `[[SCALE]]` up a ladder anchored on absolute adult comparison |
| text-on-object | `toy_car_small_2` / `suv_large` / `truck_huge` / `bumper_car_medium` | printed text present in every frame, in four different relationships to the described object | object | coverage, not control — text **not on** the object; brand + model designation; a bare brand; a real person's name. See § "Printed text and real-identity pressure" |

### Notes attached to specific pairs

**`city_day`/`city_night` carries a signage confound.** The skyline has rooftop bank logos and a
large neon hotel sign. Night lights those up and hides low-rise detail, so a `[[DEFINITION]]`
disagreement has two possible causes — atmosphere leaking into the durable fields, or the model
naming an illuminated sign it could not read by day. Check which before scoring. It is also the
strictest printed-text/brand probe in the corpus.

**The vector day/night pairs close the gap but are an *easier* test.** `forest_*` and `sanfran_*`
deliver "same camera, same place, same structure, relit only" perfectly — one piece of vector
artwork recoloured, zero photographic variation, zero signage. But the failure mode session 6
diagnosed was that **by day the model describes forms and by night it describes lights**, and that
happens because a real night photograph genuinely destroys information: the low-rise detail in
`city_night` is simply gone. **In a vector illustration nothing is destroyed.** A describer can
pass these comfortably while still failing `city_*`. Use them as the *diagnostic* (a failure is
unambiguous); keep `city_*` as the *bar*.

**`shed_*` is the day/night test the corpus was missing, and it beats both existing sets.** Standing
gap 1 asked for a pair that is photographic *and* signage-free; `city_*` had the photography and a
signage confound, `forest_*`/`sanfran_*` had the cleanliness but destroyed no information. The shed
series has both properties at once: no legible text anywhere in frame, and `shed_night` genuinely
loses the far houses, the fence detail and the shed's surface texture, which is the failure mode
session 6 actually diagnosed. Three states rather than two, like `sanfran_*`.

Two caveats, neither disqualifying. **The framing is handheld, not locked off** — the tree and shed
shift between frames, so this is `tight`, not `exact`; do not read small differences in what is
visible at the edges as drift. And **`shed_night` is a computational night-mode composite**: the
grass and foliage are far brighter, and smoother, than a true night exposure would render them. A
describer calling it something other than full darkness is reading the image correctly.

**`temple_day`/`temple_night` is a split diptych, not two photographs.** The user found one
artwork with the ruined/night/male half on the left and the intact/day/female half on the right,
split it down the middle and **mirrored one half** so the architecture aligns. Three consequences:
it is genuinely signage-free, which is what the gap asked for; it is **not** a clean atmosphere
control, because the building is intact in one and ruined in the other and ruin is *structural*,
so `[[DEFINITION]]` divergence is partly legitimate; and because one half was mirrored, any
left/right language in `[[STRUCTURE]]` will conflict across the pair — `setting` has no POSITION
field so this is mostly harmless, but do not read "stair rising to the right" vs "to the left" as
drift. What it *is* good for, and this is not a consolation prize: a **"same place, different
condition"** probe where the durable record *should* partly disagree. The natural negative control
for the day-and-night test.

**The annie ladder needs a `SUBJECT:` line.** `annie1` and `annie3_panel1` each contain the girl
*and* at least one costumed hero; only `annie2_cropped` has her alone. Cast across the three media
without disambiguation and the describer may legitimately record a different person in each, which
would read as catastrophic identity drift and would be nothing of the kind. Use the cropped and
panelled versions for content roles — raw `annie2` drags in a convention hall, raw `annie3` is four
scenes at once.

---

## Corrections & superseded findings

Every content error found so far, kept because each one would have changed a test verdict.
**`validate.py` cannot see any of this** — a record naming the wrong person is perfectly
well-formed and passes every structural check.

| claim | what we first recorded | what is actually true | how it surfaced | why it matters |
|---|---|---|---|---|
| `p5_first` / `p5_last` treatment | `vintage Technicolor`, the term's only two samples | **`colour`.** The term itself was **dropped from the vocabulary in session 20** — it named a *process*, not a colour system, which is the same category error that removed `archival`, and reading a dye-transfer process off pixels is a provenance call that tie-break 4 forbids everywhere else | agreed session 12, reaffirmed session 17, executed session 20 | the model never held the term: session 11 had the two frames **swapping** it between rounds, and the session-12 split lost it on *both* at once. A vocabulary entry that its only two samples cannot reach reliably is a source of noise, not signal — `p5_first` had been carrying a standing `[[TREATMENT]]` miss because of it. `[[TREATMENT]]` is now a two-term axis |
| `kiki` medium | `2D cel / digital`, read as an animation still | a **signed digital illustration** in an anime idiom, not animation artwork: soft airbrushed shading and gradient blush rather than flat cel separations, tapered stroke-weight in the hair, floating props on no ground. **Tie-break 5** ("visible drawing process beats flat colour") decides it, and the colour was never flat to begin with — `drawing / digital` | user ruling, session 16, while auditing accept-set candidates | the model had been answering `drawing / digital` and scoring a miss for it. It was **right**, and the answer key was wrong — so this was about to be forgiven by an accept-set, which would have preserved the error permanently instead of fixing it. `[[IDIOM]] anime` already carries "in the style of", which is what made `2D cel` look necessary |
| `window` age bracket, and the mathilda set generally | `window` recorded **1 teenage girl**; the other ten files of the same person recorded only "1 girl", with no bracket at all | **`pre-teen`** across all eleven. They are one person at ~12-13, so the whole set now reads `1 pre-teen girl` | user ruling, session 18, on the age audit set by `SIDE_HANDOFF_images_2.md` | the eleven files span three probe sets (`girl-painting`, `p2`/`p3`/`p4`, `p6-window`). A bracket recorded on one and absent from the rest meant a describer could be scored inconsistently on the same person, and `window` was scored against a bracket the other ten did not share. It also closes `pre-teen`, previously recorded as untested |
| `saber_reference_anime` medium | `painting / digital`, read as a very polished digital painting | **`3D CG / none`** — a 3D render. Under magnification the hair reads as rigid geometry rather than painted strands, the neck bow, the stacked bowls and the table edge all carry render shading, and the background softening is true depth of field rather than painted blur | the s19 round: the model answered `3D CG` and scored a miss for it; user ruling on adjudication, session 19 | the **third** time the model was right and the key was wrong (after `kiki` and `window`), and the second time an accept-set was the tempting fix. Forgiving it would have frozen the error permanently — the `kiki` shape exactly. It also changes what the `saber-ref` triplet tests: photo → 3D render → painterly, three *different* media, not two paintings and a photo |
| `window` is its own location | catalogued as an unrelated room; `p6` described as showing a *doorway* | `p6` shows a **window**, and it is the **same window** as `window.png` | user correction, session 6 | turns two unrelated images into the corpus's largest same-place set (three framings) |
| `annie1` / `annie3` cast | "1 girl, drawn twice — as herself and as a masked hero" | the masked figure is a **separate recurring character**; `annie3` has **four** distinct people | user correction, session 7a | **would have inverted a test verdict** — a describer correctly keeping them as two people would have scored as a failure |
| `kasia_swimsuit` set membership | "not part of the kasia set — nothing visual ties it to the character, only the filename" | it **is** — `kasia_swimsuit_worn` is the original commission the flat-lay derives from | second batch arrived, session 7b | closes the second-flat-to-worn-garment gap; also the source of the general lesson below |
| kasia headband hue | `kasia.png` treated as the reference, the renders as drifting | `kasia.png` is the **outlier** — three files agree on yellow, only the original is orange (hue 28–34°) | measured, then re-framed in 7b | a describer saying "orange" for `kasia.png` is right about *that image* while wrong about *the character* |
| session-6 medium tally | "16 live-action photographic" | 17 — the list under it named 17 | arithmetic, session 7a | it is what makes the session-6 total 37 |
| medium tallies vs crops | the 74-file tally excluded comic-panel crops from "comic page" but **included** `annie2_cropped` in "watercolour" | crops are files and count everywhere | recount, session 8 | the reason the tally is now generated rather than hand-maintained |
| "no medium is a singleton any more" (7b) | asserted after oil / western toon / marker board each reached 2+ | **false** — `destroyer_drawing` and `lincoln_money` were singletons before that batch and still are | recount, session 8 | under the two-level vocabulary these are `print / technical plate` and `print / engraving`, one sample each. No *coarse* term is a singleton; those two *sub*-terms are. Do not treat a `style` result on either as replicated |
| `car_1` / `car_2` medium | classified `3D CG / product render` from appearance | `photograph` — automaker press shots, per the user's provenance. **But not visually determinable** | user correction, session 8 | shifted live-action 39%→42%, and established the **`amb` category**: ground truth taken from provenance rather than appearance is not a fair test of a describer |
| `supergirl2` medium | `drawing / sketch`, described as "coloured pencil / colour sketch" | the **colour is marker, the same as `supergirl1`**; what differs is the linework, which is an un-inked pencil under-drawing. The pair differs in *finish*, not in *instrument* | user, session 9, reading both images against the style v1 and v2 rounds | the `supergirl` pair was set up as a `marker` vs `sketch` discrimination and is not one. It also exposed that the `drawing` and `painting` sub-lists mix axes — see "Medium vocabulary" |
| the four kasia flat-lay / bag files | `3D CG / product render`; briefly flagged `amb` mid-session 9 on the grounds that AI origin made photo-vs-render undeterminable | **`photograph / colour`.** All four are AI-rendered, and the user classifies them by **presentation** anyway, which is photographic | user, session 9, ruling on the full-corpus sweep | **the `amb` flag was the wrong tool here.** `amb` exists for images whose *provenance* we know and whose pixels do not match it; tie-break 4 already says to judge on presentation rather than provenance, and once that rule is applied consistently the ambiguity dissolves. It also raises whether `chair`/`car_1`/`car_2` should move the other way — the model calls all three `3D CG / product render`, which *is* the presentation read. **Unresolved, deliberately** — see the vocabulary redesign note |
| `annie1` sub-medium | `drawing / marker` | **`drawing / ink`** — the dominant, most identifying mark is brush-and-ink: thick tapering black strokes, with the colour laid in as soft wash underneath | re-read image by image during the session-10 three-axis re-derivation | it is the corpus's **only** `drawing / ink` sample. The term had zero samples and was on the TODO to "find a sample or drop"; this closes it, and `drawing / digital` takes its place as the empty term |
| `destroyer_photo` treatment | `photograph / archival`, carried over as `[[TREATMENT]] archival` | **`monochrome`** — the print is clean, well preserved or restored, and shows essentially no age: neutral grey, no sepia, no foxing, no scratches | model emitted `monochrome` in the session-10 smoke test; user ruled it defensible and the table wrong | `archival` is defined by **visible** age, so an aged-but-undamaged photograph is `monochrome`. Tie-break 5 is unchanged — it only fires when age actually shows. `archival` drops to two samples (`lincoln_photo`, `teddy_taft`) |
| `car_interior_sketch` sub-medium | `drawing / sketch` under the old vocabulary, re-derived to `drawing / pencil` in session 10 | **`drawing / digital`** — the construction lines are thin and uniform with no graphite tooth or grain; nothing on the surface imitates a physical instrument | model emitted `digital` in the session-10 smoke test; user agreed on re-inspection | the session-10 re-derivation got this one wrong and the model got it right. Tie-break 4 asks whether the *marks* read as digital, and here they do. Leaves `drawing / pencil` as an empty term, kept because graphite tooth is an unmistakable discrimination when it is present |
| `kasia` sub-term | `flat illustration`, stated flatly | the coarse term `2D cel` is solid; the **sub-term is contested** — an anime-inspired toon idiom leaning slightly western | user, session 9, after style v1 answered `anime` | a sub-term miss here is not clearly a miss. Score the coarse term only |
| `april_fanart` medium | `painting / digital`, described as "cut out on a white ground" | **`drawing / marker`**, and the image is a **composite**: a marker drawing of the figure laid over a separately-sourced manhole cover on a digital white ground. The user: *"the manhole cover looks like it was probably inserted post facto… The figure looks like a marker drawing, the manhole does not. The clean white background is obviously not a paper scan"* | user, session 15, on being shown the round's `dimensional toon` miss | recorded during the s15 enrichment pass, so it was wrong from the day it was written. It **collapses the april ladder from four media to three** — `april_comic` and `april_fanart` are now both `drawing / marker` — and the ladder's billing as "the corpus's widest" had to be retracted. Also the corpus's first acknowledged **composite**: the classification follows the *subject*, not the assembled whole |
| `coraline1` ground | "puppet cut out on white" | the file is a **palette PNG with a transparency key, 83.5% fully transparent**. It has no white ground; it has no ground at all. What reaches the model composites to **black** | the session-9 style round reported "pure black background" twice and was scored as a hallucination; the user identified transparency as the cause, confirmed by an alpha scan of the whole corpus | **a wrong ground truth was about to be recorded as a model defect.** It is the only genuinely transparent file in the corpus — six other files carry an alpha channel that is fully opaque, so they are inert |
| `chair` / `car_1` / `car_2` scorability | `amb` → **`UNSCORABLE`**: excluded from scoring entirely, permanently, because photo-vs-render is not visually determinable | still `amb`, but the flag now emits an **accept-set** `photograph \| 3D CG`. Both readings pass; everything else still fails | user, session 17, clearing every outstanding ruling before the vocabulary change | closes a question open since session 9. The exclusion was over-broad: it dropped the cases from the denominator, so a gross error on them would have registered as nothing. Scoring them against `photograph` was never an option either — that value is **provenance**, and `L-SCORE-ONLY-WHAT-THE-INPUT-SHOWS` forbids it. Deliberately a **weak** test: do not read a pass here as evidence the distinction works |
| `fish_pixel` / `lincoln_money` / `mountain_rain` idiom | three separate `CONTESTED` rulings on `[[IDIOM]]`, each recorded as its own image ambiguity | all three are `realist`, and all three failed to `flat graphic` — **one over-attractor, not three ambiguities**. `kasia_bag` and `destroyer_drawing` are already-scored misses of the same shape | user, session 17; the pattern was only visible once the three were listed together | **the excluding is what hid it.** Cases dropped one at a time are never compared with each other, so a shared failure direction stays invisible for as long as the exclusions stand. Cleared to the master value and now scoring as ordinary misses; the defect is on `.claude/TODO.md` as one named item |
| `azumanga_anime` / `azumanga_toon` cast | "same 3 schoolgirls", stated in both master rows, the contents row and the probe-pair row | **two of the three are shared**; the third differs between the images. And the recorded difference -- "flat cel, thick outline, sticker border" vs "flat toon over textured paint" -- describes SURFACE TREATMENT and misses what actually separates them: `_anime` has naturalistic body proportions and large irises with a specular glint distinct from the pupil, `_toon` has noodle limbs, oversized heads/hands/feet, small flat black pupils with no iris, and a background stylised into flat shapes | user, session 17, on being shown both images during the `western toon` vs `anime` work | **it cost a wrong design decision on the spot.** Reading the claim row rather than the pixels, I argued the pair "differs only in rendering, so a proportion rule cannot separate it" and nearly talked the user out of the very rule the corpus supports. Textbook L-CLAIM-ROWS-ARE-UNRELIABLE: a description row was reliable about uniforms and setting, a CLAIM row about cast identity and about what distinguishes the pair was not. The pair is now the corpus's sharpest anime-vs-western-toon probe rather than a "loose" one |
| `coraline1` sub-medium | `CONTESTED` — `puppet` and `figure` not distinguishable here | an **accept-set** `puppet \| figure`, with `coraline2` as the control — then **moot**, once the merge landed later the same session and both became `figure` | user, session 17 | `CONTESTED` threw away the fact that `clay` and `model` are still flatly wrong on it. Short-lived by design: it existed so the last pre-merge round could be scored against a pre-merge key. `coraline2` is *not* ambiguous the same way — a built kitchen set, fabric knitwear with visible nap, fibre hair, no toy reading available — which is why it was the control |
| `stop-motion / puppet` (the term) | a sub-term distinct from `figure`: fabric, fibre hair, sculpted painted matte surfaces, replacement-face seams | **merged into `figure`.** 4 master rows moved: `coraline1`, `coraline2`, `pjs`, `rudolf` | agreed session 12 on `coraline1`'s contested ruling; executed session 17 | the split had **no statable test** — every attempt to write one described a property both terms share. The merged term does: *fabricated and rigid*, as against `clay`'s *evidence of remodelling*. Second time this document's "unmistakable on sight" claim was falsified for a stop-motion sub-term |
| `2D cel / traditional cel` and `/ digital` (the terms) | a two-value sub-list separating hand-drawn cel animation from digital production | **both removed; `2D cel` has no sub-list.** 25 master rows moved to `none` | user, session 17, on a measured `traditional cel` recall of 2/7 with all 5 losses to `digital` | not merely undeliverable but **actively harmful to emit**: a one-value list would have asserted digital production of `april_1987` and `pocahontas` downstream to the composer. Kills the `gordon-era` probe pair and shortens the `gordon` and `april` ladders |

**The general lesson is `L-CLAIM-ROWS-ARE-UNRELIABLE`, and it is about the inventory rather than
about kasia: a "these are
unrelated" judgement is only ever true of the corpus *as it stands*.** Two of the three content
errors caught in session 7 were of this shape — an inferred *relationship*, not a described
object. **Description rows have been reliable; claim rows have not**, and claim rows are the ones
that change a verdict.

---

## Coverage by role

### `setting`

**17 distinct interiors**: 2 classrooms (+ a third in `comic_panel4`), 2 kitchens, 3 living/dining
rooms, bedroom, theatre auditorium, window room, bookshop interior, office, tiled washroom, and —
session 15 — 4 more living rooms across drawn media (`boondocks`, `gwen_cg`, `maggie_grandpa_cat`,
`titans1`), an attic bedroom (`molly`), a brick garage (`gromit`) and a diner (`gumby`).
**Plus 5 vehicle interiors** — the setting type that was entirely missing at session 6 — now
spanning photograph, drawing, anime cel and western toon, and including a night one
(`car_interior_toon`) and a motorhome (`gwen`).

**Exteriors** cover shop street, ship deck, castle grounds, snowy park, snowy hillside road, modern
city street, 1950s backlot street at night, downtown skyline from above, beech forest in fog,
alpine range in rain, volcano and thatched village, grass plain under cumulus, stylised vector
skyline, school grounds, alley, stone battery, poolside, portico, gothic temple, and — session 15 —
**a residential back garden in three lighting states** (`shed_*`), a housing-project courtyard
(`pjs`), a rocky canyon (`avatar_1`), a rainforest (`fern_gully`), a coastal headland (`nadia`),
a snowfield (`rudolf`) and a night woodland (`scooby`).

Weather: snow (×4), fog, rain, overcast, clear. Terrain: forest, rainforest, alpine rock, grass
plain, water, snowfield, and several flavours of built-up.

**Time of day** is now a first-class axis rather than an accident: `shed_*` (day/dusk/night,
photographic), `sanfran_*` (day/evening/night, vector), `city_*` and `forest_*` (day/night), plus a
run of night exteriors in drawn media (`april_1987`, `avatar_2`, `gordon_2004`, `beauty_beast`,
`scooby`, `car_interior_toon`).

**No-/low-setting cases** for "not visible" behaviour: `kasia`, `kiki`, `phone`, `chair`,
`kaypro_ii`, `car_1`/`car_2` and most product renders (plain studio grounds), `miyu` (black void).

### `object`

**In-scene targets**: CRT television (`tv`), ship's wheel (`captain`), transistor radio (`p1`),
cereal box (`p3`), frying pan (`pancakes`), leather case (`p4`), wheelie bin (`miyu`), wrought-iron
bench (`jacket2`), shoulder bag (`kasia`), breads (`kiki`), newspaper (`newspaper`), eyeglasses
(`sleeping`), 1950s cars (`p5`), cannon (`cannon`), handheld device (`ivy_toon`), holster and badge
(`woody_cg`), and — session 15 — a lettered panel van (`gromit`, `scooby`), a garden shed and
patio table (`shed_*`), a cat litter tray (`maggie_grandpa_cat`), milkshake glasses (`gumby`),
stacked pizza boxes (`april_fanart`), a printed wall chart (`gwen`), a walking cane (`pjs`) and a
heap of soft toys (`molly`).

**Articulated toys as objects** (`april_1987_figure`) are new and slightly odd: the *subject* is a
set of figures, so `object` and `style` pull in different directions on the same file. Useful for
exactly that reason.

**Isolated shots** — the thing session 6 was short of, now well covered: `phone`, `chair`,
`kaypro_ii`, `fruitbowl`, `ramen_pixel`, `fish_pixel`, `kasia_bag`, `kasia_bag_2`, `car_1`,
`car_2`.

**Garments**: plate armour (`castle`), captain's uniform (`captain`), puffer jacket
(`jacket`/`jacket2`), fedora and roller skates (`p5`), school uniforms (`classroom1`/`classroom2`,
`azumanga`), **two flat-to-worn pairs** (`kasia_outfit`, `kasia_swimsuit`), and — session 15 — a
gold ballgown and tailcoat (`beauty_beast`), leaf-and-petal costume (`fern_gully`), a trench coat
across three media (`gordon_*`), **matching pyjamas on three figures** (`molly`, which also
exercises the character describer's "the girl in the pajamas" `SUBJECT:` example) and **one yellow
jumpsuit across three media** (`april_1987`, `april_1987_figure`, `april_comic`).

**`april_fanart` deliberately breaks that run**: the same character in a *different* outfit — a
cropped yellow zip jacket and jeans, not the jumpsuit. So the april ladder tests identity across
media **and** across costume change, which is harder and more realistic than the annie ladder. A
record that carries the jumpsuit into `april_fanart` is wrong.

### `character`

**Age brackets** were the long-standing hole. Session 15 closed the worst of it: `infant`
(`baby_middle_aged`, `maggie_grandpa_cat`), `middle-aged` (`baby_middle_aged`, `gordon_2004`,
`gordon_comic`), `older adult` (`gordon_1996`, `maggie_grandpa_cat`, `pjs`). **Session 18 closed
the last two**, and every bracket now has a sample:

- **`toddler`** — `toddler` (photograph), `boo_toddler` (3D CG), `rugrats` (2D cel). Three media
  by design, so the bracket cannot be learned from one medium's conventions.
- **`pre-teen`** — `pre-teen1`, `hermione_preteen`, `riley_preteen`, `will_preteen`,
  `cleo_slingshot`, `laika`, **plus the 11-file mathilda set** (`girl_painting`,
  `girl_painting_reference`, `p2_*`, `p3_*`, `p4_*`, `p6_*`, `window`), ruled `pre-teen` as a
  block in session 18. That makes it the corpus's **best-attested** bracket, and the one most
  worth watching: eleven of its samples are the same person, so a describer that reads her one
  bracket high fails eleven cases at once and the count will look worse than the error is.
- `middle-aged` also gains `couple_middle_aged` (×2), `third_rock` (×2),
  `sam_jackson_jurassic_middle_aged`, `sketch_man`; `older adult` gains
  `wayne_knight_older_adult`.

**A finding worth keeping, from `saber-ref`.** The same subject in the same pose reads as a
different bracket depending on how it is rendered — `saber_reference_photo` is a young adult,
and `saber_reference_anime`, drawn from it, reads `teenager`. That is a property of the anime
idiom rather than a describer error, so **do not score the saber triplet as an age-consistency
set**. It is the clearest evidence in the corpus that `[[AGE]]` is a judgement about the
*depiction*, not about the person depicted.

**Skin tone** had gone unremarked as a gap until session 15 and was near-absent: the corpus was
overwhelmingly pale-skinned. Now covered across several media — `boondocks` and `pjs` (a whole
cast), `nadia` (anime), `titans1`/`titans_go`, `pocahontas`, `molly`, `avatar_2`.

**Animals** as `[[SUBJECT_KIND]]`: `maggie_grandpa_cat` (cat), `rudolf` (reindeer), `gromit` (dog),
`scooby` (dog), `nadia` (lion cub), `pocahontas` (raccoon, pug, hummingbird), `gumby` (horse).
Before session 15 the only ones were `miyu`'s and the horse in the prompt's own example, so this
axis was effectively untested against real images.

**Do not score the `gumby` horse as a miss.** Pokey is canonically a horse but is drawn heavily
stylised and anthropomorphised — upright, conversational, holding a drink. Reading him as a
generic creature, or as `person`, is defensible from the pixels alone. The same caution applies to
`gromit`'s dog, who is bipedal and wields a spanner. `[[SUBJECT_KIND]]` distinguishes person from
animal, and these two sit on the boundary by design rather than by accident.

### `style`

**No longer blocked.** 11 coarse media, **21 of 24 defined (coarse, sub) combinations
populated**; live-action down to 39% from 78%. Fourteen same-subject-across-media sets,
one of them exact. See the tally and the pairs table.

The two vocabulary decisions this section used to flag as open are **now settled** by the
tie-break rules under "Medium vocabulary":

- **The oil case** — resolved by rule 3 (report the idiom, not the substrate). `woman_oil` is
  `painting / oil`, `ayanami_oil` is `painting / digital`. They agree at coarse level and differ
  at sub level, which is exactly what that probe pair should produce.
- **The nested-medium case** — resolved by rule 2 (report the outer medium). `annie2` is
  `photograph`, with `annie2_cropped` as the clean watercolour sample. The rule generalises to
  `tv`'s CRT and to any poster, phone screen or television in frame, which is ordinary in real use.

### The three studio product shots — the `amb` category, retired

**`chair`, `car_1`, `car_2`.** They are studio product shots on a seamless white ground. The
user knows their provenance — `chair` from an Amazon listing, `car_1`/`car_2` direct from an
automaker — so they are filed as `photograph`. **The pixels do not settle it.** Contemporary
automaker press imagery is routinely CGI, and a clean e-commerce shot on white is exactly where
a photograph and a good product render converge.

They are scored as an **accept-set**, `photograph | 3D CG` on `[[MEDIUM]]`. Both readings pass;
`painting`, `drawing`, `vector` and the rest still fail. Two reasons that beats the
alternatives that were on the table:

- **Scoring them against `photograph` was never legitimate.** That value comes from knowledge of
  the *source*, not from the pixels, and `L-SCORE-ONLY-WHAT-THE-INPUT-SHOWS` forbids scoring a
  describer against information it was never given. The table is right about the world and wrong
  about what is *askable*.
- **`UNSCORABLE` threw away too much.** It removed the cases from the denominator entirely, so a
  gross error — `painting`, say — would have registered as nothing at all.

**It is deliberately a WEAK test.** Both plausible answers pass, so a pass here is not evidence
the photo-vs-render distinction works. Controls guard the direction it erodes: `photograph` is
the forgiven side, so unambiguous `3D CG` (`fruitbowl`, `shrek_cg`, `woody_cg`) must still come
back `3D CG`.

**And one thing survives regardless:** `[[MEDIUM]]` may be undecidable on a file, but **two
views of one object disagreeing with each other is still a real failure.** They must land in the
same place, whatever that place is. `car_1`/`car_2` passed that; the kasia bags did not.

#### What changed, and when

| session | change |
|---|---|
| 7–9 | category created as a flag; the model answered `3D CG / product render` every round |
| 9 | the four kasia flat-lay/bag files were flagged `amb`, then **reclassified `photograph`** — tie-break 4 judges on presentation rather than provenance, and applying it consistently *dissolves* the ambiguity rather than cataloguing it |
| 17 | ruled scorable: the flag emits an **accept-set** rather than `UNSCORABLE` |
| 18 | user direction: **stop using `amb`**; new ambiguity rulings go straight to `_expected` (the figureless-plate set was the first) |
| 19 | **flag retired entirely.** These three became ordinary `ACCEPT_MEDIUM` entries in `scripts/gen_style_sweep.py`, `amb` was removed from `inventory.py`'s `FLAGS` and from its tally footnote, and `tests/describer_style_sweep130.json` was verified to regenerate **byte-identically** — which is what proved the migration did not disturb the baseline |

The `why`/`control` text was carried across **verbatim**: it is the record of a real session-17
ruling, and rewording it would have quietly changed what a future reader thinks was decided.

## Multi-panel images — a trap to know, not to defend against

`comic` (5 panels), `annie3` (4 panels), and the two day/night composites are single files
containing several scenes; `annie2` is a photograph of a painting held in a hand. Every describer
built so far assumes one frame, one place, one moment, so `[[SETTING_KIND]]` has no correct answer
for any of them.

**Agreed approach**: crop panels for the content roles, keep the full pages for `style`, and run an
uncropped page through `setting` **once, as a diagnostic that is recorded and never patched.**

The reasoning is this project's own most expensive lesson, `L-OPTIONAL-JUDGEMENT-IS-A-LIABILITY`
(see `.claude/lessons_learned.md`). `[[SUBJECT NOT FOUND]]` cost three
rounds and caused *every* format failure in setting v1–v3 before it was deleted, and the conclusion
was that **an optional behaviour that fires on judgement is a liability unless the role genuinely
needs the judgement**. Multi-panel handling is that trap in a new costume: if a comic page produces
mush, the reflex is to add an "if the image contains multiple panels…" rule, and that rule will
cost us elsewhere the way the setting-v2 paragraph did.

Both composites are kept alongside their crops — they cost nothing, they are the provenance, and
they are a second kind of multi-panel diagnostic where the panels are the *same* scene rather than
a sequence.

---

## Printed text and real-identity pressure

**Printed text, hardest first**: `lincoln_money` (almost nothing but text) · `destroyer_drawing`
(class name, dimensions, tonnage, date) · `kaypro_ii` (brand on the case *and* rendered on the
screen) · `chips_hotdog_dr_pepper_painting` (**three** brands, hand-painted, so the text is part of
the brushwork) · `comic` / `annie3` / `comic_panel2` / `annie3_panel1` (dialogue balloons **plus a
character's name**) · `supergirl2` (hand-lettered title) · `car_interior_photo`, `car_1`, `car_2`
(maker emblem) · `car_interior_mecha_driver` (Japanese cover text) · `coraline2` (a mug slogan) ·
`van_pixel` (licence plate) · `annie1` (signature, seal, name in two scripts) · `girl_painting` (a
Weibo watermark) · `kasia_swimsuit_worn` (a commission credit) · `cloud` (artist signature and a
repeating watermark) · `miya` (printed title) · `p2`/`p3` (brand text on a box).

**Session 15 adds two kinds of text pressure the list above did not have:**

- **Text composited *over* the artwork rather than existing inside it** — `pjs` (a title logo laid
  across the lower frame), `nadia` (a title and a two-line tagline), `beauty_beast` (a
  `disneyscreencaps.com` site watermark), `april_comic` (printed publisher trade dress, issue
  number and creator credits framing hand-drawn art). These are the sharpest test of the
  "never repeat a watermark, title or signature" rule, because the text is **the most legible thing
  in the frame** and is not part of the depicted scene at all. `cloud` and `girl_painting` were the
  only prior examples and both are faint.
- **Diegetic text a describer legitimately *should* mention** — `gwen`'s `VACATION SCHEDULE` chart
  is the subject of the scene; `gromit`'s van lettering and `scooby`'s `THE MYSTERY MACHINE` name
  the object carrying them. The rule forbids repeating text as *identification*, not noticing that
  a van has lettering on it. **These two groups pull in opposite directions in the same batch**,
  which is exactly what makes them worth having.

**Real identifiable people**: `lincoln_photo` + `lincoln_money` (the same man twice across two media
— the strongest identity probe we have), `teddy_taft` (two at once), `girl_painting_reference` (a
well-known actor, and the source of `girl_painting`). **Real place**: `fuji` — the first real test
of the no-real-place-names rule.

**`shed_*` are the user's own photographs.** They contain no legible text and no people, and the
description here is deliberately generic — a residential back garden, no location. `docs/` is
published; the images are not tracked. Keep it that way.

**Recognisable fictional characters**: coraline ×2, supergirl ×2, azumanga ×2, annie ×3 + 2 crops,
`comic`, peter_griffin ×2, `kasia`, `kiki`, `miya`, `miyu`, `ivy_toon`, `shrek_cg`, `woody_cg`,
`ayanami_oil`, and **21 more from session 15** — the april, gordon, gwen, titans and avatar sets,
`beauty_beast`, `pocahontas`, `fern_gully`, `boondocks`, `molly`, `nadia`, `scooby`, `gromit`,
`gumby`, `rudolf`, `pjs`, `maggie_grandpa_cat`, `car_interior_toon`. Franchise pressure is now the
corpus's **majority condition** rather than a special case, which is worth knowing before reading
any no-franchise-name result: a describer that leaks names will now leak them often.

Three cases are nastier than the rest:

- **`peter_griffin_painting`** — instantly recognisable but rendered in a medium the source never
  uses, so naming the franchise requires *recognition* rather than *reading a label*. With
  `peter_griffin_toon` now present, the canonical version is there for comparison.
- **`ivy_toon`, `shrek_cg`, `woody_cg`** — instantly recognisable licensed characters with **no
  text anywhere in frame**, across three more media. The no-franchise-name rule is now testable
  purely on recognition.
- **`annie1` and `annie3` mix an original character with licensed ones.** The girl is the artist's
  own; the masked hero beside her is not. A describer can therefore fail *partially* — correct and
  neutral about the girl, franchise-naming about the figure next to her — which is more realistic
  than an image where everything is licensed or nothing is.

---

## Known describer limitations this corpus exercises

- **An empty space that is about to be occupied invites invention — and `door_first` triggers it
  reliably.** That frame contains no person at all: a corridor, a shut door, a lit gap at the
  hinge. It has repeatedly produced a described person who is not there. It is the opening frame
  of a shot whose closing frame *does* contain a man, and the composition carries that prior.

  This is `L-CAPABILITY-CEILINGS`' "compound environmental reversal (empty → occupied space)"
  seen from the other side, and **`door_first` is the only reliable trigger for it in the
  corpus.** The pair was nearly deleted in session 8 as a superseded duplicate; it is kept
  precisely *because* it fails consistently. A reproducible failure is worth more than a clean
  pass — see `L-NAME-THE-CASE`, and note that `L-ONE-RUN-IS-A-SAMPLE` makes reproducible
  failures rare and valuable here.

  **Not yet run under the current describers.** The hallucination was observed during earlier
  FL2VA work, before the frame describer reached v8. Re-running it is on the TODO.
- **Dim and occluded scenes degrade object-state reading.** `miyu` (pixel art, heavily occluded)
  produced invention where "not visible" was wanted.
- **Reframing costs more than relighting.** The `p6` wide/close set agrees less well than the
  `city` day/night pair. A tighter shot simply contains less place — worth knowing before trusting
  any single frame as an environment reference.
- **Some disagreement is in the source, not the describer.** The `p4` girl is genuinely borderline
  (~12–13, on the child/pre-teen/teenager boundaries); the kasia bag differs in hue *and* pin
  badges between files. Do not chase these as prompt defects.
- **The city day/night gap may be irreducible.** The day record names gold cladding and a copper
  roof the night image genuinely does not show. That is a limit of the photograph.
- **Residual leaks accepted, not chased**: a cereal carton in `p3` survives the movable-clutter ban
  and is still described as having "green lettering" — the brand name is suppressed, the fact of
  text is not.

---

## Derived files & provenance

Gutters were detected **programmatically** (row/column runs of ≥97%-white pixels, then per-band
column analysis), not estimated by eye. All comic crops exclude the panel border rules with no
bleed from neighbours.

| crop | source | geometry | size |
|---|---|---|---|
| `comic_panel2` | `comic` top-right panel | — | 335x429 |
| `comic_panel3` | `comic` middle panel | — | 1161x460 |
| `comic_panel4` | `comic` bottom panel | — | 1249x904 |
| `annie3_panel1` | `annie3` leftmost panel | — | 428x1434 |
| `annie2_cropped` | `annie2`, hand + sketchbook edge + hall removed | — | 722x1273 |
| `forest_day` | `forest_day_night` | rows 0–739 | 947x739 |
| `forest_night` | `forest_day_night` | rows 742–1480 | 947x738 |
| `sanfran_day` | `san_fransisco_day_evening_night` | rows 0–487 | 1039x487 |
| `sanfran_evening` | same | rows 495–982 | 1039x487 |
| `sanfran_night` | same | rows 993–1480 | 1039x487 |

**The San Francisco composite has clean white gutters** (rows 487–495, 982–993). **The forest
composite has none** — the two panels butt directly and the seam was found from the row-to-row
brightness discontinuity, unambiguous at row 741 (mean brightness 102.8 → 24.7). One or two seam
rows are trimmed from each side; both crops were checked visually and carry no edge artefact.

**Panels deliberately not kept**: `comic` panel 1 (a hand and a spider — no usable setting or
subject) and `annie3` panels 2–4 (costumed figures on flat grounds; the corpus already has plenty
and they add no new probe). The crop boxes are in the session-7 handoff if any are wanted later.

**`annie2` is kept whole *and* cropped, deliberately** — the two files serve different jobs and
cannot confound each other. Uncropped is the corpus's only nested-medium case; cropped is a clean
traditional watercolour sample and the annie ladder's watercolour rung, free of the hand and hall
that would otherwise contaminate a character record.

### File-format gotchas found while reading

- **`coraline2.jpg` was not a JPEG** — an AVIF file with a `.jpg` extension. `run_tests.py`'s
  `image_payload()` maps extension to MIME with **no sniffing**, so it would have sent AVIF bytes
  labelled `image/jpeg`. Converted to `coraline2.png` (PIL, lossless re-encode of the decoded
  pixels) and the bad `.jpg` deleted. **If more images arrive from hosts that serve AVIF/WebP
  behind a `.jpg` URL, check the magic bytes before casting them.** A one-line guard in
  `image_payload()` is cheap insurance — on the TODO.
- **`cannon.JPG` was an MPO**, not a plain JPEG — a 2-frame stereo pair from a 3D camera,
  4320x3240, 6.3 MB (~8.4 MB base64, 5× the pixel count of anything else). Frame 0 extracted,
  Lanczos-resized to 2000x1500, saved as JPEG q90 → `cannon.jpg`, 0.99 MB. Visually identical. The
  original was marked read-only, which had to be cleared first.
- **`coraline1.png` is transparent, and transparency is not a neutral background.** It is a
  palette PNG carrying a `tRNS` transparency key, **83.5% fully transparent**. Viewed in most
  image tools it appears cut out on white; `run_tests.py` base64-encodes the **raw file bytes**
  and lets the server-side decoder flatten it, and that composites to **black**. A naive
  `Image.open(...).convert('RGB')` gives `(0, 0, 0)` at the corner, which is what the model
  reported.

  Two consequences worth carrying:

  1. **What we see in a viewer is not necessarily what the model receives.** Any ground-truth
     claim about a background on a transparent file is a claim about our viewer, not about the
     input. This is `L-SCORE-ONLY-WHAT-THE-INPUT-SHOWS` arriving from an unexpected direction —
     the mismatch was in the pipeline rather than in the provenance.
  2. **The corpus was scanned and `coraline1` is the only offender.** `azumanga_anime`,
     `car_interior_mecha_driver`, `car_interior_sketch`, `kiki`, `miyu` and `peter_griffin_toon`
     all carry an alpha channel whose minimum value is 255 — fully opaque, so they flatten
     identically whatever the decoder does. No earlier round is affected: no transparent file
     was in the `setting` or `character` test sets.

  Re-run the scan if images arrive from sources that ship cut-outs (product shots, sprite
  sheets, wiki renders):

  ```bash
  python -c "from PIL import Image; import pathlib; [print(p.name, Image.open(p).convert('RGBA').getchannel('A').getextrema()) for p in pathlib.Path('images').iterdir()]"
  ```

  **Left as-is rather than flattened**, pending a decision: flattening onto white would match how
  we read it, but the black ground is a legitimate input and `coraline1` is a `style` and
  `character` fixture where the ground barely matters. See `.claude/TODO.md`.
- **`teddy_taft.JPG` had an uppercase extension** — Harmless today
  (`image_payload()` should lowercase before mapping) but worth normalising.

---

## Medium tally

**Generated by `scripts/inventory.py` — do not hand-edit.** Counted over every active file,
crops included; the footnote markers below are driven by the master table's `flags` column, so
they stay attached to the right rows automatically. Run `python scripts/inventory.py` after any
change to the master table.

| medium | sub | count | images |
|---|---|---|---|
| `photograph` | — | **61** | airliner_gargantuan, annie2\*\*, baby_middle_aged, blonde_reference_photo, bookshop, bumper_car_medium, cannon, captain, car_1, car_2, car_building_gargantuan, car_interior_photo, car_mountain_colossal, castle, chair, city_day, city_night, classroom1, classroom2, couple_middle_aged, destroyer_photo, forest_autumn, fruit_reference_photo, fuji, jacket, jacket2, kasia_bag, kasia_bag_2, kasia_outfit, kasia_swimsuit, kaypro_ii, lincoln_photo, misato_car_real, newspaper, pancakes, phone, pre-teen1, saber_reference_photo, shed_day, shed_dusk, shed_night, ship_gargantuan, sleeping, smart_car_large, stage, suv_large, teddy_taft, third_rock, toddler, toy_car_minuscule, toy_car_modest_1, toy_car_modest_2, toy_car_small_2, toy_car_tiny_1, toy_car_tiny_2, truck_huge, tv, uniform_reference_photo, van_huge, wayne_knight_older_adult, woman_reference_photo |
| `live-action film` | — | **20** | door_first, door_last, girl_painting_reference, hermione_preteen, p1_first, p1_last, p2_first, p2_last, p3_first, p3_last, p4_first, p4_last, p5_first, p5_last, p6_first, p6_last, sam_jackson_jurassic_middle_aged, wayne_knight_jurassic_adult, will_preteen, window |
| `3D CG` | — | **9** | boo_toddler, fruitbowl, gwen_cg, kasia_render, kasia_swimsuit_render, riley_preteen, saber_reference_anime, shrek_cg, woody_cg |
| `stop-motion` | | **11** | |
| | figure | 9 | april_1987_figure, coraline1, coraline2, laika, lego1, lego2, pjs, rudolf, skellington |
| | clay | 2 | gromit, gumby |
| | *model* | *0* | *no sample* |
| `2D cel` | — | **49** | april_1987, avatar_1, avatar_2, azumanga_anime, azumanga_toon, backyard_anime, beauty_beast, boondocks, car_interior_mecha_driver, car_interior_toon, classroom_anime_empty, cleo_slingshot, fern_gully, garden_pond_anime, ghibli_grass, ghibli_kitchen, ghibli_painting_reference_anime, ghibli_street, gordon_1996, gordon_2004, grass_anime_girl, grass_anime_scenery, gwen, ivy_toon, kasia, kasia_swimsuit_worn, maggie_grandpa_cat, misato_car_1, misato_car_2, miya, molly, nadia, nerv, pavilion_anime, peter_griffin_toon, pocahontas, pooh, river_mountain_anime, roadway_toon, room_anime, rugrats, scooby, shoes_anime, simpsons_couch_toon, spongebob_tree_toon, temple_grounds_anime, titans1, titans_go, town_tower_anime |
| `comic` | | **7** | |
| | ink | 4 | comic, comic_panel2, comic_panel3, comic_panel4 |
| | digital | 3 | annie3, annie3_panel1, gordon_comic |
| | *screentone* | *0* | *no sample* |
| `painting` | | **16** | |
| | digital | 12 | ayanami_oil, blonde_reference_painterly, cloud, ghibli_painting_reference_painterly, girl_painting, mountain_rain, peter_griffin_painting, saber_reference_painterly, temple_day, temple_night, uniform_reference_anime, uniform_reference_painterly |
| | oil | 2 | chips_hotdog_dr_pepper_painting, woman_oil |
| | watercolour | 2 | annie2_cropped, bird_watercolor |
| `drawing` | | **13** | |
| | marker | 5 | april_comic, april_fanart, marker, supergirl1, supergirl2 |
| | pencil | 5 | fruit_reference_sketch, sketch_boat, sketch_man, sketch_woman, woman_reference_sketch |
| | digital | 2 | car_interior_sketch, kiki |
| | ink | 1 | annie1 |
| `vector` | — | **10** | bird_vector, forest_day, forest_day_night, forest_night, san_fransisco_day_evening_night, sanfran_day, sanfran_evening, sanfran_night, toy_car_small_1, vector_city |
| `pixel art` | — | **4** | fish_pixel, miyu, ramen_pixel, van_pixel |
| `print` | | **3** | |
| | halftone | 2 | destroyer_drawing, misato_car_technical_print |
| | engraving | 1 | lincoln_money |

### `[[IDIOM]]` tally

| idiom | count | images |
|---|---|---|
| `realist` | **103** | airliner_gargantuan, annie2\*\*, april_fanart, baby_middle_aged, bird_watercolor, blonde_reference_painterly, blonde_reference_photo, bookshop, bumper_car_medium, cannon, captain, car_1, car_2, car_building_gargantuan, car_interior_photo, car_mountain_colossal, castle, chair, chips_hotdog_dr_pepper_painting, city_day, city_night, classroom1, classroom2, couple_middle_aged, destroyer_drawing, destroyer_photo, door_first, door_last, fish_pixel, forest_autumn, fruit_reference_photo, fruit_reference_sketch, fruitbowl, fuji, ghibli_painting_reference_painterly, girl_painting, girl_painting_reference, gordon_comic, hermione_preteen, jacket, jacket2, kasia_bag, kasia_bag_2, kasia_outfit, kasia_swimsuit, kaypro_ii, lincoln_money, lincoln_photo, misato_car_real, misato_car_technical_print, mountain_rain, newspaper, p1_first, p1_last, p2_first, p2_last, p3_first, p3_last, p4_first, p4_last, p5_first, p5_last, p6_first, p6_last, pancakes, phone, pre-teen1, ramen_pixel, saber_reference_painterly, saber_reference_photo, sam_jackson_jurassic_middle_aged, shed_day, shed_dusk, shed_night, ship_gargantuan, sketch_boat, sketch_man, sketch_woman, sleeping, smart_car_large, stage, suv_large, teddy_taft, third_rock, toddler, toy_car_minuscule, toy_car_modest_1, toy_car_modest_2, toy_car_small_2, toy_car_tiny_1, toy_car_tiny_2, truck_huge, tv, uniform_reference_painterly, uniform_reference_photo, van_huge, wayne_knight_jurassic_adult, wayne_knight_older_adult, will_preteen, window, woman_oil, woman_reference_photo, woman_reference_sketch |
| `anime` | **42** | annie1, ayanami_oil, azumanga_anime, backyard_anime, car_interior_mecha_driver, car_interior_sketch, classroom_anime_empty, cloud, comic, comic_panel2, comic_panel3, comic_panel4, garden_pond_anime, ghibli_grass, ghibli_kitchen, ghibli_painting_reference_anime, ghibli_street, grass_anime_girl, grass_anime_scenery, kasia, kasia_render, kasia_swimsuit_render, kasia_swimsuit_worn, kiki, marker, misato_car_1, misato_car_2, miya, miyu, nadia, nerv, pavilion_anime, river_mountain_anime, room_anime, saber_reference_anime, shoes_anime, temple_day, temple_grounds_anime, temple_night, town_tower_anime, uniform_reference_anime, van_pixel |
| `flat graphic` | **10** | bird_vector, forest_day, forest_day_night, forest_night, san_fransisco_day_evening_night, sanfran_day, sanfran_evening, sanfran_night, toy_car_small_1, vector_city |
| `western toon` | **31** | annie2_cropped, annie3, annie3_panel1, april_1987, april_comic, avatar_1, avatar_2, azumanga_toon, beauty_beast, boondocks, car_interior_toon, cleo_slingshot, fern_gully, gordon_1996, gordon_2004, gwen, ivy_toon, maggie_grandpa_cat, molly, peter_griffin_toon, pocahontas, pooh, roadway_toon, rugrats, scooby, simpsons_couch_toon, spongebob_tree_toon, supergirl1, supergirl2, titans1, titans_go |
| `dimensional toon` | **17** | april_1987_figure, boo_toddler, coraline1, coraline2, gromit, gumby, gwen_cg, laika, lego1, lego2, peter_griffin_painting, pjs, riley_preteen, rudolf, shrek_cg, skellington, woody_cg |

### `[[TREATMENT]]` tally

| treatment | count | images |
|---|---|---|
| `colour` | **193** | airliner_gargantuan, annie1, annie2\*\*, annie2_cropped, annie3, annie3_panel1, april_1987, april_1987_figure, april_comic, april_fanart, avatar_1, avatar_2, ayanami_oil, azumanga_anime, azumanga_toon, baby_middle_aged, backyard_anime, beauty_beast, bird_vector, bird_watercolor, blonde_reference_painterly, blonde_reference_photo, boo_toddler, bookshop, boondocks, bumper_car_medium, cannon, captain, car_1, car_2, car_building_gargantuan, car_interior_mecha_driver, car_interior_photo, car_interior_sketch, car_interior_toon, car_mountain_colossal, castle, chair, chips_hotdog_dr_pepper_painting, city_day, city_night, classroom1, classroom2, classroom_anime_empty, cleo_slingshot, cloud, comic, comic_panel2, comic_panel3, comic_panel4, coraline1, coraline2, couple_middle_aged, door_first, door_last, fern_gully, fish_pixel, forest_autumn, forest_day, forest_day_night, forest_night, fruit_reference_photo, fruitbowl, fuji, garden_pond_anime, ghibli_grass, ghibli_kitchen, ghibli_painting_reference_anime, ghibli_painting_reference_painterly, ghibli_street, girl_painting, girl_painting_reference, gordon_1996, gordon_2004, gordon_comic, grass_anime_girl, grass_anime_scenery, gromit, gumby, gwen, gwen_cg, hermione_preteen, ivy_toon, jacket, jacket2, kasia, kasia_bag, kasia_bag_2, kasia_outfit, kasia_render, kasia_swimsuit, kasia_swimsuit_render, kasia_swimsuit_worn, kaypro_ii, kiki, laika, lego1, lego2, maggie_grandpa_cat, marker, misato_car_1, misato_car_2, misato_car_real, misato_car_technical_print, miya, miyu, molly, mountain_rain, nadia, nerv, newspaper, p1_first, p1_last, p2_first, p2_last, p3_first, p3_last, p4_first, p4_last, p5_first, p5_last, p6_first, p6_last, pancakes, pavilion_anime, peter_griffin_painting, peter_griffin_toon, phone, pjs, pocahontas, pooh, pre-teen1, ramen_pixel, riley_preteen, river_mountain_anime, roadway_toon, room_anime, rudolf, rugrats, saber_reference_anime, saber_reference_painterly, saber_reference_photo, sam_jackson_jurassic_middle_aged, san_fransisco_day_evening_night, sanfran_day, sanfran_evening, sanfran_night, scooby, shed_day, shed_dusk, shed_night, ship_gargantuan, shoes_anime, shrek_cg, simpsons_couch_toon, skellington, sleeping, smart_car_large, spongebob_tree_toon, stage, supergirl1, supergirl2, suv_large, temple_day, temple_grounds_anime, temple_night, third_rock, titans1, titans_go, toddler, town_tower_anime, toy_car_minuscule, toy_car_modest_1, toy_car_modest_2, toy_car_small_1, toy_car_small_2, toy_car_tiny_1, toy_car_tiny_2, truck_huge, tv, uniform_reference_anime, uniform_reference_painterly, uniform_reference_photo, van_huge, van_pixel, vector_city, wayne_knight_jurassic_adult, wayne_knight_older_adult, will_preteen, window, woman_oil, woman_reference_photo, woody_cg |
| `monochrome` | **10** | destroyer_drawing, destroyer_photo, fruit_reference_sketch, lincoln_money, lincoln_photo, sketch_boat, sketch_man, sketch_woman, teddy_taft, woman_reference_sketch |

### `[[AGE]]` tally

| bracket | images | which |
|---|---|---|
| `infant` | **3** | baby_middle_aged, maggie_grandpa_cat, rugrats |
| `toddler` | **4** | boo_toddler, rugrats, toddler, toy_car_modest_1 |
| `child` | **15** | avatar_1, avatar_2, boondocks, classroom1, classroom2, comic_panel4, fern_gully, ghibli_street, grass_anime_girl, molly, nadia, pancakes, pjs, toy_car_modest_2, toy_car_small_1 |
| `pre-teen` | **20** | cleo_slingshot, coraline1, coraline2, girl_painting, girl_painting_reference, hermione_preteen, kiki, laika, p2_first, p2_last, p3_first, p3_last, p4_first, p4_last, p6_first, p6_last, pre-teen1, riley_preteen, will_preteen, window |
| `teenager` | **28** | annie1, annie2\*\*, annie2_cropped, annie3, annie3_panel1, avatar_2, ayanami_oil, azumanga_anime, azumanga_toon, car_interior_mecha_driver, comic, comic_panel2, gwen, gwen_cg, kasia, kasia_render, kasia_swimsuit_render, kasia_swimsuit_worn, miya, nadia, saber_reference_anime, third_rock, titans1, titans_go, uniform_reference_anime, uniform_reference_painterly, uniform_reference_photo, van_pixel |
| `young adult` | **31** | annie3, annie3_panel1, april_1987, april_comic, april_fanart, beauty_beast, blonde_reference_painterly, blonde_reference_photo, car_interior_sketch, castle, fern_gully, ivy_toon, jacket, jacket2, marker, pocahontas, saber_reference_painterly, saber_reference_photo, scooby, sketch_woman, sleeping, stage, supergirl1, supergirl2, temple_day, temple_night, third_rock, toy_car_tiny_1, woman_oil, woman_reference_photo, woman_reference_sketch |
| `adult` | **23** | bookshop, bumper_car_medium, captain, car_interior_toon, comic, coraline2, door_last, ghibli_street, gromit, newspaper, p1_first, p1_last, p4_first, p4_last, pancakes, peter_griffin_painting, peter_griffin_toon, shrek_cg, smart_car_large, suv_large, toy_car_modest_1, van_huge, wayne_knight_jurassic_adult |
| `middle-aged` | **11** | baby_middle_aged, comic_panel3, couple_middle_aged, gordon_2004, gordon_comic, phone, sam_jackson_jurassic_middle_aged, sketch_man, teddy_taft, third_rock, toy_car_small_2 |
| `older adult` | **6** | gordon_1996, lincoln_photo, maggie_grandpa_cat, pjs, tv, wayne_knight_older_adult |
| `n/d` | **18** | airliner_gargantuan, annie2\*\*, boondocks, comic, comic_panel3, destroyer_photo, forest_autumn, laika, misato_car_real, miyu, p5_first, p5_last, room_anime, rugrats, sam_jackson_jurassic_middle_aged, ship_gargantuan, toy_car_minuscule, toy_car_tiny_2 |
| `n/a` | **11** | april_1987_figure, bird_vector, bird_watercolor, gumby, lego1, lego2, lincoln_money, pooh, rudolf, skellington, woody_cg |
| `crowd` | **3** | ghibli_street, pjs, stage |

**145 of 203 images hold a human figure.** An image contributes to every bracket it contains, so this column counts IMAGES PER BRACKET and does not sum to the corpus — unlike the medium tally, which partitions it. `n/d` is a figure whose depiction does not determine an age; `crowd` is an un-individuated mass. Animals are deliberately absent: their vocabulary is a different four-term list whose `adult` would collide with the human bracket in the same cell.

**Total 203.** Live-action (`photograph` + `live-action film`) is **81 of 203, 40%** — down from 29/37, 78% at the start of session 7. 5 of those (`chair`, `car_1`, `car_2`, `car_building_gargantuan`, `car_mountain_colossal`) are filed as `photograph` on provenance the pixels do not show — clean studio product shots, and photoreal AI images that read as photographs — so the honest range is 76–81. The first three carried an `amb` flag until session 19; that flag is retired and every such ruling is now an accept-set in `_expected` instead.

\* *(retired session 19)* The `amb` flag is gone. `chair`, `car_1` and `car_2` are still
filed as `photograph` on provenance the describer cannot see — all three sit on a seamless
white studio ground, the case where photograph, product render and AI render converge — but
that ruling is now carried as an accept-set in `_expected` (`photograph | 3D CG`) rather than
by a flag, so it is applied by the scorer instead of being remembered by a reader. Two files
of one object must still agree with each other.
\*\* `annie2` is a photograph *of* a watercolour, filed by the outer medium per tie-break 2. Its
content is a drawing, so it inflates the live-action share by one.

*(Rewritten session 15. The previous version of these two paragraphs still named
`print / technical plate` and `3D CG / product render`, terms the session-10 rebuild had already
removed, and claimed `drawing / ink` had no sample after `annie1` was reclassified into it. Check
these against the generated tally rather than trusting the prose.)*

**No coarse term is a singleton.** The smallest is `print` at 2. **Five *sub*-terms are
singletons**: `stop-motion / figure` (`april_1987_figure`), `drawing / digital`
(`car_interior_sketch`), `drawing / ink` (`annie1`), `print / engraving` (`lincoln_money`) and
`print / halftone` (`destroyer_drawing`). A `style` result on any of the five is **unreplicated** —
one image cannot tell you whether the term works or whether that image is unusual. `figure` is the
one to watch, because its single sample is also atypical of the term (see "Rulings that may need
revisiting").

**Three defined sub-terms have no sample at all**: `stop-motion / model`, `comic / screentone` and
`drawing / pencil`. Same situation as the character describer's untested age brackets — the
vocabulary offers a term the corpus cannot exercise, which is fine and deliberate per "Adding a
term the corpus cannot exercise", but a describer emitting one of them cannot be checked against
anything.

---

## Standing gaps

**Nothing blocking.** Every gap raised in sessions 6, 7, 12 and 17 has been closed — session 18
closed the last one that was actually blocking work, the absence of figureless anime and cartoon
frames. What remains is preference rather than obstruction:

1. ~~A day/night pair that is both photographic *and* signage-free.~~ **Closed session 15** by
   `shed_day`/`shed_dusk`/`shed_night` — three states, photographic, no legible text, and real
   information loss at night. It is now the bar; `city_*` keeps its value as the signage probe.
2. ~~`western toon` cases on the realistic side of the proportion band.~~ **Closed session 15.**
   The idiom went 8 → 25 samples, most of them realistically proportioned. The worry that motivated
   the gap — that the model was learning "western toon = more stylised" — is now testable rather
   than merely suspected.
3. ~~A second sample for the five singleton sub-terms.~~ **Largely closed session 18.**
   `stop-motion / figure` was the named priority — its one sample was atypical — and it now has
   **9**, including `laika`, which is a textbook member. `print / halftone` went 1 → 2 and gained
   a colour sample (`misato_car_technical_print`).
4. ~~`drawing / pencil` has no sample.~~ **Closed session 18** — five samples, two of them paired
   with the photograph they were drawn from (`woman-ref`, `fruit-ref`). **`stop-motion / model`
   and `comic / screentone` still have none**, kept deliberately: both are coarse, unmistakable
   discriminations a model can apply correctly without our being able to check it. Note that
   LEGO was considered for `model` in session 18 and ruled `figure` — moulded and rigid — so
   `model` is not merely uncollected, it has been actively declined once.
5. **More live-action breadth**, if `style` turns out to need it. Session 18 added ten
   photographic and four `live-action film` files, but the batch is anime-heavy overall so the
   live-action *share* fell rather than rose. The photographic images still skew toward people
   and rooms.
6. **A figureless frame in a medium other than `2D cel` or `vector`.** Session 18 gave the corpus
   figureless anime and cartoon frames, which was the standing blocker, but every figureless
   image is still either animation artwork, vector work, or a still life. There is no figureless
   `3D CG`, `comic` or `stop-motion` frame, so the "does the idiom tie-break survive with no
   figure" question is only answerable inside two media.
