# Synthetic bloat: calibrating the system-prompt token ceiling

**Task:** `.claude/handoffs/SIDE_HANDOFF_bloat_calibration.md`
**Run:** 28 runs · 808 model calls · 1.16h wall clock · no stop condition tripped
**Server:** unchanged throughout — verified against CLAUDE.md's documented sampler settings
(`temp 0.0 · top_k 40 · top_p 0.9 · repeat_penalty 1.05`), `n_ctx` 16,384 per slot, 4 slots.
No flag was altered, so these numbers are comparable with the rest of the project's archive.

---

## Headline

**Format adherence does not degrade with system-prompt length anywhere below ~5,000 tokens, with
the prompt's logic held constant.** On the primary probe, format was **26/26 at 4,982 tokens in all
four arms** — 35% past the current 3,700 `LINE` and 28% past the 3,885 `--check` failure
threshold. Across 676 primary case-outputs there were **5 format failures (0.7%)**, and **two of
them were in the unpadded baseline**.

This is one of the outcomes the handoff named in advance: *"Nothing breaks even at 5,000 tokens.
That is a real and valuable result — it would mean the ~3.7k figure is badly wrong and the five
historical points were all confounded."* Per that instruction I did **not** escalate past 5,000
chasing a break.

**But there is a second finding that qualifies it, and it is the more interesting one.** The
corruption signature from `L-PROMPT-TOKEN-BUDGET` — a mangled field token with correct content
underneath — *did* appear, twice. Both occurrences are confined to **one of the four arms**
(filler B inserted mid-prompt), and neither scales with length. So length is not the variable that
produces it; something about *where* and *what kind* of material is added is. See § 4.

**Bottom line for the project:** the ~3.7k figure does not describe a length limit. The most
likely reading of the five historical points is that they measured **instruction density**, not
tokens — and this experiment cannot distinguish those two, because inert filler is precisely the
thing a model is free to ignore. Recommendations in § 6 are built around that distinction.

**Two things were added to § 6a after the run, both prompted by the user's reading of this report,
and both change the conclusion more than anything in the run itself:**

1. **An audit of the five historical points.** Of the three at ~3.7k, **only one is a failure**, and
   the other two are prompts that *work* — one of them the best format score ever recorded. The
   clustering of prompt sizes near 3.7k is better explained by four documents sharing one template
   than by a model property.
2. **`fl2va` v4 — the one real failure — was recovered from the user's downloads and measured: 3,591
   tokens, not ~3.7k.** That is *below* `describer_frame` (3,705, fine) and `describer_style` v2
   (3,740, best-ever), and its **live-rule count of 2,698 is identical to the version shipping
   today**. No token metric separates them. The complete v3→v4 diff is **one line, 92 tokens**.
   **And then v3 vs v4 was actually run: the failure does not replicate.** No content is lost in v4
   that v3 keeps; p1 drops the lamp in *both*; p6 is 60% *longer* under v4. The lamp turns out to be
   lost **upstream** — nothing in the composer's input corroborates it — and v4's rule was the
   attempted *fix* for exactly that. My first causal reading is retracted in § 6a. The upstream chain
   has changed since session 3, so this does not refute the original attribution; it shows the
   replication is gone. Either way the v4 point is not evidence for a token or density ceiling.
3. **After the audit, the entire basis for a token or density ceiling is ONE prompt's three-point
   ladder** (`describer_style`, 3,072 → 3,215 → 3,386 live-rule tokens). The lesson's claim of
   "attested independently on three prompts" does not hold.
4. **A better-specified hypothesis: ~3,100 LIVE-RULE tokens** (total minus the `EXAMPLES` block) —
   worth recording but now **weaker**, since v4 shows a prompt can break far below it for reasons
   that have nothing to do with count. At best it is a *necessary* ceiling, not a sufficient
   predictor. **This experiment held live-rule tokens constant at 2,239 and never tested it**; § 6e
   is the 13-minute experiment that would.

---

## 1. Method, and what was held constant

| | primary probe | secondary probe |
|---|---|---|
| prompt | `prompts/describer_setting.txt` (2,939 tok, locked v5) | `prompts/fl2va.txt` (3,561 tok) |
| test | `tests/describer_setting.json`, 26 images | `tests/cases_fl2va_full.json`, 6 composer cases |
| verdict | `validate.py describer --role setting` | `validate.py h3` |
| design | full 2×2: filler {A,B} × position {end,mid} × 6 levels | filler A appended × 6 levels × {image, no image} |
| runs | 24 padded + 2 unpadded baselines | 2 (one per arm, all levels inside each) |

Levels: **3,800 · 3,900 · 4,000 · 4,200 · 4,500 · 5,000**, hit within ±25 tokens using the live
tokenizer via `scripts/token_budget.py`'s `count()`. Measured counts and filler share:

| level | `describer_setting` | filler share | `fl2va` | filler share |
|---|---|---|---|---|
| baseline | 2,939 | 0% | 3,561 | 0% |
| 3,800 | 3,784–3,792 | 22% | 3,804 | 6% |
| 3,900 | 3,885–3,896 | 24–25% | 3,884 | 8% |
| 4,000 | 3,982–3,984 | 26% | 3,982 | 11% |
| 4,200 | 4,192–4,200 | 30% | 4,189 | 15% |
| 4,500 | 4,483–4,488 | 34–35% | 4,478 | 20% |
| 5,000 | 4,981–4,982 | 41% | 4,980 | 28% |

**Filler kinds.** **A** — inert pipeline prose: same register, plausible, past-tense provenance and
non-actionable rationale, no imperatives and no second person. **B** — neutral unrelated
encyclopaedic English on library classification and bookkeeping convention, explicitly marked
ignorable, chosen for maximum distance from image description (no colours, materials, places,
weather or times of day, so it could not bleed into a description).

**Positions.** Both are existing section boundaries; a section is never split. **mid** = between
`CHOOSING THE PLACE` and `WHAT YOU DESCRIBE` (~50% depth). **end** = after the `EXAMPLES` block but
**before** the final closing line. Filler goes *before* that closing line deliberately: it is the
task handoff and every prompt in the repo ends with it, so putting filler after it would have
changed prompt *structure* and not just length.

