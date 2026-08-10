# H3 Prompt Rewriter

System prompts that rewrite plain-English descriptions into well-formed MiniMax H3
video-generation prompts — one system prompt per generation mode (T2VA, I2VA, L2VA,
FL2VA, and eventually REF2VA), assembled from shared blocks so that differences between
modes are recorded decisions rather than undocumented drift.

Built for use as the system prompt fed to a locally-hosted vision-language model inside
a ComfyUI graph (or an equivalent LLM node), which then hands its output to the actual
H3 video-generation node.

## Layout

| Path | Description |
|---|---|
| `blocks/` | shared prompt blocks with `{{SLOT}}` placeholders |
| `modes/<mode>/` | mode-specific prose (preamble, reference-image, examples, closing) |
| `manifests/` | per-mode JSON: block order, variant choices, slot values, rationale notes |
| `prompts/` | current, ready-to-use system prompts — this is what goes into the LLM node's system prompt field. Includes both `build.py`'s output (t2va/i2va/l2va) and standalone hand-maintained prompts (image describer, FL2VA delta, FL2VA composer) |
| `scripts/` | `build.py`, `validate.py` |
| `tests/` | JSON case files run by `run_tests.py` against a local OpenAI-compatible server |

## Build

```bash
python3 scripts/build.py            # all modes -> prompts/
python3 scripts/build.py --verify   # build + diff against reference/
python3 scripts/build.py l2va       # one mode
```

Output convention: **CRLF line endings, no trailing newline.** A slot set to `null`
deletes its whole line, which is how mode-inapplicable rules (e.g. T2VA has no
alignment-suppression bullet) drop out cleanly.

## Testing

```bash
python run_tests.py tests/cases_fl2va_full.json
python scripts/validate.py runs/run-*.txt --strip-alignment
```

`run_tests.py` sends each case to a local llama.cpp (or other OpenAI-compatible) server
and writes results to `runs/`. `validate.py` checks the output format (field labels,
ordering, timestamps, tag balance, banned words) — it checks structure, not semantics.

## Adding a mode

1. Add `modes/<mode>/` prose files.
2. Add `manifests/<mode>.json` — reuse shared blocks, add slot values, add a variant
   block only when the rule genuinely differs.
3. Record *why* in the manifest's `notes`.
