# H3 prompt-rewriter build system — Phase 0

Single-source assembly for the MiniMax H3 rewriter system prompts, so mode
differences are **recorded decisions** rather than undocumented drift.

## Layout

| File | Description |
|---|---|
| blocks/ | shared blocks with {{SLOT}} placeholders|
| modes/\<mode\>/ | mode-specific prose (preamble, reference-image, examples, closing)|
| manifests/ | per-mode JSON: block order, variant choices, slot values, rationale notes|
| dist/ | build output — this is what goes into the ComfyUI node widgets|
| build/ | build.py, validate.py|
| tests/ | JSON files that define development tests (for use with run_tests.py)|

## Build

```bash
python3 build/build.py            # all modes -> dist/
python3 build/build.py --verify   # build + diff against reference/
python3 build/build.py l2va       # one mode
```

Output matches the locked convention: **CRLF line endings, no trailing newline.**
A slot set to `null` deletes its whole line, which is how mode-inapplicable rules
(e.g. T2VA has no alignment-suppression bullet) drop out cleanly.

## Verification status

| Mode | Result |
|---|---|
| t2va | byte-identical to reference |
| i2va | identical except one stray double-blank-line before `FIDELITY`, normalised to a single blank |
| l2va | identical except the four approved restorations (below) |

L2VA restorations applied — and **only** these:

- **1a** closing "Now rewrite the user's input below…" line (mode-appropriate anchor clause)
- **1b** `non_diegetic_music` banned-words list + "(radio, phone, live instruments)"
- **1c** `overall_soundscape` exemplars, split back into two bullets
- **1d** on-screen text "(signs, banners, subtitles)"

Deliberate L2VA divergences **preserved**, with rationale in `manifests/l2va.json`:

- carry-over-the-cut guidance stays removed (model handled cross-cut lines inconsistently)
- `land_on_last_frame` duration variant stays (single-shot default keeps the graph's
  alignment `[Shot N]` deterministic)
- `APPEAR_CLAUSE` drops "first" — no known rationale; kept as-is rather than making an
  untested change during a refactor

## Validator

```bash
python3 build/validate.py runs.txt --strip-alignment
```

Parses the concatenated test-run files from the ComfyUI loop and prints per-case
PASS/FAIL. `--strip-alignment` removes the graph-injected alignment line before
checking, so it doesn't read as a contract violation.

Checks: field labels exact / ordered / once each · reply begins with the first field ·
no fences, `User:`, or `<think>` · `[Shot 1]` untimestamped · sequential shot numbers ·
`At MM:SS.mmm,` present · timestamps strictly increasing and inside the stated duration ·
`<d>` balanced, non-empty, `[Language]`-tagged, not split across a cut · voiceover phrase
followed by a lips-closed statement · banned mood words in `non_diegetic_music` ·
(warn) cut phrase mid-shot.

**It checks format, not semantics.** All five Round 2 L2VA cases pass, including the
thumbs-up direction inversion — that failure is a content error and still needs eyes.

## Adding a mode (FL2VA, REF2VA)

1. Add `modes/<mode>/` prose files.
2. Add `manifests/<mode>.json` — reuse shared blocks, add slot values, add a variant
   block only when the rule genuinely differs.
3. Record *why* in the manifest's `notes`.
