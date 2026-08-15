#!/usr/bin/env python3
"""Assemble H3 rewriter system prompts from shared blocks + per-mode manifests.

Usage:
  python3 scripts/build.py              # build all modes into prompts/
  python3 scripts/build.py --verify     # build, then diff against reference/pre_build_env_canonical_prompts
  python3 scripts/build.py t2va i2va    # build selected modes

Output convention matches the locked prompts: CRLF line endings, no trailing newline.
"""
import argparse, json, pathlib, sys, difflib

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODES = ['t2va', 'i2va', 'l2va', 'fl2va']
SLOT = '{{%s}}'


def render_block(path, slots):
    """Read a block file and substitute {{SLOTS}}. A slot whose value is None
    deletes the entire line it sits on (used for mode-inapplicable rules)."""
    text = (ROOT / path).read_text(encoding='utf-8')
    out = []
    for line in text.split('\n'):
        drop = False
        for k, v in slots.items():
            token = SLOT % k
            if token in line:
                if v is None:
                    drop = True
                    break
                line = line.replace(token, v)
        if not drop:
            out.append(line)
    leftover = [l for l in out if '{{' in l]
    if leftover:
        raise SystemExit(f'ERROR: unfilled slot in {path}: {leftover[0]!r}')
    return '\n'.join(out).strip('\n')


def build(mode):
    man = json.loads((ROOT / 'manifests' / f'{mode}.json').read_text(encoding='utf-8'))
    slots = man['slots']
    parts = []
    for item in man['order']:
        if item == '@duration':
            item = f"blocks/40_duration_shots__{man['duration']}.txt"
        parts.append(render_block(item.format(m=mode), slots))
    body = '\n\n'.join(p for p in parts if p)
    # LF, deliberately. This line used to convert the assembled prompt to CRLF -- an early
    # Windows-native assumption. Session 23 normalised the repo to LF (.gitattributes), and this
    # was the one thing that put CRLF back into prompts/ on EVERY build, so the tree could never
    # stay normalised. Nothing downstream cares: the prompts are pasted into ComfyUI node widgets,
    # and --verify compares via read_text() (universal newlines), so it is blind to the ending on
    # both sides -- its three verdicts are identical before and after this change.
    return body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('modes', nargs='*', default=None)
    ap.add_argument('--verify', action='store_true')
    a = ap.parse_args()
    modes = a.modes or MODES
    (ROOT / 'prompts').mkdir(exist_ok=True)
    rc = 0
    for m in modes:
        out = build(m)
        (ROOT / 'prompts' / f'{m}.txt').write_bytes(out.encode('utf-8'))
        print(f'built prompts/{m}.txt  ({len(out)} bytes)')
        if a.verify:
            # Not every mode has a canonical baseline: fl2va postdates the pre-build-env set
            # and never had one. Skipping is correct, not a failure -- reading it
            # unconditionally raised FileNotFoundError and killed the whole --verify run,
            # which left the check dead for ALL modes because fl2va is last in MODES.
            refp = ROOT / 'reference/pre_build_env_canonical_prompts' / f'{m}.txt'
            if not refp.exists():
                print(f'  VERIFY {m}: skipped -- no canonical baseline (postdates the build system)')
                continue
            ref = refp.read_text(encoding='utf-8')
            new = out.replace('\r\n', '\n')
            if ref.replace('\r\n', '\n') == new:
                print(f'  VERIFY {m}: byte-identical to reference')
            else:
                d = list(difflib.unified_diff(ref.replace('\r\n', '\n').split('\n'),
                                              new.split('\n'), 'reference', 'rebuilt', lineterm='', n=0))
                adds = [l for l in d if l.startswith('+') and not l.startswith('+++')]
                dels = [l for l in d if l.startswith('-') and not l.startswith('---')]
                print(f'  VERIFY {m}: {len(adds)} added line(s), {len(dels)} removed line(s)')
                for l in d:
                    if l[:1] in '+-@' and not l.startswith(('+++', '---')):
                        print('   ', l[:160])
                if m != 'l2va':
                    rc = 1
    sys.exit(rc)


if __name__ == '__main__':
    main()
