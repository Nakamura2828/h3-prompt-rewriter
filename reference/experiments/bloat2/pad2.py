#!/usr/bin/env python3
"""Build SUBSTITUTION-padded copies of a prompt: total tokens fixed, live/inert mix varied.

Side experiment: .claude/handoffs/SIDE_HANDOFF_bloat_calibration2.md

Round 1 varied TOTAL length while holding live instruction constant at 2,239 tokens, and found
nothing. This round does the opposite: every cell lands on the SAME total (~5,000 tokens) and
only the split between live rules and inert filler changes. Length is therefore controlled by
construction and needs no argument.

Two insertions per prompt, both at existing section boundaries, neither splitting a section:

    rules block  -> MID anchor, inside the rules body, under an 'ADDITIONAL RULES' heading
    filler A     -> END anchor, after EXAMPLES and before the closing line (round 1's a_end)

At L0 the rules block is EMPTY, so the L0 file is exactly round 1's a_end 5,000 prompt. verify2.py
asserts that byte-for-byte; if it holds, the L0 run is also directly comparable with round 1's
stored outputs, which is a free cross-session check on the server.

  python reference/experiments/bloat2/pad2.py            # build everything in PLAN
  python reference/experiments/bloat2/pad2.py --verify   # re-count what is already on disk

Counts come from the live tokenizer via scripts/token_budget.py's count(), never estimated from
characters. Per-unit costs are cached in .tokcache.json, keyed on the exact text.

NOTHING OUTSIDE reference/experiments/bloat2/ IS WRITTEN. Source prompts and round 1's directory
are read only.
"""
import io
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]                      # repo root
# The handoff makes a relative-path slip a named hazard: round 1 had one that reached the
# project's PARENT folder. Fail loudly here rather than write somewhere unexpected.
assert ROOT.name == 'h3-prompt-rewriter' and (ROOT / '.git').is_dir(), \
    f'ROOT resolved to {ROOT} -- refusing to run outside the project'
ROUND1 = ROOT / 'reference' / 'experiments' / 'bloat'      # READ ONLY

sys.path.insert(0, str(ROOT / 'scripts'))
from token_budget import count, split_sections           # noqa: E402 -- imported, never modified

TOLERANCE = 25
TOTAL = 5000                # every cell, both probes

CACHE_PATH = HERE / '.tokcache.json'
FILLER = ROUND1 / 'filler_a.txt'            # round 1's inert corpus, reused byte-for-byte

# Anchors. 'end' is round 1's, deliberately BEFORE the closing task line: that line is the task
# handoff and every prompt in the repo ends with it, so filler after it would change structure
# and not just length. 'mid' is where a real rule would go -- inside the rules body.
PROMPTS = {
    'describer_setting': {
        'src': ROOT / 'prompts' / 'describer_setting.txt',
        'mid': '\n\nWHAT YOU DESCRIBE\n',
        'end': '\n\nNow describe the place in the image you are given',
        'rules': {'R': 'rules_r_setting.txt', 'N': 'rules_n_setting.txt',
                  'NF': 'rules_nfew_setting.txt'},
        # live-rule targets. The first is the prompt's own baseline (no rules added at all).
        'levels': {'R': [2700, 3100, 3400, 3800], 'N': [2700, 3100, 3400, 3800],
                   'NF': [3400]},
    },
    'fl2va': {
        'src': ROOT / 'prompts' / 'fl2va.txt',
        'mid': '\n\nFIDELITY\n',
        'end': "\n\nNow rewrite the user's input below into one FL2VA prompt",
        'rules': {'R': 'rules_r_fl2va.txt', 'N': 'rules_n_fl2va.txt',
                  'NF': 'rules_nfew_fl2va.txt'},
        # fl2va's own baseline is 2,698 live-rule tokens, so 2,700 IS its L0 and is not a level.
        'levels': {'R': [3100, 3400, 3800], 'N': [3100, 3400, 3800], 'NF': [3400]},
    },
}


# ---------------------------------------------------------------- corpora

def load_units(path):
    """(header, pool, short, footer) from a '### SECTION ###' delimited corpus file.

    Same format as round 1's filler files, so the rule pools and the filler pool are read by one
    function. '#' comments and blank lines are dropped. header and footer are mandatory at every
    level: an unterminated block would be a structural change rather than a length change.
    """
    text = io.open(path, encoding='utf-8').read()
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
            raise SystemExit(f'ERROR: {path.name} section {name} is empty')
    return out['HEADER'], out['POOL'], out['SHORT'], out['FOOTER']


# ---------------------------------------------------------------- cached counting

def load_cache():
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding='utf-8'))
    return {}


def unit_cost(text, cache):
    """Approximate marginal token cost of one line, cached on the text itself. Only used to
    CHOOSE units; every finished prompt is verified with a real full count before it is written."""
    if text not in cache:
        cache[text] = count('\n' + text)
    return cache[text]


def insert_at(base, anchor, block):
    if not block:
        return base
    if anchor not in base:
        raise SystemExit(f'ERROR: anchor not found in source prompt: {anchor!r}')
    return base.replace(anchor, '\n\n' + block + anchor, 1)


def build_block(header, chosen, footer):
    return '\n'.join(header + chosen + footer)


