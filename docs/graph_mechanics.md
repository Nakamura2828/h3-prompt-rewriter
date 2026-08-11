# Graph-injected mechanics

The deterministic pieces the consuming graph must supply: alignment lines, and the FL2VA landing
clause. This is `L-OFFLOAD-BOOKKEEPING` in practice — values the model is never asked to produce,
because anything it is asked to track is something it can get wrong.

**Status: implemented in `scripts/run_tests.py` only.** Still needs porting into whatever ComfyUI
graph eventually consumes these prompts — tracked in `.claude/TODO.md`. REF2VA has **no**
alignment line; see `docs/REF2VA_architecture.md`.

Moved out of `.claude/CLAUDE.md` in session 8.

## FL2VA composer (session 4)

Graph-injected alignment line, verbatim from
`official_VIDEO_PROMPT_WRITING_GUIDE_base_en.md` §2.1 — first line of the final prompt, one
blank line, then `integrated_multimodal_description:`:

- I2VA: `For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.`
- FL2VA: `How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video.`
  (FL2VA's own wording drops the `<>`/`[]` brackets I2VA/L2VA use elsewhere — that's the spec,
  not a typo.)
- L2VA: `How the reference pictures align with the target video — <Picture 1> (from [Shot N]) aligns with the S.SS-second mark of the target video.` (single picture only.)
- `N` = actual final shot index. `S.SS` = duration to exactly two decimal places.

FL2VA landing clause — sourced from MiniMax's own official ComfyUI "Prompt Guide" node
(confirmed not content-adaptive), appended after the model's own last sentence in
`integrated_multimodal_description`, before `overall_soundscape:`: **"The shot lands exactly
on `<Picture 2>`."** The model is banned from writing its own version
(`prompts/fl2va.txt` OUTPUT CONTRACT).

Both implemented in `scripts/run_tests.py` (`alignment_line()`, `insert_fl2va_landing()`,
`last_shot_number()`) via a per-case `"align": "i2va"|"fl2va"|"l2va"` field — still needs
porting into whatever ComfyUI graph eventually consumes these prompts. `fl2va.txt` is now also
folded into the block/manifest build system alongside t2va/i2va/l2va (`manifests/fl2va.json`,
`modes/fl2va/`) — rebuilding all four modes produces zero diff. `describer_frame.txt` and
`fl2va_delta.txt` stay standalone: different prompt shape (structured image-description, not
the three-field H3 contract), no shared sub-components to factor out. See the REF2VA roadmap
in the current handoff (`.claude/handoffs/`) for the full reasoning.
