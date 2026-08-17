# Validator — `scripts/validate.py`

> **There are two failure pipelines and they must not be conflated.**
>
> | script | answers | needs an answer key? |
> |---|---|---|
> | `scripts/validate.py` | *Is the record well formed?* Fields present, ordered, once each; no reserved characters; closed vocabularies hold. | no |
> | `scripts/score.py` | *Did the model say the right thing?* Compares fields against the test file's `_expected` map. | yes |
>
> `validate.py` **cannot see content** — a record naming the wrong medium, the wrong person or the
> wrong place is perfectly well formed and passes every check here. That is what `score.py` and
> `docs/image_inventory.md` are for.
>
> Only `score.py`'s counts feed the adjudication thresholds in `.claude/CLAUDE.md`; format failures
> are reported separately and are never part of `F`. `score.py` also honours the `CONTESTED` /
> `UNSCORABLE` markers, so an adjudicated case drops out of the denominator instead of being
> re-litigated every round — and it prints the contested rate, because a rising one means the
> vocabulary is asking for a distinction the images don't support. **`CONTESTED` rulings are
> provisional and expire when the vocabulary changes; `UNSCORABLE` ones don't.**
>
> ```bash
> python scripts/score.py tests/describer_style.json runs/run-*.txt
> python scripts/score.py tests/describer_style_sweep.json <run> --fields MEDIUM   # coarse only
> ```

Format subcommands and what each one checks. Moved out of `.claude/CLAUDE.md` in session 8.

## Validator (`scripts/validate.py`) — format subcommands

**The format is always named explicitly** (session 5). This project produces several output
shapes that share nothing but the record wrapper, and "should we use validate.py? no, it's for
something specific" kept coming up. There is now no default format:

```bash
python scripts/validate.py h3        runs/run-*.txt --strip-alignment
python scripts/validate.py describer runs/run-*.txt --role character
python scripts/validate.py ref2va    runs/run-*.txt        # not built yet
```

**Roles are data, not branches (session 6).** `DESCRIBER_ROLES` maps a role to
`{fields, closed, drift, no_digits, not_found, style_warn, style_allow, atmos_field, no_launder,
derived}`, and what
counts as a wrong field is **derived** from that table rather than hardcoded. That matters for the
roles still to come: the old hardcoded list contained `PALETTE` and `LIGHTING`, both of which
`describer_style` legitimately owns, so it would have rejected that role's own fields. Refactor
verified by re-running the character checker over
`reference/test_archive/REF2VA/Describer-Character-v1.txt`: identical except the drift line now
names its field.

### Wrong fields: an allow-list, not a deny-list (session 13)

`classify_tokens()` enumerates every `[[...]]` token actually present and sorts the ones this role
does not own into three buckets, because they mean different things:

| bucket | meaning | example |
|---|---|---|
| `foreign` | a real field of **another** role — the record is bleeding across passes | `[[MEDIUM]]` in a `setting` record |
| `corrupted` | nothing owns it, but it is one edit from one of ours | `[[DISTINGISHING]]` → `[[DISTINGUISHING]]` |
| `invented` | made up outright | `[[CONTINGENCY]]` |

**This replaced a deny-list, and the distinction is the whole point.** `foreign_fields()` returned
(every role's fields ∪ the frame describer's) minus this role's, so it could only reject a name
some *other* role owned. An invented token is in no role's list, so it was never compared against
anything and **passed silently** — which is how `[[CONTINGENCY]]` got through the session-13 bloat
run. Enumerating what is present subsumes the old check rather than sitting beside it.

The `corrupted` bucket is the valuable one: emitting the right *content* under a near-miss token is
the silent failure signature described in `L-PROMPT-TOKEN-BUDGET`. Re-running the archived
4,054-token derivation round now names `[[DISTINGISHING]]` ×3 and `[[DEFINING]]` ×1 directly,
where before they surfaced only as the *absence* of the real field. Pass/fail counts on every
archived run are unchanged — the new errors land on records that were already failing.

`[[SUBJECT NOT FOUND]]` is exempt here and validated by its own rules below, so a role that may not
emit it still reports that once rather than twice.

### Printed-name laundering: a cross-field check with no fixed vocabulary (session 29)

