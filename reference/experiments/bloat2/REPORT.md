# Instruction density: substituting live rules for inert filler at constant length

**Task:** `.claude/handoffs/SIDE_HANDOFF_bloat_calibration2.md`
**Run:** 12 runs · 358 model calls · 0.50 h · no stop condition tripped
**Server:** unchanged throughout, verified against CLAUDE.md's documented sampler settings
(`temp 0.0 · top_k 40 · top_p 0.9 · repeat_penalty 1.05`), `n_ctx` 16,384. No flag was altered, so
these numbers are comparable with round 1 and with the rest of the project's archive.

---

## Headline

**Live instruction does not degrade this model either.** Holding total system-prompt length fixed
at ~5,000 tokens and trading inert filler for real rules — from 2,239 up to 3,805 live-rule tokens,
**1.7× the control and 1.24× the densest prompt the project ships** — produced **no monotone
degradation in format or content, in either arm.** The ladder was placed *on* the band where the
project's only recorded degradation happened, not merely past it (§ 2b).

This is the handoff's *"If nothing moves"* branch, and it was named in advance as a real result:

> A flat curve to L4 would be a **real and valuable result**, not a failure. It would mean the
> live-rule metric is dead alongside the total-token one, and that **one prompt's three-point
> ladder is the only ceiling evidence the project has**.

That is where we now are. Per the handoff I did **not** escalate past ~3,800 live-rule tokens and
did **not** author increasingly aggressive rules to force a break.

**Three findings do the work, and the third is the one I did not expect:**

1. **Every failure observed this round has a round-1 precedent produced with ZERO added rules.**
   Four of the five failure modes occur in round 1's *unpadded or inert-padded* cells — including
   the duplicated-field signature that `L-PROMPT-TOKEN-BUDGET` treats as diagnostic. These are
   stably marginal cases being perturbed, exactly as round 1 concluded (§ 3).
2. **The arms disagree in a way that kills both candidate metrics.** N (novel constraints) accrued
   more failures than R (restatements) — but they are concentrated in **one cell**, and the cell
   with the **most** rules scored **better** than the cell below it. Non-monotone in both arms
   (§ 2).
3. **The model does not drop the new rules. It obeys them almost perfectly.** A direct compliance
   measure — added after the first scored round, and the most informative thing here — finds
   **one** real violation across 9 cells. At 3,782 live-rule tokens carrying **49 added rule units
   and 21 mechanically-checkable constraints**, compliance was **perfect** (§ 5). "Adding a rule
   costs a rule" is not what these prompts do at these magnitudes.

**Bottom line for the project:** the live-rule metric proposed in round 1 § 6a has now been tested
directly and **does not predict degradation**. It should not be built into `token_budget.py`.
`describer_style`'s three-point ladder remains the only ceiling evidence the project has, and it is
now the *only* thing left standing after two rounds and 1,166 model calls.

---

## 1. Method, and what was held constant

The manipulation is **substitution, not addition**: every cell lands on the same total, and only the
split between live rules and inert filler moves. Length is therefore controlled *by construction*
and needs no argument.

| | setting probe | fl2va probe |
|---|---|---|
| prompt | `prompts/describer_setting.txt` (2,939 tok, 700 examples, **2,239 live**) | `prompts/fl2va.txt` (3,561 tok, 863 examples, **2,698 live**) |
| test | `tests/describer_setting.json`, 26 images | `tests/cases_fl2va_full.json`, 6 composer cases |
| format | `validate.py describer --role setting` | `validate.py h3` |
| content | item counts in `[[STRUCTURE]]`+`[[CONTENTS]]`+`[[DISTINGUISHING]]` | action coverage, 12 elements |
| cells | L0 ×2, R ×4, N ×4, NF ×1 = 11 runs | 9 levels inside **one** chained run |

