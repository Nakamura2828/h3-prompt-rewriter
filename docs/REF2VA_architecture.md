# REF2VA architecture

Reference document for the full-reference (REF2VA) mode. Agreed session 5 (2026-08-10).
Source of truth for the spec itself is
`reference/official_H3_references/official_VIDEO_PROMPT_WRITING_GUIDE_ref_en.md`; section
numbers below (§) refer to it.

REF2VA takes up to 9 reference images with heterogeneous roles, plus audio references, and
produces a **six-section** output in this order (§1):

```
subject_definitions
summary
retention_analysis
detailed_description
overall_soundscape
non_diegetic_music
```

Two things make it unlike T2VA/I2VA/L2VA/FL2VA:

1. **It carries a label system.** `<Subject N>` / `<Picture N>` / `<Audio N>` must keep the same
   meaning across all six sections (§2). That is bookkeeping, and lesson 6 says bookkeeping
   belongs in code.
2. **The guide's own section order puts a whole-output judgment third.** `retention_analysis`
   summarises how each reference fared, but sits *before* the description it judges — exactly
   the failure that forced `[[CAST NOT FOUND]]` to the end of the frame describer (lesson 4).

## Pipeline

```
per image slot (1..9)   describer by role       -> structured [[FIELD]] record
code                    label roster            -> <Subject N>/<Picture N>/<Audio N>, task types
composer pass A         roster + records + user -> detailed_description
                                                   overall_soundscape
                                                   non_diegetic_music
code                    subject_definitions     -> from records + roster + pass A's (Sx) bindings
composer pass B         roster + pass A output  -> summary body
                                                   retention_analysis markers + rationales
code                    assemble                -> six sections in guide order
```

The local LLM node accepts one image per call, so per-image describer passes were forced
anyway. The two-pass composer split is the lesson-4 fix: pass A writes the description, pass B
judges it, and code puts the sections back into guide order.

Pass A's three fields are the existing three-field contract with `integrated_multimodal_
description` renamed to `detailed_description` — so pass A belongs in the `blocks/`/`modes/`/
`manifests/` build system as a fifth mode, reusing `30_fidelity`, `50_style_camera`,
`60_speakers_dialogue`, `70_soundscape`, `80_music` as-is. Two block edits will be needed at
that point, both slot conversions with no content change: `10_output_contract.txt` hardcodes
the three field labels, and `80_music.txt`'s last line names `integrated_multimodal_description`
literally. Pass B is small and stays standalone.

`describer_*` prompts stay standalone — confirmed session 4, unchanged by this design.

## Label assignment — deterministic, in code

**`<Picture N>` is the image slot index, always.** Whether a picture gets its own
`subject_definitions` / `retention_analysis` line depends only on its role: §2.2 says an image
that merely defines a character, scene, costume, or style is cited *inside* the subject's
definition with no standalone entry. The guide's complete example (§7) shows this — `<Picture 1>`
through `<Picture 4>` all appear only inside `<Subject N>` lines.

| user-facing role | describer prompt | label | standalone entry? |
|---|---|---|---|
| character / person | `describer_character.txt` | `<Subject N>` | no — cited in the subject line |
| setting / environment | `describer_setting.txt` (v2) | `<Subject N>` | no |
| object / prop / clothing | `describer_object.txt` *(later)* | `<Subject N>` | no |
| style | `describer_style.txt` *(later)* | `<Subject N>` | no |
| first frame / keyframe / last frame | `describer_frame.txt` (v8) | `<Picture N>` | **yes** |
| storyboard | `describer_frame.txt` (v8) | `<Picture N>` | **yes** |

`<Subject N>` is a running counter in slot order over the subject-producing roles.

A selector maps the ~12 user-facing role labels onto these ~5 describer prompts. Separate
per-role prompts, not one role-table prompt: this model reads a field list as an obligation
(lesson 3) and will not reliably suppress listed fields.

**v1 constraint — one asset produces at most one subject.** The guide permits one asset to
supply several subjects, and one subject to draw on several assets (§2.1). If the user wants
the character out of a keyframe reused as a subject, they add that image a second time with
`role: character`. Known limitation, not a bug.

## Task-type prefix — deterministic, in code

`summary` opens with a square-bracketed task-type prefix (§3). Derive it from the roles present,
dedupe, join with ` + `, and emit in this canonical order — which reproduces all three of the
guide's own examples (`[video continuation + keyframe completion]`, `[video editing + audio
reuse]`, `[reference generation + audio reference]`):

```
video editing -> video continuation -> keyframe completion -> reference generation
              -> audio reuse -> audio reference
