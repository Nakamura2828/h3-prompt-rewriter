# Build system — blocks, modes, manifests

How the four H3-contract prompts (t2va/i2va/l2va/fl2va) are assembled from `blocks/`,
`modes/<mode>/` and `manifests/<mode>.json`, and the verification record against the
pre-build-environment reference set. Moved out of `.claude/CLAUDE.md` in session 8.

`fl2va` was folded into this system in session 4; `describer_*` and `fl2va_delta` stay
standalone. See `docs/graph_mechanics.md` for that reasoning.

## Verification status (t2va/i2va/l2va vs pre-build-env reference)

| Mode | Result |
|---|---|
| t2va | byte-identical to reference |
| i2va | identical except one stray double-blank-line before `FIDELITY`, normalised to a single blank |
| l2va | identical except the four approved restorations (below) |
| fl2va | not in the pre-build-env reference set (didn't exist then); folded into the block/manifest system session 4 — rebuilding produces zero diff against the committed `prompts/fl2va.txt` |

**`--verify` reproduces this table as of session 13.** It previously died on `fl2va`:
`build.py` read `reference/pre_build_env_canonical_prompts/<mode>.txt` unconditionally, but there
is no `fl2va.txt` there and never was — by construction, per the last row — so a
`FileNotFoundError` killed the run and left the check effectively dead. It now skips modes with no
canonical baseline and reports all four.

**It still exits 1, and that is expected rather than a second bug.** Only `l2va` is exempted from
setting the failure code, so `i2va`'s single normalised blank line — approved, and recorded in the
table above — makes the run non-zero every time. `--verify` is therefore a report to read, not a
gate to wire into anything, unless that exemption is widened deliberately.

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
