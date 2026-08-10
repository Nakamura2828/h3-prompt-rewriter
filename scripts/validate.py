#!/usr/bin/env python3
"""Offline validator for H3 prompt-rewriter outputs.

Reads the concatenated test-run files produced by the ComfyUI loop and reports
per-case PASS/FAIL so a review pass only has to read the failures.

Record format (as produced by the existing loop):
    <model>
    ---
    <input>
    ---
    <output>
    [---
    Analysis: ...]
    ----------

Usage:
  python3 scripts/validate.py runs.txt
  python3 scripts/validate.py runs.txt --strip-alignment   # graph injects the alignment line
  python3 scripts/validate.py runs.txt -v                  # also print passing cases
"""
import argparse, re, sys, pathlib

FIELDS = ['integrated_multimodal_description:', 'overall_soundscape:', 'non_diegetic_music:']
BANNED = ['tense', 'melancholic', 'mysterious', 'mystery', 'ominous', 'haunting', 'uplifting',
          'somber', 'eerie', 'hopeful', 'triumphant', 'wistful', 'nostalgic', 'foreboding',
          'sense of', 'evoking', 'conveying', 'creating a']
CUT_PHRASES = ['cuts to', 'transitions to', 'switches to', 'changes to']
ALIGNMENT = re.compile(r'^\s*(How the reference pictures align|For the target video, at).*$', re.M)
TS = re.compile(r'At (\d{2}):(\d{2})\.(\d{3}),')
SHOT = re.compile(r'\[Shot (\d+)\]')
DBLOCK = re.compile(r'<d>(.*?)</d>', re.S)


def parse_records(text):
    text = text.replace('\r\n', '\n')
    chunks = [c for c in re.split(r'\n-{8,}\n', text) if c.strip()]
    recs = []
    for c in chunks:
        parts = [p.strip('\n') for p in re.split(r'\n-{3}\n', c)]
        if len(parts) >= 3:
            recs.append({'model': parts[0].strip(), 'input': parts[1], 'output': parts[2]})
        elif len(parts) == 1:
            recs.append({'model': '', 'input': '', 'output': parts[0]})
    return recs


def duration_of(inp):
    m = re.search(r'(\d+(?:\.\d+)?)\s*seconds?', inp, re.I)
    return float(m.group(1)) if m else None


