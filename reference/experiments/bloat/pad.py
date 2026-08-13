#!/usr/bin/env python3
"""Build padded COPIES of a prompt at exact system-prompt token targets.

Side experiment: .claude/handoffs/SIDE_HANDOFF_bloat_calibration.md

The one question is where format adherence breaks as a function of system-prompt LENGTH with
the prompt's logic held constant. So the only thing this script is allowed to change is length:
it inserts filler at an existing section boundary and never edits a line of the original.

  python reference/experiments/bloat/pad.py            # build everything in PLAN
  python reference/experiments/bloat/pad.py --verify   # re-count what is already on disk

Counts come from the live tokenizer via scripts/token_budget.py's count(), never estimated
from characters -- that proxy fails badly on this material (L-PROMPT-TOKEN-BUDGET). Per-unit
counts are cached in .tokcache.json so a rebuild is a handful of HTTP calls rather than
thousands; the cache is keyed on the exact text, so it cannot go stale silently.

NOTHING OUTSIDE reference/experiments/bloat/ IS WRITTEN. Source prompts are read only.
"""
import io
import json
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]                      # repo root
sys.path.insert(0, str(ROOT / 'scripts'))
from token_budget import count              # noqa: E402  -- imported, never modified

TOLERANCE = 25                              # the handoff's +/-25 token window
LEVELS = [3800, 3900, 4000, 4200, 4500, 5000]

CACHE_PATH = HERE / '.tokcache.json'

# Insertion anchors. Both positions are EXISTING section boundaries -- filler is never spliced
# into the middle of a section, because that would change the prompt's structure and not just
# its length.
#
# 'end' deliberately means "after the EXAMPLES block, BEFORE the final closing line", not
# "at the very bottom of the file". That closing line is the task handoff and every prompt in
# this repo ends with it; putting filler after it would separate the instruction from the task
# and confound structure with length.
PROMPTS = {
    'describer_setting': {
        'src': ROOT / 'prompts' / 'describer_setting.txt',
        'anchors': {
            'mid': '\n\nWHAT YOU DESCRIBE\n',
            'end': '\n\nNow describe the place in the image you are given',
        },
    },
    'fl2va': {
        'src': ROOT / 'prompts' / 'fl2va.txt',
        'anchors': {
            'end': "\n\nNow rewrite the user's input below into one FL2VA prompt",
        },
    },
}

# (prompt, filler kind, position) cells to build, one padded file per level.
# Primary probe is the full 2x2 the user asked for; the secondary probe varies length only.
PLAN = [
    ('describer_setting', 'a', 'end'),
    ('describer_setting', 'b', 'end'),
    ('describer_setting', 'a', 'mid'),
    ('describer_setting', 'b', 'mid'),
    ('fl2va', 'a', 'end'),
]


# ---------------------------------------------------------------- filler corpora

def load_filler(kind):
    """(header, pool, short, footer) from filler_<kind>.txt.

    Sections are delimited by '### NAME ###' lines; '#' comments and blank lines are dropped.
    header and footer are MANDATORY at every level, so the filler always has an explicit open
    and close -- an unterminated block would be a structural change, not a length change.
    """
    text = io.open(HERE / f'filler_{kind}.txt', encoding='utf-8').read()
    section, out = None, {'HEADER': [], 'POOL': [], 'SHORT': [], 'FOOTER': []}
    for line in text.split('\n'):
        s = line.strip()
        if s.startswith('###') and s.endswith('###'):
            section = s.strip('# ').strip()
            continue
        if not s or s.startswith('#'):
            continue
        if section in out:
            out[section].append(s)
    for name in out:
        if not out[name]:
            raise SystemExit(f'ERROR: filler_{kind}.txt section {name} is empty')
    return out['HEADER'], out['POOL'], out['SHORT'], out['FOOTER']


# ---------------------------------------------------------------- cached counting

def load_cache():
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding='utf-8'))
    return {}


def unit_cost(text, cache):
    """Approximate marginal token cost of adding one line, cached on the text itself.

    Counted with a leading newline so the join is included. This is only used to CHOOSE units;
    every finished prompt is verified with a real full count before it is written.
    """
    if text not in cache:
        cache[text] = count('\n' + text)
    return cache[text]


def assemble(base, anchor, block):
    if anchor not in base:
        raise SystemExit(f'ERROR: anchor not found in source prompt: {anchor!r}')
    return base.replace(anchor, '\n\n' + block + anchor, 1)


def build_block(header, chosen, footer):
    return '\n'.join(header + chosen + footer)