### Instrument verification — `verify.py`, all four checks pass

1. **Pure insertion.** All 30 padded prompts differ from their source by **exactly one inserted
   block and nothing else** — no line of the original added, removed, reordered or altered.
   Checked with `difflib.SequenceMatcher`: exactly one non-equal opcode, of type `insert`. Without
   this the experiment would be measuring a prompt *edit*.
2. **Token window.** All 30 re-counted live, all within ±25 of target.
3. **Noise floor: ZERO.** The two unpadded baseline runs are **byte-identical** (`md5
   08f8420b…`). This is the strongest form this check can take and it means any movement in the
   curve is attributable rather than jitter.
4. **Server config** unchanged, as above.

**A bonus determinism result.** Session 12 found that determinism holds for a *replayed run* but
not a *replayed case* at a different file position. The secondary probe tested that directly — the
same 6 composer cases appear twice in one file, at different positions, as `c_base_*` and
`c_base2_*` — and got **6/6 byte-identical in both arms**. That does not refute session 12's
observation, but it does mean the effect is not general, and here it contributed nothing.

**Context headroom.** `n_ctx` is 16,384. A 5,000-token prompt + a 2,048-token image floor + 2,048
`max_tokens` ≈ 9,500, so nothing was truncated and "nothing breaks" is not a context artefact.

---

## 2. The curve

### Primary probe — format score, 26 images per cell

| level | measured tokens | a_end | b_end | a_mid | b_mid |
|---|---|---|---|---|---|
| *unpadded* | 2,939 | **25/26** (×2 runs) | | | |
| 3,800 | 3,784–3,792 | 26/26 | 26/26 | 25/26 | 25/26 |
| 3,900 | 3,885–3,896 | 26/26 | 26/26 | 26/26 | 26/26 |
| 4,000 | 3,982–3,984 | 26/26 | 26/26 | 26/26 | 26/26 |
| 4,200 | 4,192–4,200 | 26/26 | 26/26 | 26/26 | 26/26 |
| 4,500 | 4,483–4,488 | 26/26 | 26/26 | 26/26 | 25/26 |
| 5,000 | 4,981–4,982 | 26/26 | 26/26 | 26/26 | 26/26 |

The curve is **flat**, and the worst cell in the table is the unpadded baseline.

### Every format failure in the experiment, and where it happened

| case | failing runs | token counts where it failed |
|---|---|---|
| `set_miya` | 2 / 26 | **2,939 · 2,939** (both baselines only) |
| `set_cloud` | 1 / 26 | 3,784 |
| `set_city_night` | 1 / 26 | 3,792 |
| `set_forest` | 1 / 26 | 4,488 |

This table is the argument. Five failures, four distinct cases, every one a singleton except
`set_miya` — which fails **only when unpadded** and passes in all 24 padded runs. Failures occur at
2,939, 3,784, 3,792 and 4,488, and **not** at 4,981/4,982. With a zero noise floor these flips are
genuinely caused by the prompt change, but their *direction is arbitrary*: these are marginal
cases being perturbed, not a ceiling being crossed.

**Do not read this as "padding improves adherence."** The apparent improvement (0.5% failure rate
padded vs 3.8% unpadded) is one marginal case counted twice in two baseline runs against 24 padded
runs. The correct statement is: *the single most failure-prone case in the corpus happens to fail
in the unpadded configuration*, and `L-DETERMINISM-IS-NOT-STABILITY` describes exactly this —
stably marginal, not stably correct.

### Secondary probe — `fl2va` composer, 6 cases per cell

| level | measured tokens | img | noimg |
|---|---|---|---|
| *unpadded* | 3,561 | 5/6 (×2) | 5/6 (×2) |
| 3,800 | 3,804 | 6/6 | 6/6 |
| 3,900 | 3,884 | 5/6 | 6/6 |
| 4,000 | 3,982 | **4/6** | 6/6 |
| 4,200 | 4,189 | 6/6 | 6/6 |
| 4,500 | 4,478 | 6/6 | **5/6** |
| 5,000 | 4,980 | 6/6 | 6/6 |

Again flat, again with the unpadded baseline among the worst cells, and again **6/6 at 4,980 in
both arms**. The two dips are non-monotone and land at different levels in the two arms (4,000 vs
4,500), which is the signature of noise rather than a threshold. And they are case-specific rather
than level-specific: the img arm's failures are all `p6` plus one `p1`, and the noimg arm's are all
`p5` — the same cases that fail at that arm's own unpadded baseline.

---

## 3. Where it breaks, and how — the signature breakdown

The handoff asked for the *kind* of failure, not just the count. Across the whole experiment:

| signature | primary (624 padded outputs) | secondary (72 padded outputs) |
|---|---|---|
| format failure (`validate.py`) | 3 (0.5%) | 4 (5.6%) |
| **corrupted field token** (near-miss) | **1** | 0 |
| **invented field token** | **1** | 0 |
| length collapse < 70% of baseline | 18 events / 3 distinct cases | 12 events |
| length collapse < 50% | 3 | 0 |
| empty output | 0 | 0 |
| runaway toward `max_tokens` | 0 | 0 |

**Order of appearance:** corruption at **3,792** and **4,488**; length collapse at **3,784**, the
lowest level tested; format failure at **3,784**. Nothing appears first at the high end. There is
no "corruption starts at N, collapse at M" ordering to report, because **no signature has a
threshold** — each appears sporadically across the whole range, including the bottom of it.

### Length collapse is case-driven, not length-driven

| case | collapse events | at token counts |
|---|---|---|
| `set_p6_outside` | 10 / 24 runs | 3,784 · 3,784 · 3,885 · 3,896 · 3,982 · 3,984 · 4,192 · 4,483 · 4,981 · 4,982 |
| `set_miya` | 7 / 24 runs | 3,784 · 3,896 · 3,982 · 4,192 · 4,483 · 4,488 · 4,981 |
| `set_window` | 1 / 24 runs | 3,792 |