def check(out, inp, strip_alignment):
    errs, warns = [], []
    if strip_alignment:
        hits = ALIGNMENT.findall(out)
        out = ALIGNMENT.sub('', out)
        if not hits:
            warns.append('no graph alignment line found (expected with --strip-alignment)')
    out = re.sub(r'\n{3,}', '\n\n', out).strip()

    # --- field labels, order, uniqueness
    pos = {}
    for f in FIELDS:
        n = out.count(f)
        if n == 0:
            errs.append(f'missing field label: {f}')
        elif n > 1:
            errs.append(f'field appears {n}x: {f}')
        if n:
            pos[f] = out.index(f)
    if len(pos) == 3 and not (pos[FIELDS[0]] < pos[FIELDS[1]] < pos[FIELDS[2]]):
        errs.append('fields out of order')
    if not out.startswith(FIELDS[0]):
        errs.append(f'output does not begin with {FIELDS[0]!r}')
    for bad in ('```', 'User:', 'Assistant:', '<think>'):
        if bad in out:
            errs.append(f'stray token in output: {bad!r}')

    if len(pos) != 3:
        return errs, warns
    imd = out[pos[FIELDS[0]] + len(FIELDS[0]):pos[FIELDS[1]]].strip()
    ndm = out[pos[FIELDS[2]] + len(FIELDS[2]):].strip()

    # --- trailing junk after the last field
    if len(ndm.split('\n')) > 3:
        warns.append('non_diegetic_music spans >3 lines (possible continuation)')

    # --- shots
    shots = [int(x) for x in SHOT.findall(imd)]
    if not shots:
        errs.append('no [Shot N] marker')
    else:
        if shots[0] != 1:
            errs.append(f'first shot is [Shot {shots[0]}], expected [Shot 1]')
        if shots != list(range(1, len(shots) + 1)):
            errs.append(f'shot numbering not sequential: {shots}')
    segs = re.split(r'(\[Shot \d+\])', imd)
    bodies = []
    for i in range(1, len(segs), 2):
        bodies.append((segs[i], segs[i + 1] if i + 1 < len(segs) else ''))
    times = []
    for n, (mark, body) in enumerate(bodies):
        m = TS.search(body)
        if n == 0:
            if m and body.index(m.group(0)) < 30:
                errs.append('[Shot 1] carries a timestamp')
        else:
            if not m:
                errs.append(f'{mark} has no "At MM:SS.mmm," timestamp')
            else:
                secs = int(m.group(1)) * 60 + int(m.group(2)) + int(m.group(3)) / 1000
                times.append((mark, secs))
        # cut phrase mid-shot
        tail = body[m.end():] if (m and n) else body
        for cp in CUT_PHRASES:
            for hit in re.finditer(re.escape(cp), tail):
                if hit.start() > 60:
                    warns.append(f'{mark}: cut phrase {cp!r} mid-shot without a new [Shot N]')
                    break
    for a, b in zip(times, times[1:]):
        if b[1] <= a[1]:
            errs.append(f'timestamps not strictly increasing: {a[0]}={a[1]}s then {b[0]}={b[1]}s')
    dur = duration_of(inp)
    if dur:
        for mark, s in times:
            if s >= dur:
                errs.append(f'{mark} timestamp {s}s is outside the {dur}s duration')

    # --- dialogue blocks
    if imd.count('<d>') != imd.count('</d>'):
        errs.append(f'unbalanced <d> tags ({imd.count("<d>")} open, {imd.count("</d>")} close)')
    for d in DBLOCK.findall(imd):
        inner = d.strip()
        if not inner:
            errs.append('empty <d> block')
            continue
        if not re.match(r'^\[[A-Za-z ]+\]', inner):
            errs.append(f'<d> block missing [Language] tag: {inner[:40]!r}')
        if len(re.sub(r'^\[[A-Za-z ]+\]', '', inner).strip()) < 2:
            errs.append('nearly-empty <d> block')
    for mark, body in bodies:
        if body.count('<d>') != body.count('</d>'):
            errs.append(f'{mark}: <d> block split across a cut')

    # --- voiceover
    for m in re.finditer(r'says in an off-screen voiceover', imd):
        after = imd[m.end():m.end() + 400]
        if not re.search(r'lips remain', after):
            errs.append('voiceover without a following "lips remain closed" statement')
    if re.search(r'(voice-over|voiceover)\b', imd) and 'says in an off-screen voiceover' not in imd:
        warns.append('voiceover referenced without the exact required phrase')

    # --- music field
    low = ndm.lower()
    for w in BANNED:
        if re.search(r'\b' + re.escape(w), low):
            errs.append(f'mood/effect word in non_diegetic_music: {w!r}')
    return errs, warns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('path')
    ap.add_argument('--strip-alignment', action='store_true')
    ap.add_argument('-v', '--verbose', action='store_true')
    a = ap.parse_args()
    recs = parse_records(pathlib.Path(a.path).read_text(encoding='utf-8'))
    npass = 0
    for i, r in enumerate(recs, 1):
        errs, warns = check(r['output'], r['input'], a.strip_alignment)
        label = (r['input'].strip().split('\n')[0])[:64] or f'record {i}'
        if errs:
            print(f'[{i}] FAIL  {label}')
            for e in errs:
                print(f'        ERROR  {e}')
            for w in warns:
                print(f'        warn   {w}')
        else:
            npass += 1
            if warns or a.verbose:
                print(f'[{i}] PASS  {label}')
                for w in warns:
                    print(f'        warn   {w}')
    print(f'\n{npass}/{len(recs)} passed')
    sys.exit(0 if npass == len(recs) else 1)


if __name__ == '__main__':
    main()
