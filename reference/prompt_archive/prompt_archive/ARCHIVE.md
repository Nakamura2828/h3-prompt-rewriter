# The prompt archive

Every distinct system-prompt state that still exists anywhere in this project, in one place,
numbered, with what it measured and where it came from — plus an explicit record of the six
states that are **gone**.

Assembled in session 13 by hashing every blob of every prompt path at all 34 commits and every
candidate file in the working tree, then grouping by content. It was built because the session
had just proved the cost of not having it: a result from session 3 could not be reproduced, and
the prompt that anchors this project's most-cited rule turned out to be unrecoverable.

- `<label>.txt` — 29 prompt states, LF line endings
- `MANIFEST.json` — every state with tokens, md5, commits, lineage, status
- `verify.py` — integrity, drift against `prompts/`, and coverage

## How to use it

```bash
python reference/prompt_archive/verify.py                    # is the archive still true?
python scripts/token_budget.py reference/prompt_archive/*.txt   # the whole length history
```

`verify.py` is the load-bearing one. A snapshot of a *living* file goes stale silently, so it
re-checks that every state marked `live` still matches `prompts/`, and that every file in
`prompts/` matches some archived state. A drift is not corruption — it means `prompts/` moved on
and **a new numbered state needs archiving**.

## What "vN" means here

Two rules, both because guessing either way destroys information.

**1. Never invent a number the project already assigned.** `describer_setting` has exactly one
state in git, but the project calls it **v5** — v1–v4 were iterated in-session and never
committed. Renumbering it `v1` would break the mapping to
`reference/test_archive/REF2VA/Describer-Setting-v1..v5.txt`, which is now the only surviving
evidence those rounds ever happened.

**2. This is a tree, not a line.** `fl2va` v4 was reverted, and the shipping prompt descends from
**v3**, not v4 — proved by diff: v4's one added rule appears in neither v3 nor the current file.
A flat renumbering would assert a lineage that does not exist. `MANIFEST.json` carries a `parent`
per state; `status` is one of:

| status | meaning |
|---|---|
| `live` | byte-identical to its file in `prompts/` right now |
| `superseded` | was live, later replaced on the main line |
| `reverted` | tried and rolled back — a dead branch that never shipped |
| `pre-build` | predates the block/manifest build system; a comparison input |

Exactly one label, `fl2va_v5`, was assigned by this archive rather than by the project. It is
flagged as such in the manifest.

## Every surviving state, by token count

Counts are from the live llama-server tokenizer under the parameters in CLAUDE.md, so they are
directly comparable with `L-PROMPT-TOKEN-BUDGET` and the session-13 bloat curve.

| tokens | state | status | notes |
|---|---|---|---|
| **4,054** | `describer_style_v2-derivation` | reverted | **LOST — no file.** The only real degradation on record |
| 3,883 | `describer_style_v2` | superseded | largest surviving state; 43/45 format |
| 3,740 | `describer_style_v2-compressed` | superseded | 45/45 — best format score recorded |
| 3,713 | `describer_frame_v7` | superseded | **above the 3,700 line, shipped fine for sessions** |
| 3,705 | `describer_frame_v8` | live | |
| 3,634 | `describer_frame_v6` | superseded | |
| 3,591 | `fl2va_v4` | reverted | |
| 3,561 | `fl2va_v5` | live | |
| 3,548 | `fl2va_v2` | superseded | larger than v3 — v2→v3 was a net cut |
| 3,499 | `fl2va_v3` | superseded | common ancestor of v4 *and* v5 |
| 3,200 | `describer_frame_v4` | superseded | |
| 3,179 | `fl2va_v1` | superseded | |
| 3,133 | `describer_frame_v5` | superseded | smaller than v4 — another net cut |
| 3,007 | `i2va_v1` | live | |
| 3,007 | `i2va_pre-build` | pre-build | same count, different content |
| 2,939 | `describer_setting_v5` | live | |
| 2,868 | `describer_frame_v3` | superseded | |
| 2,861 | `describer_style_v1` | superseded | |
| 2,657 | `l2va_v1` | live | |
| 2,613 | `describer_frame_v2` | superseded | |
| 2,584 | `describer_style_class_v3` | live | pass B of the split |
| 2,555 | `l2va_pre-build` | pre-build | |
| 2,496 | `fl2va_delta_v2` | reverted | |
| 2,407 | `describer_character_v1` | live | post-calibration |
| 2,364 | `fl2va_delta_v4` | reverted | |
| 2,277 | `fl2va_delta_v3` | reverted | |
| 2,165 | `t2va_v1` | live | identical to its pre-build canonical |
| 2,127 | `describer_frame_v1` | superseded | |
| 2,015 | `fl2va_delta_v1` | live | oldest state still shipping |
| 1,876 | `describer_style_look_v3` | live | pass A of the split |