**Where the material goes.** Two insertions, both at existing section boundaries, neither splitting
a section. Rules go **mid-prompt** under an `ADDITIONAL RULES` heading — identical heading in both
arms, so heading text is not a confound. Inert filler A (round 1's corpus, reused byte-for-byte)
tops up at the **end**, after `EXAMPLES` and before the closing task line.

At L0 the rules block is empty, so **L0 is round 1's `a_end` 5,000 cell exactly.**

### The ladder as built — total constant, live-rules varied

| cell | live-rules | total | rule units | inert |
|---|---|---|---|---|
| `setting` L0 | 2,239 | 4,982 | 0 | 2,743 |
| `setting` R2700 / N2700 | 2,678 / 2,699 | 4,993 / 4,993 | 15 / 12 | 2,315 / 2,294 |
| `setting` R3100 / N3100 | 3,098 / 3,102 | 4,984 / 4,988 | 29 / 25 | 1,886 / 1,886 |
| `setting` R3400 / N3400 | 3,396 / 3,406 | 4,983 / 4,993 | 38 / 34 | 1,587 / 1,587 |
| `setting` **NF3400** | **3,392** | **4,979** | **8** | 1,587 |
| `setting` R3800 / N3800 | 3,785 / 3,782 | 4,979 / 4,976 | 51 / 49 | 1,194 / 1,194 |
| `fl2va` L0 | 2,698 | 4,980 | 0 | 2,282 |
| `fl2va` R3100 / N3100 | 3,102 / 3,089 | 4,986 / 4,995 | 14 / 10 | 1,884 / 1,906 |
| `fl2va` R3400 / N3400 | 3,379 / 3,383 | 4,994 / 4,998 | 24 / 18 | 1,615 / 1,615 |
| `fl2va` **NF3400** | **3,393** | **4,982** | **4** | 1,589 |
| `fl2va` R3800 / N3800 | 3,789 / 3,805 | 4,975 / 4,991 | 38 / 31 | 1,186 / 1,186 |

**Total tokens span 4,975–4,998 across all 18 cells** — a 23-token spread on a 5,000-token target,
against a live-rule range of 1,566 tokens. Length is genuinely not the variable.

### Instrument verification — `verify2.py`, six checks, all pass

1. **Pure insertion.** All 18 padded prompts differ from their source by exactly the intended
   insertions (two for a rules cell, one for L0) and nothing else — no line of the original added,
   removed, reordered or altered, checked with `difflib.SequenceMatcher`.
2. **Total window.** All 18 within ±25 of 5,000, re-counted live.
3. **Live-rule window.** All 18 within ±25 of target, **re-derived from the files** rather than
   trusted from the build: strip the end-filler insertion, re-count, add back the source's live
   count.
4. **L0 == round 1.** Byte-identical to round 1's `a_end__5000` prompt for **both** probes.
5. **Noise floor: ZERO.** The two L0 runs are byte-identical.
6. **Server config** unchanged.

**A bonus, and it is the strongest determinism result the project has.** Because L0 reproduces
round 1's prompt exactly, its outputs can be compared with round 1's stored run — a different
session, hours later, after the server had been used for other work:

> **26/26 outputs byte-identical to round 1's `primary__a_end_5000`.**

Session 12 found determinism holds for a *replayed run* but not a *replayed case*. This extends the
replayed-run result **across sessions**, which no previous measurement had shown.

**Context headroom.** `n_ctx` 16,384; a 5,000-token prompt + 2,048 image floor + ~900 of composer
input + 2,048 `max_tokens` ≈ 10,000. Nothing was truncated.

---

## 2. The curve

### Format

| live-rules | total | R | N | NF |
|---|---|---|---|---|
| **2,239** *(L0 ×2)* | 4,982 | 26/26 · 26/26 | 26/26 · 26/26 | — |
| ~2,690 | 4,993 | 26/26 | 26/26 | — |
| ~3,100 | 4,984–4,988 | 26/26 | 26/26 | — |
| ~3,400 | 4,979–4,993 | 26/26 | 26/26 | **26/26** |
| ~3,783 | 4,976–4,979 | 26/26 | **25/26** | — |

| live-rules | total | R | N | NF |
|---|---|---|---|---|
| **2,698** *(L0 ×2)* | 4,980 | 6/6 · 6/6 | 6/6 · 6/6 | — |
| ~3,095 | 4,986–4,995 | 5/6 | 5/6 | — |
| ~3,380 | 4,982–4,998 | 6/6 | **3/6** | **6/6** |
| ~3,797 | 4,975–4,991 | 6/6 | 5/6 | — |

**Read the fl2va N column.** 5/6 → **3/6** → 5/6. The cell with *more* rules (N3800: 31 units,
3,805 live) scores **better** than the cell below it (N3400: 18 units, 3,383 live). A ceiling does
not behave like that. The same non-monotonicity appears in R, whose only failure is at its
*lowest* level.

### Content

| probe | L0 | R ladder | N ladder | NF |
|---|---|---|---|---|
| `setting` items | 207 | 207 · 200 · **194** · 200 | 215 · 220 · 220 · 219 | 215 |
| `fl2va` coverage /12 | 10 | 10 · 10 · 10 | 9 · 10 · 9 | **8** |

**These movements are read against a null band computed from round 1's own data**
(`null_calibration.txt`), which is the single most useful thing built this round. Round 1 varied
inert length with live-rules pinned at 2,239, so all 24 of its cells are nulls for *this* round's
manipulation:

- **Item count: null band 200–217 against a 210 baseline** (spread 17, sd 4.6). Anything inside
  roughly ±10 items is movement this metric already produces *with no rule change at all.*
- **Action coverage: null band 10–11 out of 12** across all eight round-1 cells.

Against that: R's dip bottoms at 194 (−13, just outside), N sits at +8 to +13 (just outside the
other way), and coverage stays inside the band except NF3400's 8/12. **Nothing here is monotone and
nothing is large.** The one consistent pattern — R always at or below L0, N always above — is
discussed in § 4.