def pad_to(base, anchor, header, pool, short, footer, target, cache):
    """Choose filler units so the assembled prompt lands within +/-TOLERANCE of target.

    Two phases. Phase 1 greedily adds long units using cached per-unit costs, which is cheap
    and gets close. Phase 2 verifies with a REAL full count and corrects with short units,
    re-counting each time -- cached sums drift from the truth by a few tokens because token
    boundaries at the joins are not additive, and the +/-25 window is tight enough to care.
    """
    fixed = unit_cost('\n'.join(header + footer), cache)
    base_n = unit_cost(base, cache)
    est = base_n + fixed

    chosen = []
    for unit in pool:
        if est >= target - TOLERANCE:
            break
        chosen.append(unit)
        est += unit_cost(unit, cache)

    def real(units):
        return count(assemble(base, anchor, build_block(header, units, footer)))

    actual = real(chosen)
    shorts = sorted(short, key=lambda u: unit_cost(u, cache), reverse=True)
    used_short = []

    for _ in range(40):
        if target - TOLERANCE <= actual <= target + TOLERANCE:
            break
        if actual > target + TOLERANCE:
            # Overshot. Give back the last long unit (or a short one) and re-approach.
            if used_short:
                used_short.pop()
            elif chosen:
                chosen.pop()
            else:
                raise SystemExit(f'ERROR: cannot reach {target}: base alone is {actual}')
        else:
            room = target + TOLERANCE - actual
            pick = next((u for u in shorts
                         if u not in used_short and unit_cost(u, cache) <= room), None)
            if pick is None:
                pick = next((u for u in pool if u not in chosen), None)
                if pick is None:
                    raise SystemExit(f'ERROR: filler pool exhausted below {target} '
                                     f'(reached {actual}) -- lengthen the corpus')
                chosen.append(pick)
                actual = real(chosen + used_short)
                continue
            used_short.append(pick)
        actual = real(chosen + used_short)
    else:
        raise SystemExit(f'ERROR: did not converge on {target} (last {actual})')

    units = chosen + used_short
    return assemble(base, anchor, build_block(header, units, footer)), actual, len(units)


# ---------------------------------------------------------------- main

def main():
    verify_only = '--verify' in sys.argv
    (HERE / 'prompts').mkdir(exist_ok=True)
    cache = load_cache()
    manifest = []

    for name, kind, pos in PLAN:
        spec = PROMPTS[name]
        base = io.open(spec['src'], encoding='utf-8').read()
        anchor = spec['anchors'][pos]
        header, pool, short, footer = load_filler(kind)
        base_n = count(base)
        print(f'\n{name}  filler={kind}  position={pos}   source={base_n} tokens')

        for target in LEVELS:
            out = HERE / 'prompts' / f'{name}__{kind}_{pos}__{target}.txt'
            if verify_only:
                if not out.exists():
                    print(f'  {target:>5}  MISSING')
                    continue
                n = count(io.open(out, encoding='utf-8').read())
                ok = abs(n - target) <= TOLERANCE
                print(f'  {target:>5}  {n:>5}  {"ok" if ok else "OUT OF WINDOW"}')
                manifest.append({'file': out.name, 'prompt': name, 'filler': kind,
                                 'position': pos, 'target': target, 'tokens': n,
                                 'source_tokens': base_n, 'in_window': ok})
                continue

            text, n, nunits = pad_to(base, anchor, header, pool, short, footer, target, cache)
            out.write_text(text, encoding='utf-8')
            pct = 100.0 * (n - base_n) / n
            print(f'  {target:>5}  {n:>5}  ({n - target:+d})  '
                  f'{nunits:>3} filler lines  {pct:.0f}% filler')
            manifest.append({'file': out.name, 'prompt': name, 'filler': kind,
                             'position': pos, 'target': target, 'tokens': n,
                             'source_tokens': base_n, 'filler_lines': nunits,
                             'filler_share_pct': round(pct, 1),
                             'in_window': abs(n - target) <= TOLERANCE})

    CACHE_PATH.write_text(json.dumps(cache), encoding='utf-8')
    (HERE / 'manifest.json').write_text(
        json.dumps(manifest, indent=2), encoding='utf-8')

    bad = [m for m in manifest if not m['in_window']]
    print(f'\n{len(manifest)} padded prompts, {len(bad)} outside the '
          f'+/-{TOLERANCE} window')
    if bad:
        for m in bad:
            print(f'  OUT: {m["file"]} target {m["target"]} got {m["tokens"]}')
        return 1
    print(f'manifest: {(HERE / "manifest.json").relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