`object` is the only role that reproduces on-thing lettering (`[[TEXT]]`), and it has a
persistent defect where a printed name gets carried into the model's own identification of the
thing elsewhere — `"HEATH"` on a computer case becoming `[[LABEL]] the beige and blue Heathkit
computer`. The prompt has banned this by name since session 22 and it kept happening anyway, so
`no_launder` gives it a mechanical FAIL rather than leaving it to be judged by eye every round: a
`(source field, target fields)` pair on a role's spec — `('TEXT', ('KIND', 'LABEL',
'DISTINGUISHING', 'DEFINITION'))` for `object`, `None` for every other role.

Unlike every other closed-vocabulary check here, there is no fixed list to check against — what
counts as a banned word is *derived per record* from that record's own `[[TEXT]]` field, so it
gets its own small helpers (`_quoted_words`, `_capitalized_words`, `_launder_hit`) rather than
reusing `age_terms()`. Two things they specifically guard against, both found live rather than
designed in advance:

- **A capitalised word that is itself a legitimate quoted reproduction of `[[TEXT]]`.**
  `[[DEFINITION]]` and `[[DISTINGUISHING]]` are allowed to quote `[[TEXT]]` content verbatim (it's
  in their own field rules, and the prompt's own worked example does it), so `_capitalized_words`
  strips quoted spans before scanning. Found on a real record: a TV in `ob_notfound_slippers`
  legitimately quoted a channel watermark it had (separately, and outside this check's scope)
  mis-attributed to its own casing — `[[DEFINITION]] ... the words "Global HD" printed on the
  casing` should not fail just because `[[TEXT]]` also says `"Global"`.
- **A short word that coincidentally sits inside a longer, unrelated printed word.** The
  substring match needed for `'Heathkit'` ⟵ `'HEATH'` cuts both ways unless both sides clear a
  length floor (`LAUNDER_MIN_LEN = 4`) — found via regression against the archived
  `Describer-Object-v2.txt`, where `'No'` (from the legitimate quote `"No job too small"`)
  matched inside `'gnome'`.

Verified against a live 44-case round, all four archived historical `describer_object` rounds, and
the session-28 archive: the six known laundering cases all still catch, and nothing else in any of
those six files does.

### `vocab_terms()` — the AGE extractor generalised for COLOUR, plus `score.py`'s first derived field (session 30)

`age_terms(line, vocab)` became `vocab_terms(line, vocab, *, hyphen_boundary=True, order='length')`
— a rename plus two real bug fixes shipped together (per `.claude/TODO.md`'s explicit instruction:
"not a bare rename"), each a **parameter** rather than a behaviour change in place, since both
`score.py` and the character-age format check already depend on the old behaviour:

- `hyphen_boundary=True` (the AGE default, unchanged) treats a hyphen as a word boundary, so
  `middle-aged` cannot match a bare `aged`. `hyphen_boundary=False` (COLOUR's need) does not — so
  `yellow` is now correctly pulled out of `mustard-yellow`, where the old unconditional guard made
  every compound colour term extract as nothing (`L-A-SILENT-FALLTHROUGH-IS-WORSE-THAN-A-CRASH`).
- `order='length'` (the AGE default, unchanged) yields matches in longest-term-first order — the
  same order subsumption is computed in, so `young adult` still correctly beats bare `adult`.
  `order='position'` (COLOUR's need) yields in the order terms actually appear in the line instead
  — `order='length'` is a systematic bias toward whichever colour has the longest name, which would
  have made COLOUR's "rank 1" mean "longest name" rather than "mentioned first."

Both AGE call sites (the character `[[APPEARANCE]]` bracket check; the `same:`-group drift
cross-check) now pass `hyphen_boundary=True, order='length'` explicitly. Regression-gated
byte-identical against the two archived AgeDrift rounds, `Describer-Character-v1.txt`, and
`Describer-Setting-v5.txt`/`Describer-Style-v4c-s18-enriched.txt` (drift check, non-AGE vocab).

**`DESCRIBER_ROLES` gained a `derived` key**, `{field name: (source field, vocab, vocab_terms()
kwargs, aliases)}` — declares a field extracted from another field's free text rather than written
literally, the same shape `no_launder` gave cross-field checking. `object`'s only entry: `COLOUR`
off `[[MATERIAL]]`. `score.py` imports `DESCRIBER_ROLES` for the first time (previously only
`validate.py`'s own format checks read it) and merges every role's `derived` dict into one flat
lookup, since a derived field name is unique across roles today. `read_run()` computes a derived
field's value via `vocab_terms()` instead of literal `[[FIELD]]` lookup — **the first field this
project has ever content-scored without the model writing it out literally.** Only rank 1 (the
first extracted, alias-mapped term) is scored; the full ranked extraction is diagnostic-only,
printed next to any miss on a derived field so a rank-2 match is visible without new ground-truth
machinery.

**`aliases`** maps a defensible synonym to a canonical vocabulary term (`COLOUR_ALIASES` in
`validate.py`: `beige`/`tan` → `light brown`, `cream`/`off-white` → `white`, `navy` → `dark blue`),
applied after extraction so every derived value handed to the scorer is always a vocabulary word.
Added only once empirically confirmed necessary (`ob_van`'s real dominant colour, `"a faded beige
or cream colour"`, was invisible to extraction and fell through to a secondary mention) — not
pre-emptively. `mustard`/`mustard-yellow` is deliberately **not** an alias: it was ruled a genuine
miss against `brown`, not a defensible synonym, and mapping it would silently launder the one real
content defect this round found.