Three of 26 images account for all 18 events, and `set_p6_outside` collapses at **every** level
including the lowest — so this is "padding at all moves this case," not "padding past N breaks it."
Mean output length across all padded primary runs is **1.004** of baseline (range 0.982–1.048):
dead flat in aggregate.

Two important qualifications on this measure:

- **`set_miya`'s collapse is an artefact.** Its *baseline* is the broken output — the one emitting
  two records with a duplicated `[[DEFINITION]]`. The padded runs emit one correct record, which
  reads as 63–65% of an inflated baseline. That is a fix being counted as a collapse.
- **`set_p6_outside`'s collapse is real, and it is a content change the format checker cannot
  see.** Both records are well-formed. The padded one is terser and writes `[[CONTENTS]] none`
  where the baseline itemised a window, a door frame and a hanging picture:

  > baseline (893 chars): `[[CONTENTS]] a section of exposed red brick wall, a tall rectangular window set into the brickwork, a heavy wooden door frame with peeling paint, a framed picture hanging on the interior wall visible through the opening`
  >
  > padded at 4,192 (517 chars): `[[CONTENTS]] none`

  This is the closest thing in the experiment to the `fl2va` v4 signature — well-formed output
  that has quietly shed content. It is worth knowing that it shows up at 3,784 as readily as at
  4,982.

---

## 4. Do the filler kinds agree? — mostly, and the exception is the finding

**On the curve: yes, completely.** Both filler kinds are flat across all six levels in both
positions. On the main question the experiment is *not* compromised.

**On the corruption signature: no, and the disagreement is confined to one cell.**

| arm | near-miss tokens | invented tokens | case-outputs |
|---|---|---|---|
| unpadded | 0 | 0 | 52 |
| a_end | 0 | 0 | 156 |
| b_end | 0 | 0 | 156 |
| a_mid | 0 | 0 | 156 |
| **b_mid** | **1** | **1** | 156 |

Both events, in full:

**`b_mid_4500` / `set_forest` at 4,488 tokens** — the classic signature, correct content under a
corrupted token:
```
[[CONTINGENTS]] none
```
`CONTENTS` → `CONTINGENTS`. `validate.py` reported this as `missing field [[CONTENTS]]`, which is
how it became that arm's 25/26. This is structurally identical to the `[[DISTINGISHING]]` /
`[[DEFINING]]` events that `L-PROMPT-TOKEN-BUDGET` cites.

**`b_mid_3800` / `set_stage` at 3,792 tokens** — an *invented extra* field, spliced between
`[[STRUCTURE]]` and a correctly-emitted `[[CONTENTS]]`:
```
[[CONTINGENCY]] none
[[CONTENTS]] a wide red carpet aisle running from the stage into the audience, ...
```
**`validate.py` PASSED this record.** All eight required fields were present, once each, in order,
so nothing in the checker objected — it has no concept of an unexpected field token. This is a real
gap, and it is exactly the gap the handoff predicted the extra checks would fill.

### What this does and does not license

Both arms of the 2×2 that isolate a single factor are clean: filler kind alone (`b_end`) produces
zero corruption, and mid-position alone (`a_mid`) produces zero corruption. Only the **interaction**
produces any. **This cell exists only because you chose the full 2×2 over the 3-arm design I had
recommended.** The 3-arm plan omitted `b_mid` precisely on the grounds that nothing asked for the
interaction, and it would have reported "nothing breaks, filler kinds agree" with no corruption
observed at all.

**What I am not going to claim.** The obvious story is that filler B's formal Latinate register
(`classification`, `notation`, `hospitality`, `reconciliation`, `enumerative`) drags a field name
toward `CONTINGENTS`/`CONTINGENCY` when it sits mid-prompt among live rules rather than after the
examples. That story is *plausible and unverified*. Filler B contains neither "contingency" nor
"contingents", so this is not direct lexical bleed. Per `L-CAUSAL-STORIES-ARE-WEAK` this is a
hypothesis with a discriminating test attached (§ 6g), not a finding. **Two events in 156 outputs is
also too few to characterise** — it could be two marginal cases, the same way the format flips are.

What it does establish: **the filler is not perfectly inert.** That was the named risk of choosing
a probe needing 22–41% filler, and it materialised — at a very low rate, on a secondary measure,
in one of four arms. It is a reason to treat the flat curve as "inert length is nearly free" rather
than "length is free."

---

## 5. Image-bearing vs text-only — the secondary question

**Both arms break in the same place: nowhere.** Both are flat and both reach 6/6 at 4,980. Per the
handoff each arm was compared only against its own unpadded baseline, never against the other in
absolute terms — and each arm's own baseline is 5/6, below its padded results.

So on the evidence available: **the image is not crowding out prompt tokens** anywhere in
3,561–4,980. If it were, the image-bearing arm would have degraded earlier, and it did not.

**One asymmetry worth recording, with a caveat attached.** Mean output length relative to each
arm's own unpadded baseline:

| level | img | noimg |
|---|---|---|
| 3,800 | 0.933 | 0.940 |
| 3,900 | 0.941 | 0.981 |
| 4,000 | 0.914 | 1.120 |
| 4,200 | 0.965 | 0.997 |
| 4,500 | 0.932 | 0.954 |
| 5,000 | 0.955 | 1.013 |
| **mean** | **0.94** | **1.00** |

The image-bearing composer shortens by ~6% under padding at every level; the text-only one does
not, centring on 1.00. That is consistent with total attention load mattering for *how much gets
written* even while format holds — which is the mechanism the `--image-min-tokens` experiment is
built on. **But it is 6 cases and a ~6% effect, and it does not grow with padding**, so it is a
lead, not a result.

**Consequence for the blocked experiment.** It now has its curve. But the expected payoff looks
**small**: the image-bearing arm did not break earlier, so buying prompt headroom by cutting image
tokens has little format headroom to buy. That matches the caution already on the TODO — `fl2va`
v4 degraded with no image in the call at all.

---

## 6. Recommendations — numbers, not edits

**Nothing below has been applied.** Every file named is one the handoff put out of bounds.

### 6a. The framing change that matters more than any constant

