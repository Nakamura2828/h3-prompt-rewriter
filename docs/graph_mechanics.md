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

## What the graph must REMOVE — `[[SUBJECT NOT FOUND]]` on a SUBJECT-less call

Added session 22, user ruling. Everything above is something the graph **injects**; this is the
first thing it must **delete**.

**The rule: if the call supplied no `SUBJECT:` line, strip any `[[SUBJECT NOT FOUND]]` line from
the describer's output before anything downstream sees it.** Implemented as
`strip_unsolicited_not_found()` in `scripts/run_tests.py`, beside `alignment_line()` and
`insert_fl2va_landing()`, and it needs porting into the ComfyUI graph with them.

**Why it is code and not a rule.** `describer_object` emitted the line on SUBJECT-less cases in
three consecutive rounds, each time copying whichever SUBJECT-shaped phrase sat nearest in the
prompt — first an empty value, then `"the yellow jumpsuit"` (lifted from a rule that had just been
added to fix something else), then `"the red kettle"` (lifted from a worked example). Deleting the
stolen phrase only moved the theft to the next candidate. `setting` lost the same fight across
v1/v2/v3 and answered it by removing the line from that role entirely.

`object` cannot take that answer, because it genuinely needs the judgement — an image holds many
discrete things, so "nothing here matches what you asked for" is real information, and the model
gets it **right** when a `SUBJECT:` line is actually present. What it cannot do is decide whether
one was present. That is `L-OFFLOAD-BOOKKEEPING` exactly: the caller knows for certain, so the
model should never have been asked.

**Scope is deliberately narrow.** When a `SUBJECT:` line IS present, the output is left completely
untouched — including a tail line, including a wrong one. Only the unsolicited case is deleted.

**`validate.py` still treats an unsolicited line as an ERROR, and that is intentional.** The check
now guards the *consumer*: a graph that forgets this step will trip it. Read a format score for
this role knowing the harness has already applied the strip — `run_tests.py` prints how many lines
it removed, and that raw rate is the number worth watching.