---

## 2b. How far past the working range is this, really?

Added because "1.7× the control" flatters the result: `describer_setting` is one of the *least*
dense prompts in the repo, so that multiple is measured from a low base. Measured live, every
prompt currently in `prompts/`:

| prompt | total | examples | **live-rules** | live share |
|---|---|---|---|---|
| `describer_style` | 3,740 | 668 | **3,072** | **82%** |
| `fl2va` | 3,561 | 863 | **2,698** | 76% |
| `describer_frame` | 3,705 | 1,344 | **2,361** | 64% |
| `describer_setting` | 2,939 | 700 | **2,239** | 76% |
| `i2va` | 3,007 | 939 | 2,068 | 69% |
| `describer_style_class` | 2,584 | 615 | 1,969 | 76% |
| `l2va` | 2,657 | 741 | 1,916 | 72% |
| `describer_character` | 2,407 | 508 | 1,899 | 79% |
| `t2va` | 2,165 | 860 | 1,305 | 60% |
| `describer_style_look` | 1,876 | 614 | 1,262 | 67% |
| `fl2va_delta` | 2,015 | 902 | 1,113 | 55% |

**Rules are the bulk of every prompt** — 55–82% live, median ~72%. Two things follow.

**1. The honest multiple is 1.24×, not 1.70×.** Against the densest prompt shipping today
(`describer_style`, 3,072 live) the ladder's top cell is only 24% beyond, not 70%.

**2. But the ladder was placed ON the degradation band, not merely past it.** The only degradation
the project has ever recorded runs 3,072 (clean, 45/45) → 3,215 (43/45) → 3,386 (39/45 + corrupted
tokens). This round's cells land as follows:

| `describer_style` history | live | this round's cells at that level |
|---|---|---|
| v2-compressed — **45/45, best on record** | 3,072 | L2: 3,089 · 3,098 · 3,102 |
| v2 — 43/45 | 3,215 | *(not sampled — falls between L2 and L3)* |
| v2-derivation — **39/45 + corrupted tokens** | 3,386 | **L3: 3,379 · 3,383 · 3,392 · 3,396 · 3,406** |
| — | — | L4: 3,782 · 3,785 · 3,789 · 3,805 |

**Five cells sit within 20 tokens of 3,386** — the count at which `describer_style` lost six cases
and began emitting corrupted field tokens — spanning two prompts and all three arms. They produced
**zero corrupted tokens**, no content movement outside the null band, and near-perfect rule
compliance (§ 5).

So the *quantity* axis is genuinely covered, and "we did not push hard enough" is not the
explanation for the flat curve. What separates this round from `describer_style` is not how many
rule tokens are present but **what the rules do** — see § 9 item 1, which is the live gap.

**A third consequence, for § 8a.** Because live share is 55–82% with a median near 72%, live-rule
tokens are close to **collinear** with total tokens across the real corpus (live ≈ 0.72 × total).
A metric that nearly duplicates the one it replaces cannot discriminate much more than it does.
The historical points it *did* order correctly hinged on a single outlier — `describer_frame`'s
unusually heavy 36% examples block. That is a thin basis for a guard, independent of this round's
null result, and it reinforces the recommendation not to build one.