**The budget should count live instruction, not tokens.** This experiment shows *inert* length is
nearly free to ~5,000. It says nothing about *rule* length, because inert filler is exactly what a
model can safely ignore. The two facts sit together like this:

| | tokens | what the added material was | outcome |
|---|---|---|---|
| `describer_setting` + filler | 4,982 | 41% inert prose | **26/26, clean** |
| `describer_style` (session 11) | 4,054 | a 171-token *rule* | 39/45, corrupted tokens |

The most economical explanation of the five historical points is that they tracked **instruction
density** — competing rules, closed vocabularies, field count — and that token count was a
correlated proxy that has now been shown to come apart from it. `describer_style` at 4,054 was
~30% closed vocabulary and 10 fields, all live. `describer_setting` at 4,982 was 41% material the
model was free to skip.

This also predicts the split's success: `describer_style_look` (1,876) + `describer_style_class`
(2,584) total **4,460 tokens** — more than the 3,740 single prompt it replaced — and it improved
`western toon` from 1/8 and 3/8 to 6/8. Under a token-budget theory that is anomalous. Under a
density theory it is the expected result: the total grew, but no single call's live rule count did.

#### Audit: what the five historical points actually say

Added after the run, prompted by the observation that ~3.7k appears three times in the record. It
does — but on inspection **only one of those three is a failure**, and it is the one point that was
never measured:

| point | tokens | measured? | actually a failure at ~3.7k? |
|---|---|---|---|
| `fl2va` v3 | 3,499 → 3,561 | yes, in git | no — ships |
| **`fl2va` v4** | **3,591 — MEASURED** | **yes, recovered mid-session** | **it failed, but NOT at 3.7k** |
| `describer_frame` | 3,705 | yes | **no — works across many sessions** |
| `describer_style` v2 | 3,740 | yes | **no — 45/45, best format score on record** |
| `describer_style` | 3,883 | yes | yes, but 5% above 3.7k |
| `describer_style` | 4,054 | yes | yes, but 10% above 3.7k |

Three things follow, and together they are more deflationary than § 6a's density reading alone.

**1. The one failure at "~3.7k" was measured, and it was 3,591 — and that is decisive.** The v4 file
had never been committed (`prompts/fl2va.txt` has exactly two commits, at 3,499 and 3,561), but the
user found a copy in their downloads mid-session and added it to
`reference/retired/prompts/fl2va_v4.txt`. Measured against the live tokenizer:

| version | total | examples | **live-rules** | outcome |
|---|---|---|---|---|
| v3 (git `3daef42`) | 3,499 | 893 | **2,606** | fine |
| **v4** | **3,591** | 893 | **2,698** | **broke badly — reverted** |
| current (ships) | 3,561 | 863 | **2,698** | fine |

**Two independent facts kill every token-based explanation of this failure:**

- **v4 broke at 3,591 total — *below* two prompts that are fine.** `describer_frame` works across
  many sessions at 3,705 and `describer_style` v2 scored the best format result on record at 3,740.
  A ceiling cannot sit below the things that pass it.
- **v4 broke at 2,698 live-rule tokens, and the prompt shipping today is at exactly 2,698 live-rule
  tokens.** Same number, one broken and one fine. So the live-rule measure does not separate them
  either. *No* token metric does.

And the cause is now pinned exactly. The complete v3 → v4 diff is **one line** — a 92-token addition,
matching the lesson's own description of "one checklist rule":

> `- EVERY action the user describes MUST appear in your output. Before you finish, read the user's
> description again and check that each action you were given is present. A user action is never
> replaced by something from [[DELTA]]: if the user says he picks up the gun and [[DELTA]] reports a
> photograph moving, write the gun. Write both only if both fit; drop the [[DELTA]] item before you
> drop the user's.`

**My first reading of that rule was wrong, and I ran the test that shows it.** The rule ends by
telling the model which material to *drop* when things compete — "write both only if both fit; drop
the `[[DELTA]]` item before you drop the user's" — and the recorded failure was dropped material, so
the story wrote itself. I then ran v3 and v4 head to head (`cases/primary__v3v4.json`, 18 shared
upstream cases + 6 composer per arm, 30 calls, 3.2 min) and **it does not replicate**:

| case | v3 chars | v4 chars | ratio | missing in v3 | missing in v4 |
|---|---|---|---|---|---|
| p1 | 745 | 709 | 0.95 | **`lamp`** | **`lamp`** |
| p2 | 850 | 839 | 0.99 | — | — |
| p3 | 848 | 911 | 1.07 | — | — |
| p4 | 958 | 803 | 0.84 | — | — |
| p5 | 1,081 | 1,065 | 0.99 | — | — |
| p6 | 628 | 1,005 | **1.60** | `window` | — |

**No case loses content in v4 that v3 keeps.** p1 drops the lamp in *both* arms — no light-related word
appears in either (`lamp`, `light`, `glow`, `switch`, `illuminate` all absent). p6, which the lesson
says shed a third of its length under v4, is **60% longer** under v4 here. Both arms passed format.

**And the cause is upstream, not in the composer at all.** The `[[DELTA]]` for p1 reports pose, gaze,
expression and a cigarette — no lamp. The lighting pair the composer receives shows warm artificial
light in *both* frames with only a direction change (right → front-left), never an on/off transition.
So nothing in the composer's input corroborates the user's "turns on the lamp," and both versions
silently drop it.

Which inverts the story completely: **v4's rule was the attempted FIX for this** — "EVERY action the
user describes MUST appear… A user action is never replaced by something from `[[DELTA]]`" is aimed
squarely at a user action no other input supports. It did not work. v4 is a rule that **failed to fix
its target**, not one that broke something else.

**What I can and cannot conclude.** I cannot say session 3's attribution was wrong: the upstream chain
has changed underneath (`describer_frame` is now v8, `fl2va_delta` has its own version history), so
the composer's input today is not what it was, and the lamp may well have been present in the delta
back then. **The v3-vs-v4 comparison is no longer a valid replication** — which is itself the sharpest
possible argument for § 6f, and shows the archiving rule must cover *the whole chain*, not one prompt:
reproducing a composer result needs the composer, the describer and the delta prompt versions together.