```

v1 reachable set (video deferred): `keyframe completion`, `reference generation`,
`audio reuse`, `audio reference`.

Note §3's warning: the mere presence of a video or audio asset does not create a task type.
A video supplying only camera movement or rhythm is `reference generation`, not `video editing`.

## Audio slots

`<Video N>` is **deferred entirely** for v1 — the model cannot watch video, and a
user-typed structural description of one has no clear payoff yet. `<Audio N>` is in, because a
voice-timbre reference for a character is genuinely useful.

Each audio slot carries a role dropdown, free text, and (for timbre) a bound subject slot. The
role drives both the task type and the `retention_analysis` marker (§4.2) with no model
judgment:

| audio role | task type | retention marker |
|---|---|---|
| copy — complete soundtrack | `audio reuse` | `fully_copy` |
| copy — partial / single layer | `audio reuse` | `partially_copy` |
| voice-timbre reference (bound to a subject) | `audio reference` | `reference` |
| music-style reference | `audio reference` | `reference` |
| beat / continuity reference | `audio reference` | `reference` |

A voice-timbre entry reads `<Audio 1> is the voice-timbre reference for <Subject 1> (S1).`
The `(S1)` comes from the **target video's** global speaker order (§2.4, §5.4), which only
exists once pass A has written the dialogue — so code fills it by scanning pass A's output for
that subject's `<Subject N> (Sx)` binding. **This is why `subject_definitions` is assembled
after pass A, not before.**

Code must **not** emit `(Sx)` into `retention_analysis` — §5.4 forbids it outright.

Which audible layer an audio reference is described in is fixed by §6: ambience and sound
effects belong in `overall_soundscape`, audience-only score in `non_diegetic_music`. One asset
providing both gets a line in each.

## `retention_analysis` — split between code and pass B

Code builds each line's prefix; pass B supplies only `marker - rationale`:

- Subjects: `<Subject 1> (appears in [Shot 1], [Shot 3]): ` — the shot list is scanned out of
  pass A's `detailed_description` by finding each `<Subject N>` occurrence and its enclosing
  `[Shot N]`. `run_tests.py`'s `SHOT` regex already does the parsing half of this.
- Pictures: `<Picture 2> ([Shot 1] first frame): ` — straight from the slot's role.
- Audio: `<Audio 1>: ` — no parenthetical.

§4.2's closing rule matters and belongs in pass B's prompt: choose a marker only *within* the
reference role already defined for that label, and do not treat newly added actions,
backgrounds, or plot events in the target video as losses of reference fidelity.

## No alignment line

Confirmed against both guides: REF2VA has **no** graph-injected "aligns with" line. The
`<Picture N>` anchoring happens inside `detailed_description` in natural phrasing — "the shot
begins from `<Picture 1>`", "the shot ends on `<Picture 3>`" (§5.3). The `alignment_line()` and
`insert_fl2va_landing()` machinery in `run_tests.py` stays untouched and is simply unused by
REF2VA cases.

## Other spec points to carry into the prompts

- `detailed_description` opens with the style in one or two sentences **before** `[Shot 1]`,
  unlike T2VA where style is written after it (§5.2).
- Target length for generation tasks is 350–500 English words (§5.2).
- Do not introduce new reference labels in `summary` (§3).
- Write `[unclear]` for unintelligible reused dialogue rather than guessing (§5.4).

## Build order

1. **`describer_character.txt`** — session 5. Identity-only (no POSE/POSITION/FRAMING); see
   `CLAUDE.md` for the field list and the age-bracket vocabulary.
2. **`describer_setting.txt`** — session 6. Eight fields, with everything transient quarantined
   in `[[ATMOSPHERE]]` and barred from `[[DEFINITION]]`, so the spliced subject-definition
   sentence holds by day and by night. See `CLAUDE.md`.
   `describer_object.txt` and `describer_style.txt` remain; **`style` is blocked on input
   variety** — see `docs/image_inventory.md` for the corpus and the shopping list.
3. Composer pass A as a fifth build-system mode; pass B standalone.
4. Roster / task-type / assembly code, and a `ref2va` validator subcommand.
5. Port the whole thing into the ComfyUI graph, along with the FL2VA alignment/landing logic
   that currently lives only in `run_tests.py`.