---

## 3. Every failure this round already happened in round 1, with no rules added

This is the load-bearing table. Round 1's cells added **no live instruction at all**, so any
failure mode appearing there is not evidence about rule density.

| round 2 failure | mode | round 1 precedent | round 1 condition |
|---|---|---|---|
| `c_N3400_p1` | duplicated `overall_soundscape` + `non_diegetic_music` | `c_4000_p1`, **identical error** | inert padding, live-rules constant |
| `c_N3800_p5` | duplicated audio fields | `c_base_p5`, `c_base2_p5` | **unpadded baseline** |
| `s_N3800` `set_miya` | duplicated `[[DEFINITION]]` | `set_miya` in both baselines | **unpadded baseline** |
| `c_N3400_p6` | `melancholic` in `non_diegetic_music` | `c_base_p6`, `c_base2_p6`, 3900, 4000 | **unpadded baseline** |
| `c_*_p4` | `melancholic` | **none — p4 never failed in round 1** | — |

Four of five are known-marginal. The duplicated-field signature in particular is the one
`L-PROMPT-TOKEN-BUDGET` calls diagnostic, and **round 1 produced it under pure inert padding and in
the unpadded baseline.** It cannot carry a rule-density interpretation.

**The one genuinely new failure is `p4`'s `melancholic`, and it does not discriminate the arms.**
It appears at R3100 *and* N3100 — both arms, same level — then vanishes at R3400/R3800 and persists
at N3400 before vanishing at N3800. Non-monotone, in both arms, on a mood-word check that fires on
a single adjective choice.

### The case × cell matrix

```
cell         p1    p2    p3    p4    p5    p6
L0            .     .     .     .     .     .
L0b           .     .     .     .     .     .
R3100         .     .     .  MOOD     .     .
R3400         .     .     .     .     .     .
R3800         .     .     .     .     .     .
N3100         .     .     .  MOOD     .     .
N3400       DUP     .     .  MOOD     .  MOOD
N3800         .     .     .     .   DUP     .
NF3400        .     .     .     .     .     .
```

Four of six cases never fail at any level in either arm. All the movement is in p1, p4, p5 and p6 —
and p1, p5 and p6 are precisely the cases that failed in round 1.

### Corrupted and invented field tokens: zero

Round 1's most interesting secondary finding was two corrupted tokens (`[[CONTINGENTS]]`,
`[[CONTINGENCY]]`), both in one arm. **This round produced none at all** — 0 corrupted, 0 invented,
0 foreign across all 286 setting records, at up to 3,782 live-rule tokens.

`crosscheck.py` confirms `signature.py` and `scripts/validate.py` agree on **every one of the 286
records**, so neither implementation has drifted since `1322269`. (The two known-benign differences
— tuple order, and `validate.py`'s `[[SUBJECT NOT FOUND]]` exemption — are normalised there.)

---

## 4. Content: where the arms differ, and why it is not a ceiling

The one consistent arm difference is directional, not degrading:

- **R (restatement) always writes less**: item totals 207 · 200 · 194 · 200, output length
  ×0.963–×0.98 of L0.
- **N (novel constraints) always writes slightly more**: 215 · 220 · 220 · 219, length
  ×0.998–×1.03.

**The obvious artefact was checked and ruled out.** My own N rule says to use a comma where an em
dash would go, and the item metric counts comma-separated fragments — so N's rise could have been
manufactured by my own manipulation. It was not: **L0's outputs contain zero em dashes**, so that
rule is genuinely vacuous and cannot be the mechanism. Comma counts move with length, not against
it (L0 275, N3400 293, R3400 261).

**And the cases that move are the cases that always move.** Of R3400's eight largest item losses,
**five are among the top losers in round 1's inert-padded cells** (`set_miya`, `set_mountain_rain`,
`set_p3_first`, `set_p3_last`, `set_stage`). This is round 1's own conclusion replicated: *length
collapse is case-driven, not length-driven* — and now, not rule-driven either.

The most defensible reading of the R dip is that **restating "write plain declarative phrases, no
full-sentence prose" makes the model terser** — the rules working, not failing. I am not asserting
that; it is a causal story of exactly the shape `L-CAUSAL-STORIES-ARE-WEAK` warns about, and I have
no discriminating test for it.