**The split does not reduce total load.** `look` + `class` sum to **4,460** tokens — more than the
3,740 single prompt they replaced. It buys headroom *per call*, which is the only budget that
binds.

## Version trees

```
t2va          pre-build ═══ v1 (live)          identical content: build reproduced it exactly
i2va          pre-build ──> v1 (live)
l2va          pre-build ──> v1 (live)

fl2va         v1 ──> v2 ──> v3 ──┬──> v4   (reverted, dead branch)
                                 └──> v5   (live)

fl2va_delta   v1 (live) ──> v2 ──> v3 ──> v4   (all three reverted; v1 never replaced)

describer_frame    v1 ─> v2 ─> v3 ─> v4 ─> v5 ─> v6 ─> v7 ─> v8 (live)

describer_setting  [v1] ─> [v2] ─> [v3] ─> [v4] ─> v5 (live)      [..] = LOST
describer_character  [v1-precalibration] ─> v1 (live)
describer_style    v1 ─> v2 ──┬──> [v2-derivation]  (reverted, LOST)
                              └──> v2-compressed ──> v3 split ─┬─> look_v3  (live)
                                                              └─> class_v3 (live)
```

`fl2va_delta` is the one to notice: **the oldest state is the live one.** v2, v3 and v4 were each
tried and abandoned.

## The six states that no longer exist

No copy exists in git, in the working tree, or anywhere the user has checked. Each row's
*evidence* is what still proves it existed — in every case an archived test run, never the prompt.

| state | what was lost | evidence |
|---|---|---|
| `describer_style_v2-derivation` | **4,054 tokens.** The *only* prompt that ever produced the corrupted-field-token signature (39/45 format, correct content under mangled `[[FIELD]]` names) | `test_archive/REF2VA/Describer-Style-v2-targeted-iteration1-derivation-rule.txt` · `docs/describers.md:288` |
| `describer_setting_v1` | 25/26, five atmosphere leaks + example-bleed. The atmosphere quarantine was designed against this text | `test_archive/REF2VA/Describer-Setting-v1.txt` |
| `describer_setting_v2` | The canonical `L-KNOW-WHEN-TO-STOP` case: one added paragraph cost 25/26 → 21/26. **The paragraph itself is gone** | `test_archive/REF2VA/Describer-Setting-v2.txt` |
| `describer_setting_v3` | The mechanical-gate attempt, 23/26, "diagnostically decisive" | `test_archive/REF2VA/Describer-Setting-v3.txt` |
| `describer_setting_v4` | 25/26, tying v5 while failing a *different* case — half the pair `L-ONE-RUN-IS-A-SAMPLE` rests on | `test_archive/REF2VA/Describer-Setting-v4.txt` |
| `describer_character_v1-precalibration` | The closed age vocabulary *without* apparent-age spans; proved a closed list alone doesn't stop drift | `test_archive/REF2VA/Describer-Character-AgeDrift-BeforeCalibration.txt` |

**The first row is the expensive one.** `L-PROMPT-TOKEN-BUDGET` rests on five points, and the
session-13 audit found only one that actually degraded: 4,054. That prompt cannot be re-run,
re-measured, or diffed against the 3,740 version that scored 45/45. The bloat experiment padded
its way to 4,982 tokens without breaking anything — and could not test the one prompt its whole
question was about.

Probably lost but unproven: the T2VA/I2VA/L2VA prompts behind the earlier test rounds
(`test_archive/L2VA/` alone holds Rounds 1.3–5, against two surviving `l2va` states). Whether each
round changed the prompt is not recoverable, so they are not listed as individual losses.

## What building this corrected