**`score.py`'s comparison gained one directional loosening**, `_field_match(field_name, got, alt)`:
for a derived field only, a modifier-qualified extraction satisfies its bare-hue expectation
(`dark grey` credits against expected `grey`) — never the reverse, and never across two *different*
modifiers, so `light brown` still does not satisfy plain `brown`. Applied consistently everywhere
a field value is compared against an expectation (the main per-field verdict, and the
accept-set-control collapse check), so the two paths cannot silently diverge.

`h3` — the three-field contract (t2va/i2va/l2va/fl2va). Field labels exact / ordered / once
each · reply begins with the first field · no fences, `User:`, or `<think>` · `[Shot 1]`
untimestamped · sequential shot numbers · `At MM:SS.mmm,` present · timestamps strictly
increasing and inside the stated duration · `<d>` balanced, non-empty, `[Language]`-tagged, not
split across a cut · voiceover phrase followed by a lips-closed statement · banned mood words in
`non_diegetic_music` · (warn) cut phrase mid-shot.

`describer` — structured `[[FIELD]]` records. Fields present/ordered/once each · reply begins
with the first field · no `<` or `>` · no fences or `User:` · no foreign, corrupted or invented
`[[...]]` tokens ·
closed-vocabulary fields hold a permitted value (`SUBJECT_KIND`, `SETTING_KIND`) · exactly one
term from the closed age vocabulary, human or animal per `[[SUBJECT_KIND]]` · no digits where
the role bans them · (`object`) no printed name laundered from `[[TEXT]]` into an identification
field · `[[SUBJECT NOT FOUND]]` only with a SUBJECT line, never `none`/`N/A`,
always last · (warn) rendering-style words · (warn, setting) a transient condition in
`[[DEFINITION]]`. `--role` selects everything; add a role by adding a row to `DESCRIBER_ROLES`.

**Gotcha when adding a role.** `DESCRIBER_ROLES` is no longer `role -> [field names]`; it is
`role -> {…}`. Adding a role is still one row, but it is a **dict**, and `drift` is a
`(field, callable)` pair where the callable takes the record text and returns the vocabulary to
read that field with. (Carried over from the session-6 handoff, which was the only place this
was written down.)

**Cross-case drift check**: cases in a group named `same: ...` must produce the same age
bracket. That is the REF2VA identity-drift check, driven entirely by the group name — no new
harness field.

**Both check format, not semantics.** All test cases may pass, including visual or logical
mistakes; those are content errors and still need eyes and/or reasoning to catch.

`parse_records()` now skips `##### group #####` banners, which were previously validated as
malformed records — one guaranteed spurious FAIL per group in every grouped run. Verified
against all 32 archived runs: real-record verdicts and errors are unchanged, only the banner
failures disappear (and the case label printed is now the case id rather than the input's
first line).