**Content and format diverge, which is the round-1 lesson holding.** `NF3400` has **perfect format
in both probes** and the **worst coverage in the experiment** (8/12). A format-only experiment would
have called that cell the cleanest in the round.

---

## 5. The measurement I did not plan, and the one that matters most

After the first scored round, `describer_setting` at 3,406 live-rule tokens emitted the word
"various" — which the very prompt it was running under bans by name. That made the right dependent
variable obvious.

`L-PROMPT-TOKEN-BUDGET`'s actual claim is that **adding a rule silently costs a rule.** Format score
and item count are both indirect proxies for that. `compliance.py` measures it directly: take the
constraints actually present in a cell's prompt, and count how many that cell's own output breaks.

| cell | live | rule units | checkable rules | broken |
|---|---|---|---|---|
| `setting` N2700 | 2,699 | 12 | 11 | 0 |
| `setting` N3100 | 3,102 | 25 | 17 | 0 |
| `setting` N3400 | 3,406 | 34 | 18 | **1** — "various" |
| `setting` N3800 | 3,782 | **49** | **21** | **0** |
| `setting` NF3400 | 3,392 | 8 | 3 | 0 |
| `fl2va` N3100 | 3,089 | 10 | 9 | 0 |
| `fl2va` N3400 | 3,383 | 18 | 15 | 0 |
| `fl2va` N3800 | 3,805 | **31** | **19** | **0** |
| `fl2va` NF3400 | 3,393 | 4 | 2 | 0 |

**One real violation across nine cells.** The densest cell in the experiment — 49 added rule units,
21 independently checkable constraints, 3,782 live-rule tokens — broke **none of them**.

Matching is word-boundaried and deliberately conservative, so this **undercounts**: rules needing
judgement (e.g. "write the colour before the material") are excluded rather than guessed at. Two
apparent violations were investigated and are **false positives against my own rule's carve-out** —
both were "a small framed photograph", a physical object on a shelf, which that rule's text
explicitly permits. The checker was corrected to implement the carve-out; the correction is in the
code with the reason.

---

## 6. Which metric survives

**Neither. That is the deliverable.**

| candidate | verdict |
|---|---|
| **total tokens** | already dead (round 1). Nothing degrades to 4,998. |
| **live-rule tokens** (round 1 § 6a, bracket ~3,100) | **now tested directly and dead.** Both probes cross the 3,100 bracket and reach ~3,800 with no monotone degradation. The R arm — pure live-rule tokens, zero new constraints — is clean at every level. |
| **number of distinct constraints** | **not supported, though it was the last hope.** The count-vs-tokens split points that way in isolation: at matched tokens, `NF3400` (4–8 rule units) is clean in both probes while `N3400` (18–34 units) is the worst cell in the round. **But the N ladder itself contradicts it** — N3800 carries *more* constraints than N3400 and scores better, on both probes. And § 5 shows the constraints are being *obeyed*, which is what a count-based ceiling would have to violate. |

The count reading deserves one more sentence because it is the only one with any support: it rests
on **two cells** (one per probe), against a non-monotone four-point ladder in the same arm and a
near-perfect compliance result. That is not enough, and the honest statement is that the N/NF
contrast is **a lead worth one cheap follow-up** (§ 8), not a finding.

---

## 7. The rules, quoted

The handoff requires the N rules in full so that a degradation can be judged as load rather than
semantics. Since there was **no degradation to explain**, the fuller value here is the *design*, so
both are recorded. Complete text lives in `rules_{r,n,nfew}_{setting,fl2va}.txt`, each file
carrying its design constraints and — more usefully — the candidates I **rejected** and why.