def fill_to(base, anchor, header, pool, short, footer, target, cache):
    """Choose units from (pool, short) so the ASSEMBLED text lands within +/-TOLERANCE of target.

    Byte-for-byte the algorithm round 1 used, so that an L0 build with no rules reproduces round
    1's a_end file exactly. Phase 1 greedily adds long units using cached per-unit costs; phase 2
    verifies with a REAL full count and corrects with short units, re-counting each time, because
    cached sums drift by a few tokens at the joins and the +/-25 window is tight enough to care.

    Returns (assembled_text, measured_count, n_units, chosen_units).
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
        return count(insert_at(base, anchor, build_block(header, units, footer)))

    actual = real(chosen)
    shorts = sorted(short, key=lambda u: unit_cost(u, cache), reverse=True)
    used_short = []

    for _ in range(40):
        if target - TOLERANCE <= actual <= target + TOLERANCE:
            break
        if actual > target + TOLERANCE:
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
                    raise SystemExit(f'ERROR: pool exhausted below {target} (reached {actual}) '
                                     f'-- lengthen the corpus')
                chosen.append(pick)
                actual = real(chosen + used_short)
                continue
            used_short.append(pick)
        actual = real(chosen + used_short)
    else:
        raise SystemExit(f'ERROR: did not converge on {target} (last {actual})')

    units = chosen + used_short
    return insert_at(base, anchor, build_block(header, units, footer)), actual, len(units), units


# ---------------------------------------------------------------- main

def examples_tokens(text):
    """The EXAMPLES block's own token count -- the 'inert' part of an unpadded prompt, and what
    'live-rule tokens = total - EXAMPLES' subtracts."""
    for name, body in split_sections(text):
        if name.startswith('EXAMPLES'):
            return count(body)
    raise SystemExit('ERROR: no EXAMPLES section found -- the live-rule metric is undefined')


def cells():
    """[(prompt, arm, live_target)] -- L0 first so it is built and checkable before anything else."""
    out = []
    for name in PROMPTS:
        out.append((name, 'L0', None))
    for name, spec in PROMPTS.items():
        for arm in ('R', 'N', 'NF'):
            for lvl in spec['levels'][arm]:
                out.append((name, arm, lvl))
    return out


def main():
    verify_only = '--verify' in sys.argv
    (HERE / 'prompts').mkdir(exist_ok=True)
    cache = load_cache()
    manifest = []

    fh, fpool, fshort, ffoot = load_units(FILLER)
    meta = {}
    for name, spec in PROMPTS.items():
        base = io.open(spec['src'], encoding='utf-8').read()
        base_n = count(base)
        ex_n = examples_tokens(base)
        meta[name] = {'base': base, 'total': base_n, 'examples': ex_n, 'live': base_n - ex_n}
        print(f'{name:<20} total {base_n}  examples {ex_n}  live-rules {base_n - ex_n}')

    for name, arm, lvl in cells():
        spec = PROMPTS[name]
        m = meta[name]
        tag = 'L0' if arm == 'L0' else f'{arm}{lvl}'
        out = HERE / 'prompts' / f'{name}__{tag}.txt'

        if verify_only:
            if not out.exists():
                print(f'  {tag:<8} MISSING')
                continue
            n = count(io.open(out, encoding='utf-8').read())
            print(f'  {tag:<8} {n:>5}  {"ok" if abs(n - TOTAL) <= TOLERANCE else "OUT OF WINDOW"}')
            continue

        # ---- stage 1: rules at the MID anchor, targeting a live-rule DELTA
        if arm == 'L0':
            staged, rule_delta, n_rules, rule_units = m['base'], 0, 0, []
        else:
            rh, rpool, rshort, rfoot = load_units(HERE / spec['rules'][arm])
            want = m['total'] + (lvl - m['live'])       # absolute count after inserting rules
            staged, got, n_rules, rule_units = fill_to(
                m['base'], spec['mid'], rh, rpool, rshort, rfoot, want, cache)
            rule_delta = got - m['total']

        live = m['live'] + rule_delta

        # ---- stage 2: inert filler at the END anchor, targeting the fixed TOTAL
        text, total, n_filler, _ = fill_to(
            staged, spec['end'], fh, fpool, fshort, ffoot, TOTAL, cache)

        out.write_text(text, encoding='utf-8')
        inert = total - live
        print(f'  {tag:<8} total {total:>5} ({total - TOTAL:+d})   live-rules {live:>5} '
              f'({(live - lvl) if lvl else 0:+d})   inert {inert:>5}   '
              f'{n_rules:>3} rule units, {n_filler:>3} filler units')
        manifest.append({
            'file': out.name, 'prompt': name, 'arm': arm, 'tag': tag,
            'live_target': lvl or m['live'], 'live_tokens': live,
            'total_tokens': total, 'total_target': TOTAL,
            'source_total': m['total'], 'source_live': m['live'], 'examples_tokens': m['examples'],
            'rule_delta': rule_delta, 'rule_units': n_rules, 'filler_units': n_filler,
            'inert_tokens': inert, 'inert_share_pct': round(100.0 * inert / total, 1),
            'rule_text': '\n'.join(rule_units),
            'in_total_window': abs(total - TOTAL) <= TOLERANCE,
            'in_live_window': lvl is None or abs(live - lvl) <= TOLERANCE,
        })

    if verify_only:
        return 0

    CACHE_PATH.write_text(json.dumps(cache), encoding='utf-8')
    (HERE / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')

    bad = [m for m in manifest if not (m['in_total_window'] and m['in_live_window'])]
    print(f'\n{len(manifest)} padded prompts, {len(bad)} outside a +/-{TOLERANCE} window')
    for m in bad:
        print(f'  OUT: {m["file"]} total {m["total_tokens"]} live {m["live_tokens"]} '
              f'(targets {TOTAL} / {m["live_target"]})')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