So the v4 data point ends up weaker still. It is not a length failure, not a density failure, and not
reproducibly a v4 failure at all. **`L-DONT-OVER-CONSTRAIN` remains the better home for it than
`L-PROMPT-TOKEN-BUDGET`, but that is now a judgement about the rule's wording, not a measured result.**

**A live finding for the main project, incidentally.** p1's lamp event is dropped by the current chain,
and the mechanism is visible: a user-specified action with no corroborating input silently disappears.
That is a *content* failure `validate.py` cannot see, and it is exactly the class of failure the
follow-up experiment needs to measure — with p1 as a ready-made known-failing case.

On where "3.7k" came from: the user notes their memory may have been reaching for **3,705** —
`describer_frame` — and attached it to the v4 event afterwards. That is a very ordinary thing to
happen, and it is the whole argument for § 6f: the number in the lesson was a reconstruction, and one
file recovered from a downloads folder overturned it in a single command.

**2. Two of the three points at the line are prompts that WORK**, and one of those is circular.
`describer_frame` at 3,705 is described in the lesson as "sits exactly on the line; almost certainly
why it stopped growing there" — that reads a prompt's *success* as evidence for a limit, inferring
the cause from the absence of an effect. And `describer_style` v2 at 3,740 scored the **best format
result in the project's history**. If 3.7k were a ceiling, the best-ever score should not be sitting
on it.

**3. The clustering of prompt SIZES near 3.5–3.7k has a mundane explanation.** These are four
documents written to one template, by one author, for one family of tasks, each carrying a worked
`EXAMPLES` block of comparable weight:

| prompt | tokens | EXAMPLES share |
|---|---|---|
| `describer_frame` | 3,705 | 1,344 (36%) |
| `fl2va` | 3,561 | 863 (24%) |
| `describer_setting` | 2,939 | 700 (24%) |
| `describer_style` | 3,740 | 668 (18%) |

Similar documents from a common template converge on similar sizes. That is **convergent size, not a
convergent limit** — and it is a much cheaper explanation for "3.7k three times" than a model
property.

**What survives the audit — one prompt.** Taking the six points in turn:

| point | verdict after audit |
|---|---|
| `fl2va` v3 3,499 / 3,561 | not a failure |
| `fl2va` v4 3,591 | **a failure, but caused by one rule's semantics.** No token metric separates it from the version shipping today. Removed from the evidence base for any length or density claim |
| `describer_frame` 3,705 | not a failure; the lesson's reasoning here is circular |
| `describer_style` v2 3,740 | not a failure — best score on record |
| `describer_style` 3,883 → 4,054 | **real, monotone degradation** |

**The entire empirical basis for a token or density ceiling reduces to ONE prompt's three-point
ladder.** Everything else was either never a failure or now has a better explanation.

The lesson's claim to be "attested independently on three prompts" does not hold. It is: one prompt's
ladder, plus a semantic-rule failure misfiled as a length failure, plus a prompt that works fine.

**"Adding a rule costs a rule" survives intact, and v4 is its cleanest demonstration** — one line,
92 tokens, and the damage was exactly the behaviour the line described. What does not survive is the
attachment of that finding to a token count.

The `describer_style` ladder is the one piece of real signal left, and note what it is: a monotone
degradation on the **densest prompt in the repo** (18% examples, so ~82% live rules, plus three
closed vocabularies and ten fields) as constraints were added to it. That is evidence about rule
load on an already-saturated prompt. It is not evidence about tokens.

#### A better-specified hypothesis: ~3,100 LIVE-RULE tokens

If the variable is live instruction rather than total length, then subtracting each prompt's
`EXAMPLES` block should line the historical points up better than total tokens do. It does — and
strikingly so:

| point | total | examples | **live rules** | outcome |
|---|---|---|---|---|
| `describer_setting` | 2,939 | 700 | **2,239** | fine |
| `describer_frame` | 3,705 | 1,344 | **2,361** | fine across many sessions |
| `fl2va` v3 (earliest) | 3,499 | 893 | **2,606** | fine |
| `fl2va` current | 3,561 | 863 | **2,698** | ships |
| **`fl2va` v4** | **3,591** | 893 | **2,698** | **BROKE — same count as the shipping version** |
| `describer_style` v2 | 3,740 | 668 | **3,072** | **45/45 — best on record** |
| `describer_style` | 3,883 | 668 | **3,215** | 43/45 |
| `describer_style` | 4,054 | 668 | **3,386** | 39/45, corrupted tokens |

The `describer_style` ladder is ordered correctly and brackets a boundary tightly: **3,072 live-rule
tokens is fine and scores best-ever; 3,215 degrades.** Candidate threshold **~3,100 ± 100**. Total
tokens cannot order even that much — `describer_frame` at 3,705 total is fine while `describer_style`
at 3,883 total is not, a 178-token gap in the wrong direction — while live-rule tokens separate them
by 854 the right way.

**But v4 caps how much this hypothesis can ever claim.** v4 and the shipping prompt sit at the *same*
2,698 live-rule tokens with opposite outcomes, so the measure is **not sufficient**: a prompt can
break well below the bracket because of what a rule *says*. The most the live-rule measure can be is
a **necessary ceiling** — "above ~3,100 expect trouble" — never a guarantee of safety below it. Any
guard built on it must be worded that way.

It also accounts for the split without special pleading: `describer_style_class` sits at **1,969**
live-rule tokens and `describer_style_look` at **1,262**, both far below the bracket, which is why
splitting a 3,072-live prompt into two smaller ones bought real headroom even though the *total*
went up to 4,460.

**The arithmetic trap, stated because I nearly published it.** Applying "total minus examples"
mechanically to this experiment's padded prompts gives `describer_setting` at 4,982 a live-rule
count of 4,282 — which would appear to blow the hypothesis apart. That is wrong. **My filler is not
a rule.** The metric is *live instruction* tokens, and examples and inert filler are both
non-instructional, so the padded prompts sat at **2,239 live-rule tokens at every level**, exactly
the same as the baseline.