**The N rules are novel, additive, and vacuously satisfied by a correct output**, so their cost is
*reading and checking*, never editing content to comply. That is deliberate: a rule forcing a
content edit would move the content metric by construction, and the experiment would be measuring
its own manipulation. The handoff endorses exactly this shape ("banning a word that never appears,
requiring an ordering that already holds, prohibiting a unit nobody uses").

Representative `describer_setting` N rules (44 in the pool):

> - Never use the word "nestled" anywhere in your output. It is banned in every field, including inside a longer phrase such as "nestled against the wall".
> - Never write an em dash anywhere in your output. Use a comma where you would have used one, in every field without exception.
> - Never write "etc", "e.g.", or "i.e." anywhere in your output. Finish the list or leave the item out; those three forms are banned in every field.
> - Write whole numbers below ten as words rather than as digits: "three tall sash windows", never "3 tall sash windows". This applies in every field.
> - Never write a full stop inside [[STRUCTURE]], [[CONTENTS]], or [[DISTINGUISHING]]. Those three fields are comma-separated lists and take no sentence punctuation.
> - Never write a unit of weight or temperature. Kilograms, pounds, degrees, Celsius, and Fahrenheit are all banned anywhere in your output.
> - Never write the words "image", "photo", "photograph", "picture", or "frame" inside a field's value. Describe the place, never the thing the place was recorded on.

**Rules rejected while writing, each because it would have been a semantics manipulation wearing a
load manipulation's clothes** — this list is as much the method as the rules that survived:

| rejected | why |
|---|---|
| banning digits outright | the prompt *wants* counts ("three tall sash windows") |
| banning compass directions | "a south-facing window" is plausible; would cut content |
| banning "appears"/"seems" | would *remove* hedging and could **improve** the score |
| banning superlatives | "the largest window" is a plausible `[[DISTINGUISHING]]` |
| banning possessive apostrophes | the prompt's own `[[PLACE]]` example is "a ship's deck" |
| "list items largest first" | a real ordering constraint; would rewrite every field |

**`fl2va` is much more constrained, and that is itself worth recording.** Its output contract ruled
out most bans that were safe for `setting`: the semicolon (its own example output uses one), round
brackets (`(S1)`), angle brackets (`<d>`), digits (`[Shot 1]`), ALL-CAPS (`N/A`), the slash
(`N/A`), `?`/`!` and contractions and non-Latin characters (dialogue is preserved **verbatim** from
the user), and quotation marks (required for on-screen text). Its pool is 31 rules against
`setting`'s 44. **A tightly-specified output contract leaves less room for a genuinely inert novel
rule** — which is a small, real constraint on how far this method can be pushed.

The R rules are near-verbatim paraphrases of rules each prompt already contains — your call in
planning, over literal duplication, so the arm could not be made accidentally inert by trivial
compressibility or by `repeat_penalty 1.05`.

---

## 8. Recommendations — numbers, not edits

**Nothing below has been applied.** Every file named is one the handoff put out of bounds.

### 8a. `token_budget.py` — do NOT add the live-rule guard

Round 1 § 6b proposed reporting **live-rule tokens = total − `EXAMPLES`** as a second number, and
§ 6a's ~3,100 bracket as the line, sequenced explicitly behind this experiment:

> Sequencing: do not implement the live-rule guard before running § 6e. It is a post-hoc fit to six
> points, and the test that would justify it costs 13 minutes.

**That test has now run, and the answer is no.** Both probes cross 3,100 and reach ~3,800 live-rule
tokens with no monotone degradation, and the R arm is clean at every level. A guard on live-rule
tokens would fire on prompts this round shows to be fine. **Recommend dropping § 6b's live-rule
proposal.** It was a good hypothesis, cheaply tested, and it failed.

**A second, independent reason to drop it, which does not depend on this round's result at all:**
§ 2b shows live share across the real corpus is 55–82% (median ~72%), so live-rule tokens are close
to collinear with total tokens and cannot discriminate much better. The historical ordering that
motivated the metric rested on one outlier, `describer_frame`'s unusually heavy examples block.

### 8b. `NEAR` / `LINE` / `TOLERANCE` — round 1's numbers stand, with more support

Current: `NEAR 3500 · LINE 3700 · TOLERANCE 0.05 → OVER 3885`. Round 1 recommended:

```python
NEAR = 4000        # was 3500
LINE = 4300        # was 3700
TOLERANCE = 0.05   # unchanged -> OVER = 4515 (was 3885)
```

**Round 2 strengthens this and does not change the numbers.** `--check` currently fails a prompt at
3,885 while these two rounds together measured clean behaviour at **4,975–4,998 total tokens
carrying up to 3,805 live-rule tokens**. The recommended `OVER 4515` still sits below everything
measured clean, now with the stronger claim that the headroom is not merely inert.

Round 1's proposed code comment should be **revised**, though. It reads: *"these numbers say inert
length is cheap; they do not license adding 800 tokens of new rules to a 3,700-token prompt."* This
round added **1,566 tokens of live rules** with no degradation, so that caveat is now too strong.
Suggested replacement:

> These numbers were measured twice: once padding with inert filler (round 1) and once substituting
> real rules for that filler at constant length (round 2). Neither degraded below ~5,000 tokens.
> What is still **unmeasured** is a prompt whose rules *compete* — `describer_style`'s three closed
> vocabularies and ten fields — which is where the only surviving degradation was ever observed.

Round 1's suggestion to **drop `TOLERANCE`** and write `OVER = 4500` as its own constant still
stands; with `LINE` moved it does no work.

### 8c. `L-PROMPT-TOKEN-BUDGET` — one hypothesis to retire, one boundary to sharpen

The lesson's current text (rewritten session 13) names the live hypothesis and points here:

> The live hypothesis is **instruction density / rule count**, and it is what the next experiment
> tests.

It has now been tested. Suggested edits:

- **Record the result:** at constant ~5,000 total tokens, live-rule tokens were raised from 2,239 to
  3,805 (1.7×) on two prompts, in two arms plus a count-vs-tokens arm, 358 calls, zero noise floor.
  No monotone degradation in format or content, and **near-perfect compliance with up to 21
  independently checkable added constraints**.
- **Retire "instruction density / rule count" as the live hypothesis**, or downgrade it to the
  narrow form that survives: *competing* or *mutually-constraining* rules, which this round did not
  test — every N rule here was deliberately non-interacting.
- **Keep "adding a rule costs a rule" as a caution about rule SEMANTICS, not rule count.** `fl2va`
  v4 is still its cleanest demonstration: one line, 92 tokens, and the damage was the behaviour the
  line described.
- **Strengthen the failure-signature note with a warning.** The duplicated-field and corrupted-token
  signatures are real, but round 1 and round 2 together show they **occur in unpadded baselines and
  under inert padding**. Seeing one is not evidence of a budget problem. `set_miya` and `p5` produce
  it at the *unpadded* baseline.
- **The evidence base is unchanged and is one prompt.** After two rounds, `describer_style`'s
  3,072 → 3,215 → 3,386 live-rule ladder is still the only degradation on record, and its three
  prompt states no longer exist.

### 8d. Two live content bugs for the main project

Both are found by the coverage metric, both present at **every level of both rounds**, so neither is
caused by anything either experiment did:

1. **`p1`'s lamp** — the user says "turns on the lamp"; nothing in the composer's input corroborates
   it and the composer drops it. **Already on `.claude/TODO.md`.** One correction to how round 1
   framed it: the lamp is **marginal, not stably absent** — it appeared in 2 of round 1's 8 cells.
   So "the lamp appeared" is not on its own a signal.
2. **`p6`'s rabbit — apparently NOT logged, and it should be.** The user writes "her stuffed
   rabbit"; the composer drops the word in **7 of 8 round-1 cells and 9 of 9 round-2 cells** — 16
   of 17 measured cells across both rounds, at every prompt length and every rule density. And
   `fl2va.txt` contains a rule aimed at precisely this case:
   > When the user names an object and [[DELTA]] names it differently, use the USER's name. […] A
   > "stuffed rabbit" in the user's words is a stuffed rabbit, not a teddy bear.

   A rule that specific failing that consistently is worth a look on its own terms.

### 8e. The one cheap follow-up, if the N/NF lead is judged worth it

Everything above says stop. The single loose thread is § 6's count-vs-tokens contrast, which rests
on two cells. The discriminating test is **N-few at the other three levels** (2,700 / 3,100 / 3,800)
so the NF arm has a ladder instead of a point — **6 runs, ~15 minutes**, reusing everything in this
directory. If NF stays clean while N stays non-monotone, the count reading is dead too and the
matter is closed. I did not run it: the handoff caps the manipulation and this is a new arm, not a
repeat.

---

## 9. What this did not establish

Stated explicitly, because a flat curve invites over-reading in the other direction.

1. **Non-interacting rules only.** Every N rule was *designed* to be additive and vacuously
   satisfied, precisely so the arm would measure load and not semantics. **This round therefore says
   nothing about rules that compete with each other** — which is what `describer_style` has, and
   where the project's only surviving degradation lives. The narrow density hypothesis is untested,
   not refuted.
2. **The N-rule authoring confound cuts both ways.** The handoff warns that a badly-chosen rule
   breaks things by semantics. The mirror risk applies to a null result: rules chosen to be
   maximally inert may be **too easy**, and a genuinely inert rule may cost less attention than a
   real one. I consider the compliance result (§ 5) partial protection — the model demonstrably
   *processed* these rules rather than skipping them — but it is not proof.
3. **Two prompts, both simple.** `describer_setting` (8 flat fields, one two-value vocabulary) and
   `fl2va` (3-field contract). `describer_frame` remains untested — it has no `validate.py` role —
   and `describer_style`, the prompt that motivated all of this, was off limits as the live thread.
4. **One run per cell.** Mitigated unusually well — zero noise floor, plus 26/26 byte-identical
   reproduction across sessions — but a cell is still one sample of one prompt shape.
5. **Not tested past ~3,805 live-rule tokens or ~5,000 total**, deliberately, per the handoff.
   That is only **1.24× the densest prompt shipping today**, so the proven headroom above real
   working prompts is narrower than the 1.7×-the-control framing suggests. It does, however, cover
   the actual degradation band with five cells (§ 2b), which is the comparison that matters.
6. **The NF arm is one cell per probe.** See § 8e.
7. **`p4`'s `melancholic` is unexplained.** It is the only failure without a round-1 precedent, it
   appears in both arms at ~3,100, and it is non-monotone. I have no account of it beyond "marginal
   case", which is what round 1 said about its own flips.
8. **The content metrics are crude by design.** Comma-splitting over-counts an item containing a
   comma and under-counts two joined with "and"; coverage stems trade false positives for
   inflection-insensitivity. Both are read as differences against L0, never as absolute scores, and
   both are calibrated against a null band from round 1 — but neither is precise.
9. **The coverage metric has narrow dynamic range.** Two of its twelve elements (`p1:lamp`,
   `p6:rabbit`) are broken upstream at every level, so it effectively measures 10.
10. **One server config, one model**, including `--image-min-tokens 2048`.

---

## Files in this directory

Everything kept; every number above is re-derivable from the run files.

| file | what it is |
|---|---|
| `REPORT.md` | this report |
| `rules_{r,n,nfew}_{setting,fl2va}.txt` | the six rule pools, each with its design constraints and rejected candidates written in |
| `null_calibration.txt` | **null bands for both content metrics**, computed from round 1's runs |
| `pad2.py` | two-stage builder: rule block to a live-rule delta, filler top-up to a fixed total |
| `verify2.py` | the six instrument checks |
| `gen_cases2.py` | the 12 case files, from the repo's own tests |
| `drive2.py` | batch driver, round 1's stop conditions, own fresh `state.json` |
| `coverage.py` / `items.py` | the two content metrics |
| `compliance.py` | the direct "does it obey the new rules" measure (§ 5) |
| `crosscheck.py` | `signature.py` vs `validate.py` — agreement on all 286 records |
| `collect2.py` | scores every cell and builds the curve tables |
| `manifest.json` | per-cell measured totals, live-rule counts, rule text |
| `compliance.json` | per-cell compliance detail |
| `prompts/` · `cases/` · `runs/` · `logs/` | 18 padded prompts · 12 case files · 12 runs · harness output |

**Nothing outside this directory was created or modified.** `run_tests.py --outdir` pointed here
throughout, so the repo's `runs/` is untouched. Round 1's directory was read from — `filler_a.txt`,
`signature.py`, `split_run.py`, and its stored runs — and **never written to**, including its
`state.json`. `archive_run.py` was not invoked. No commit was made. `git status` should show only
the untracked `.claude/experiments/bloat2/` tree, since `.claude/` is gitignored.

## Reproducing

```bash
python .claude/experiments/bloat2/pad2.py         # 18 padded prompts, +/-25 on both axes
python .claude/experiments/bloat2/verify2.py      # six instrument checks
python .claude/experiments/bloat2/gen_cases2.py   # 12 case files
python .claude/experiments/bloat2/drive2.py s_L0 s_L0b            # the noise floor first
python .claude/experiments/bloat2/drive2.py s_R2700 ... f_img     # the ladders
python .claude/experiments/bloat2/collect2.py     # the tables in § 2
python .claude/experiments/bloat2/compliance.py   # the table in § 5
```
