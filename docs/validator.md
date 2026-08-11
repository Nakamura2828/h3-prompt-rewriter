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
`{fields, closed, drift, no_digits, not_found, style_warn, style_allow, atmos_field}`, and the
foreign-field list is **derived** — (every role's fields ∪ the frame describer's) minus this
role's own — rather than hardcoded. That matters for the roles still to come: the old hardcoded
list contained `PALETTE` and `LIGHTING`, both of which `describer_style` will legitimately own,
so it would have rejected that role's own fields. Refactor verified by re-running the character
checker over `reference/test_archive/REF2VA/Describer-Character-v1.txt`: identical except the
drift line now names its field.

`h3` — the three-field contract (t2va/i2va/l2va/fl2va). Field labels exact / ordered / once
each · reply begins with the first field · no fences, `User:`, or `<think>` · `[Shot 1]`
untimestamped · sequential shot numbers · `At MM:SS.mmm,` present · timestamps strictly
increasing and inside the stated duration · `<d>` balanced, non-empty, `[Language]`-tagged, not
split across a cut · voiceover phrase followed by a lips-closed statement · banned mood words in
`non_diegetic_music` · (warn) cut phrase mid-shot.

`describer` — structured `[[FIELD]]` records. Fields present/ordered/once each · reply begins
with the first field · no `<` or `>` · no fences or `User:` · no fields foreign to this role ·
closed-vocabulary fields hold a permitted value (`SUBJECT_KIND`, `SETTING_KIND`) · exactly one
term from the closed age vocabulary, human or animal per `[[SUBJECT_KIND]]` · no digits where
the role bans them · `[[SUBJECT NOT FOUND]]` only with a SUBJECT line, never `none`/`N/A`,
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