Which means: **this experiment never varied the quantity the hypothesis is about.** It varied total
length while holding live instruction constant, found no effect, and is therefore fully consistent
with a live-rule ceiling at ~3,100. The flat curve is what the hypothesis *predicts*, not evidence
against it.

**Treat this as a hypothesis, not a result.** It is four prompts and six points, the critical gap is
143 tokens on a single prompt, and it was fitted after the fact to data I already had — which is
exactly the shape `L-CAUSAL-STORIES-ARE-WEAK` warns about. It earns its place only because it is
*better specified and cheaply testable*, not because it is established. The test is in § 6e.

### 6b. `scripts/token_budget.py` — concrete constants

Current: `NEAR 3500 · LINE 3700 · TOLERANCE 0.05 → OVER 3885`.

`OVER 3885` is the number that is actually indefensible: `--check` fails a prompt at 3,885 while
this experiment measured **26/26 at 4,982** on the same instrument. Recommended:

```python
NEAR = 4000        # was 3500
LINE = 4300        # was 3700
TOLERANCE = 0.05   # unchanged -> OVER = 4515 (was 3885)
```

Reasoning for each:
- **`OVER 4515`** sits below the 4,982 where clean behaviour was measured, keeping a real margin
  for the fact that genuine prompt growth is rules rather than filler. It no longer fails anything
  this experiment showed to be fine.
- **`LINE 4300`** clears every prompt in the repo (largest 3,740) with ~560 tokens of headroom, so
  the `AT` band means "unusually large, check what you added" rather than firing on two
  known-good prompts as it does today.
- **`NEAR 4000`** keeps a coarse early warning.
- **Consider dropping `TOLERANCE` entirely** and writing `OVER = 4500` as its own constant. The
  percentage was introduced in session 12 to avoid failing `describer_frame` by five tokens; with
  `LINE` moved it is doing no work, and one derived constant is easier to reason about than two.

**A caveat to state in the code comment:** these numbers say *inert* length is cheap. They do not
license adding 800 tokens of new rules to a 3,700-token prompt.

**And the better guard, if § 6a's hypothesis survives its test.** Report a second number alongside
the total: **live-rule tokens = total − `EXAMPLES`**. `split_sections()` already isolates that block,
so this is a few lines in `token_budget.py`, not a rewrite. For real prompts (which contain no inert
filler) the two differ only by the examples block, and the live figure is the one that orders the
historical points correctly:

| prompt | total | live rules | on a ~3,100 live line |
|---|---|---|---|
| `describer_style` | 3,740 | 3,072 | **AT — right at it** |
| `fl2va` | 3,561 | 2,698 | near |
| `describer_frame` | 3,705 | 2,361 | comfortable |
| `describer_setting` | 2,939 | 2,239 | comfortable |
| `describer_style_class` | 2,584 | 1,969 | comfortable |
| `describer_style_look` | 1,876 | 1,262 | comfortable |

Note what that table does that the total-token column cannot: it puts `describer_style` alone at the
line and `describer_frame` — currently flagged `AT` and the subject of a session-12 false alarm —
comfortably clear. That matches the observed history exactly.

**Sequencing:** do not implement the live-rule guard before running § 6e. It is a post-hoc fit to six
points, and the test that would justify it costs 13 minutes.

### 6c. `L-PROMPT-TOKEN-BUDGET` — needs rewriting, and here is the substance

The lesson's thesis ("this model holds roughly 3.7k system-prompt tokens before adherence starts to
degrade") is **not supported** and should be replaced. Suggested content:

- Lead with the measurement: 26 runs, 676 outputs, 26/26 at 4,982 tokens in all four arms, with a
  zero noise floor and logic provably held constant. Length alone does not degrade format below
  ~5,000.
- Replace the thesis with the density claim in § 6a: what costs a rule is **another rule**, not
  another token. Keep the "adding a rule costs a rule" observation — it is still the attested
  effect — and detach it from the token count.
- Keep the **corruption signature** as diagnostic, but reattribute it: correct content under a
  mangled token is a real sign of losing grip on the format contract, and this experiment produced
  it twice — from *where and what kind* of material was added, not from how much.
- Retain the five historical points, but **replace the framing with the audit in § 6a**: only one of
  the three points at ~3.7k is a failure, that one's token count is an unrecoverable estimate, and
  the other two are prompts that work — one of them the best format score on record. What survives
  is two rule-addition pairs. Keep them; they are still the only evidence about rule-density growth.
- Drop the `describer_frame` row's reasoning outright. "Sits exactly on the line; almost certainly
  why it stopped growing there" infers a limit from a prompt's success, and it is the clearest piece
  of circularity in the current text.
- Keep "measure, don't estimate" — that part was always right.
- Note the new hard boundary: this was measured on **two** prompts, format only, one model, one
  server config.

### 6d. `scripts/validate.py` — a real gap, cheaply closed

`check_describer` silently passed a record containing an invented `[[CONTINGENCY]]` field, because
it only ever asks whether each *expected* field is present once and in order. Recommendation: flag
any `[[...]]` token that is not in the role's own field list, splitting near-misses (close to a real
field name) from inventions. `signature.py` in this directory has a working implementation
(`classify_tokens`, ~20 lines using `difflib.get_close_matches`) that reuses `DESCRIBER_ROLES` and
`FRAME_FIELDS` and adds no new data.

Note the existing constraint: `validate.py` is shared by every role and imported by `score.py`, so
the TODO's rule applies — gate the change on validating the archived character/setting/style runs
before and after and requiring byte-identical output.

### 6e. The one experiment that would settle this — and it is cheap

**Pad `describer_setting` with RESTATED EXISTING RULES instead of inert prose.** This was the
handoff's optional filler kind 3, and I skipped it; it is now clearly the most valuable arm that was
not run, because it is the only one that moves *live-rule* tokens.

Verbatim restatement adds rule-shaped, live instruction while adding **no new constraint**. So it
separates the two surviving candidate metrics:

| result | reading |
|---|---|
| degrades as live-rule tokens approach ~3,100 | the § 6a hypothesis holds; the budget should count live instruction, and the number is ~3,100 not 3,700 |
| stays clean at 3,100+ live-rule tokens | it is not token-shaped at all — what costs a rule is another **distinct constraint**, and restating is free. That would make the budget a *rule count*, not any token measure |

Design: `describer_setting` has 2,239 live-rule tokens, so reaching ~3,300 needs ~1,100 tokens of
restated rules — about 6 levels from 2,400 to 3,400 live. **6 runs, ~13 min**, reusing every script
in this directory (`pad.py` takes a new filler file and a target; `gen_cases.py` and `drive.py`
need a tag added). The zero noise floor means 6 runs is a real measurement.

One caveat on the probe: `describer_setting` is a *simple* prompt — 8 flat fields, one two-value
closed vocabulary. It may tolerate more live rules than `describer_style` does at the same count,
since the hypothesis is really about *competing* constraints. So a clean result at 3,400 live tokens
on `setting` would not fully clear `style`. The ideal probe is `describer_style` itself, which is off
limits while it is the live thread.

### 6f. Archive notable prompt states — the rule this session argues for

**User's proposal, and this session is the argument for it.** One file recovered from a downloads
folder overturned the project's most-cited lesson in a single command. We got that only by luck, and
only because the pre-repo `describer_frame` work happened to be preserved — for the ironic reason that
it was done by hand against claude.ai, where every version exchanged was kept. Once the work moved
into git, *fewer* prompt states were retained, not more, because git only records what was committed
and a superseded draft is exactly what nobody commits.

**Good news first, correcting an earlier claim in this report.** `fl2va` v1–v3 *do* survive, under
`dist/fl2va_v{1,2,3}.txt` in git history — `dist/` was the pre-`prompts/` location, folded in by commit
`3daef42`. Recovered and measured, the complete ladder is:

| version | total | examples | **live-rules** | outcome |
|---|---|---|---|---|
| v1 | 3,179 | 934 | 2,245 | — |
| v2 | 3,548 | 934 | 2,614 | — |
| v3 | 3,499 | 893 | **2,606** | fine, shipped |
| **v4** | **3,591** | 893 | **2,698** | **BROKE, reverted** |
| current | 3,561 | 863 | **2,698** | ships today |

v3 → v4 is **+92 live-rule tokens**, and v4 versus the current shipping prompt is **+0**.

**Now the bad news, and it is a live data-loss hazard.** While checking whether v4 could be committed
I found that **`reference/` is gitignored in its entirety** (`.gitignore:57`). Two consequences, both
of which contradict `.claude/CLAUDE.md`:

1. **CLAUDE.md's Project Structure lists `reference/` under "*(tracked in git)*". It is not, and never
   was** — `git log --all --diff-filter=A -- 'reference/*'` returns nothing on any branch. So
   `reference/test_archive/` (every archived test round), `reference/baselines/`, and
   `reference/official_H3_references/` have **no version-control backup at all**. They are
   local-only, exactly like `.claude/`.
2. **CLAUDE.md's session-11 note is wrong for two files.** It states that "every file here is
   byte-identical to a blob still reachable in git history, so this is a convenience copy and can be
   pruned freely." Checked file by file against the initial commit:

   | file | status |
   |---|---|
   | `describer_frame_v2…v7.txt` | recoverable — were committed under `prompts/` in `4dce882` |
   | **`describer_frame_v1.txt`** | **only copy in existence** — never committed |
   | **`fl2va_v4.txt`** | **only copy in existence** — never committed |

   Session 11's check was right about the six it looked at and generalised to a seventh that was
   never there. **"Can be pruned freely" is now a data-loss instruction**, and it points at the file
   that overturned the lesson.

**So the user's proposal needs one amendment: archiving into `reference/` preserves nothing.** It is
ignored, so a copy there is exactly as fragile as the downloads folder v4 was sitting in. Either
un-ignore the archive path — the narrow fix, `!reference/retired/` after the `reference/` line — or
put notable prompt states somewhere already tracked. The first is cleaner: it keeps the existing
directory shape and adds maybe a megabyte over the project's life.

**Still genuinely gone:** no `describer_setting` v1–v4, no `describer_character` history, and no
`describer_style` v1 or the 3,883 / 4,054 states — whose ladder is now the *entire* evidence base for
a ceiling. That last one stings: the three points the whole budget rests on are three numbers in a
markdown table with no files behind them. Had they been kept, § 6a's audit could have been a diff
instead of an inference.

**Recommended rule** (for `.claude/CLAUDE.md`, since it is a working practice):

> **Archive a prompt state whenever it becomes notable.** Notable means: we **locked** it; we
> **reverted** it and the reason is instructive; or it **scored** in a recorded test round. Copy it to
> `reference/retired/prompts/<name>_v<N>.txt` and commit it with one line saying what happened —
> "v4, reverted: the action-checklist rule caused dropped content." A prompt whose behaviour we
> measured is **data**, and the measurement is not reproducible without the file.

Notes on making it stick:

- **It is nearly free.** These files are 10–15 KB of text. The whole `reference/retired/prompts/`
  directory would be well under a megabyte after years of this.
- **`reference/retired/` already has exactly this shape** — mirroring the original repo path
  underneath — so this formalises existing practice rather than inventing a convention.
- **One correction to a note in CLAUDE.md.** It currently says the retired copies are "a convenience
  copy and can be pruned freely" since every file is byte-identical to a reachable git blob. True for
  the `describer_frame` set, and **now false for `fl2va_v4.txt`**, which exists *only* there. That
  line needs qualifying before someone prunes the file that overturned the lesson.
- **Consider recording the token counts alongside.** A one-line header comment, or a row in a small
  table, giving total and live-rule tokens plus the score it earned. § 6a needed exactly those two
  numbers, and re-deriving them needs the file *and* a running server.
- **Cheap extension:** when a test round is archived to `reference/test_archive/`, note which prompt
  file produced it. `run_tests.py` already writes the prompt's basename into each record header, but
  not its version, so an archived round cannot currently be tied to an exact prompt state.

### 6g. The discriminating test for the `b_mid` corruption, if it is judged worth a round

