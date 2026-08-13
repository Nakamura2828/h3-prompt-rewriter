# Retired tests

Superseded test files, kept because their `_expected` maps encode user rulings that took real
adjudication effort. **None of these should be run.** Each names what replaced it.

## `describer_style.json` — retired session 10

The original `describer_style` test, 39 cases. Probes distinctions the three-axis rebuild dropped
and covers none of the terms it added.

## `describer_style_targeted.json` (+ `gen_style_targeted.py`, `-BASELINE-s12.txt`) — retired session 17

45 images / 90 cases, enriched, gating on movement. Replaced by
**`tests/describer_style_sweep130.json`**, which covers all 130 images including every one of
these 45.

**Retired for a reason worth understanding: the thing it existed to do stopped being needed.** A
targeted test is a *cost* optimisation — session 12 measured the full two-pass sweep at 200 calls
and 22 minutes, so a 90-call subset was the affordable way to iterate. Session 17's frozen-pass-A
harness (`scripts/gen_style_frozen.py`) runs the **whole 130-image corpus in 130 calls, about 8
minutes** — cheaper than this test's own 90 two-pass calls. Once the full sweep is cheaper than the
subset, the subset only costs you things:

- **A second answer-key namespace.** Its ids are `st_`, the sweep's are `sw_`, so every user ruling
  had to be applied twice. It carried **zero** of the sixteen accept-sets ruled in sessions 16-17,
  and three rows still named `traditional cel` / `puppet` after those terms were merged away.
- **Divergent keys for identical images**, which is the drift hazard this project keeps paying for.
- Its baseline was pre-split (session 12) and had been dead as a comparison since.

**What replaced its one real capability.** It gated on *movement* over hard cases rather than on
level. That does not need its own test file: the hard cases are a subset of the sweep, so the same
gate is an analysis slice over sweep results at zero extra model cost.

`gen_style_targeted.py` is retired with it — it was the only thing that wrote this file. Its probe
pair list is preserved in `docs/image_inventory.md` § "Probe pairs & sets", which is where that
information should have lived anyway.