| claim | where | correction | status |
|---|---|---|---|
| 3,561 tokens is "fl2va v3" | `scripts/token_budget.py:41` | 3,561 is **v5** (current). v3 is **3,499**, v4 is **3,591** | **fixed** in `b4191f4` |
| every `reference/retired/` file is byte-identical to a reachable blob | `.claude/CLAUDE.md` | true for `retired/`, but `pre_build_env_canonical_prompts/i2va.txt` and `l2va.txt` were on **no ref, ever** — for one day they existed in exactly one place | **fixed** in `b4191f4` (now tracked) |
| `reference/` is tracked | `.claude/CLAUDE.md` | `.gitignore:57` ignores `reference/*` by exception list; `pre_build_env_canonical_prompts/` was not on it | **fixed** in `b4191f4`; `prompt_archive/` still needs adding |
| `dist/fl2va_v3.txt` never existed | session 13, earlier | **wrong.** It did. `git rev-list --objects` prints each blob once under a single path, so shared-content files vanish from that listing. `git ls-tree` per commit is the reliable enumeration | corrected here |
| `describer_frame` is at the budget line | `docs/describers.md` | v8 is 3,705 but **v7 was 3,713** and shipped without trouble. v7→v8 *removed* two rules and got 8 tokens smaller | open — more evidence against the line |

**`python scripts/build.py --verify` crashes**, and there is *no missing file to recover*.
`fl2va` did not exist when the build system was written and at first did not use it at all, so a
pre-build canonical copy of it was never made. `--verify` iterates every mode and reaches for one
anyway. The fix is a guard that skips modes with no canonical baseline, not a hunt for a lost
file — recorded here so nobody goes looking.

It does mean that directory is a script *input*, not merely an archive, which collides with the
standing TODO to delete it: removing it would leave `--verify` with nothing to check against on
all three modes, not just `fl2va`. The archive now holds all three states
(`t2va_v1`, `i2va_pre-build`, `l2va_pre-build`), so the *content* is safe either way — but
deleting the directory means retiring `--verify` or repointing it here.

`prompts/describer_style.txt` is **deliberately** still in the live directory: it is
`v2-compressed`, the pre-split baseline the in-progress `describer_style` work is measured
against. `verify.py` notes it rather than failing on it, so that a genuinely forgotten file and a
deliberately retained one look different.

## The rule going forward

The reason `describer_frame` has a complete v1–v8 history and `describer_setting` has only v5 is
that the frame work predates this repo and was iterated by hand, keeping every exchange. Git made
that *feel* unnecessary and quietly made it worse: committing only the final state of a session's
iteration is what lost v1–v4.

**Archive a prompt state whenever it stops being the live one, and whenever it produces a scored
test round.** Concretely, a state earns a slot if any of these is true:

1. **It shipped** — it was the live file for any commit.
2. **It was scored** — a run of it is in `reference/test_archive/`. A run whose prompt is gone is
   half a record; every loss above is one of these.
3. **It was reverted** — *especially* then. Four of the six lost states are reverts, and a revert
   is the most informative thing in the history: it is the only direct evidence of what made
   things worse.

The mechanics are already here: add the file, extend `CURATED` in
`.claude/experiments/prompt_archive/build_archive.py`, re-run it, and run `verify.py`. The
`CURATED` gate fails loudly on any state it does not recognise, so a new prompt state cannot be
archived without someone deciding what it is called and what it descends from.

One `.gitignore` addition is still needed for this to be durable:

```
!reference/prompt_archive/
```

Without it, `reference/*` swallows this directory and the archive shares the exact exposure it was
built to fix. (`!reference/pre_build_env_canonical_prompts` was added in `b4191f4`.)

## Maintenance

Regenerate with `census.py` → `measure.py` → `build_archive.py` (in
`.claude/experiments/prompt_archive/`). Everything mechanical is derived; only `CURATED` and
`MISSING` in `build_archive.py` hold decisions, and they are commented with the reasoning.

**Line endings:** every archived file is LF and `md5_lf` is over those bytes. `core.autocrlf=true`
here with no `.gitattributes`, so a *fresh checkout* yields CRLF copies whose MD5 will not match
the manifest. Normalise to LF before comparing — a CRLF mismatch once made a one-line `fl2va`
change look like a 261-line whole-file rewrite.