Two events is thin. If you want to know whether it is real, the cheap version is to re-run
**`b_mid` at 3,800 and 4,500 only** (2 runs, ~5 min) — a zero noise floor means a repeat that
reproduces `[[CONTINGENTS]]`/`[[CONTINGENCY]]` proves determinism, not stability, and a repeat is
therefore *not* informative on its own. The informative version is `a_mid` with filler B's
*vocabulary* swapped into filler A's register, or filler B placed at a third position, to separate
"register" from "position." I did not run either; both are outside what was asked.

---

## 7. What this did not establish

Stated explicitly, because the flat curve invites over-reading.

1. **Format only. Content was not measured at all.** `score.py` was never invoked; there is no
   `_expected` map in play. `set_p6_outside` is direct evidence that content can shift materially
   while format stays perfect — it wrote `[[CONTENTS]] none` over a furnished view. **A content
   curve against prompt length is the obvious next experiment and this one does not substitute for
   it.** If length costs anything below 5,000 tokens, this is where it would show.
2. **Two prompts, two roles.** `describer_setting` (locked v5, 8 flat fields) and `fl2va` (3-field
   contract). Not the whole prompt set, and both are *simple* relative to `describer_style`, which
   is where the historical degradation actually happened.
3. **`describer_frame` — the prompt closest to the line at 3,705 — was not tested**, because it has
   no `validate.py` role, and giving it one requires the repeating-sub-block work already logged
   on the TODO. The prompt that motivated the concern is the one prompt still unmeasured.
4. **Filler is a proxy for prompt growth, and an imperfect one.** § 4 shows it. Real growth is live
   rules; every number here is about material the model may ignore.
5. **One run per cell.** Mitigated unusually well — the byte-identical baselines mean a single run
   is a much stronger sample than usual on this server — but a cell is still one sample of one
   prompt shape, and `L-ONE-RUN-IS-A-SAMPLE` has not been repealed.
6. **Not tested past 5,000 tokens**, deliberately, per the handoff's instruction not to chase a
   break past ~6,000. Where the real cliff is remains unknown; only that it is above 4,982 for
   these two prompts.
7. **The `b_mid` result is 2 events.** Too few to characterise, and the register explanation is
   unverified (§ 6g).
8. **v4's failure could not be replicated, and the reason is not knowable.** v3 vs v4 was run (§ 6a):
   no content is lost in v4 that v3 keeps, and p1 drops the lamp in both. But the upstream chain has
   changed since session 3, so this neither confirms nor refutes the original attribution — it shows
   the replication is no longer available. My first causal story for v4 was wrong and is retracted in
   § 6a; `L-CAUSAL-STORIES-ARE-WEAK` caught me on my own report.
9. **The `describer_style` 3,740 → 3,883 → 4,054 ladder is not explained by this experiment**, and it
   is now the *only* surviving evidence for any ceiling. I can say it was not inert length; I cannot
   say it was rule density rather than the specific rules' semantics, because those were never
   separated — and v4 shows semantics alone is sufficient to break a prompt. **The three prompt
   states behind that ladder no longer exist**, so it cannot be re-measured (§ 6f).
10. **The image-vs-text length asymmetry is 6 cases and ~6%**, and does not grow with padding.
11. **One server config, one model.** Everything here is contingent on it, including
   `--image-min-tokens 2048`.

---

## Files in this directory

All kept, nothing deleted. Every number above is re-derivable from the run files.

| file | what it is |
|---|---|
| `REPORT.md` | this report |
| `scores.txt` / `scores.json` | `collect.py` output, human and machine readable |
| `filler_a.txt` / `filler_b.txt` | the two filler corpora, with their design constraints written in as comments |
| `pad.py` | builds padded copies to exact token targets via the live tokenizer; `--verify` re-counts |
| `gen_cases.py` | generates all 28 case files from the repo's own tests |
| `verify.py` | the four instrument checks (pure insertion · token window · noise floor · server config) |
| `signature.py` | the two signatures `validate.py` cannot see; `classify_tokens` is the § 6d candidate |
| `split_run.py` | splits a run file by case-id prefix, since `validate.py h3` has no `--id-prefix` |
| `drive.py` | batch driver with the handoff's stop conditions and the 4h wall enforced in code |
| `collect.py` | scores every run and builds the tables above |
| `manifest.json` | every padded prompt's measured token count and filler share |
| `plan.json` / `state.json` | generated run inventory; per-run timings and latency references |
| `prompts/` | the 30 padded prompt copies |
| `cases/` | the 28 generated case files |
| `runs/` | 28 concatenated run files + per-case files, isolated from the repo's `runs/` |
| `logs/` | per-run harness stdout, plus `server_props.json` |

`logs/` also holds `fl2va_3daef42.txt` and `fl2va_68909d9.txt`, the two `fl2va.txt` states extracted
from git history for the § 6a audit, plus their line-ending-normalised copies used for the v3→v4 diff.

**Nothing outside this directory was created or modified by me.** `run_tests.py --outdir` was pointed
here throughout, so the repo's `runs/` still holds the main thread's `look_*`/`st_*` files untouched.
`archive_run.py` was never invoked. No commit was made.

**One file outside it was added by the user, mid-session, and it matters:**
`reference/retired/prompts/fl2va_v4.txt`. It is the **only copy in existence** — and because
`reference/` is gitignored (§ 6f) it **cannot be committed as things stand**, so it currently has no
backup of any kind. It overturned the project's most-cited lesson. Preserving it needs a `.gitignore`
change, not a `git add`; that is a decision for the user, so I have not made it.

`git status` is clean because the file is ignored, **not** because nothing was added — worth knowing,
since the usual check would not have shown it.

## Reproducing

```bash
python .claude/experiments/bloat/pad.py           # 30 padded prompts, +/-25 tokens
python .claude/experiments/bloat/gen_cases.py     # 28 case files
python .claude/experiments/bloat/verify.py        # instrument checks
python .claude/experiments/bloat/drive.py base_1 base_2 a_end_3800 ... img noimg
python .claude/experiments/bloat/collect.py       # the tables in this report
```
