#!/usr/bin/env python3
"""Run H3 prompt cases against a llama.cpp (or any OpenAI-compatible) server.

Stdlib only. Windows-friendly. No ComfyUI required.

  python scripts/run_tests.py cases.json
  python scripts/run_tests.py cases.json --only p1_first p1_last
  python scripts/run_tests.py cases.json --out runs/describer_v8.txt
  python scripts/run_tests.py cases.json --dry-run

Case files are JSON:

{
  "defaults": {
    "server": "http://localhost:8080/v1/chat/completions",
    "model": "local",
    "system_file": "prompts/describer_frame.txt",
    "temperature": 0, "top_p": 0.9, "top_k": 40, "max_tokens": 2048
  },
  "cases": [
    {"id": "p1_first", "user": "CAST: the man in the grey coat | ROLE: frame",
     "image": "images/p1_first.png"},
    {"id": "p1_last",  "user": "CAST: the man in the grey coat | ROLE: frame",
     "image": "images/p1_last.png"},
    {"id": "p1_compose", "system_file": "prompts/fl2va_composer.txt",
     "user": "[[FIRST_FRAME]]\\n{{p1_first}}\\n\\n[[LAST_FRAME]]\\n{{p1_last}}\\n\\nDURATION: 6 seconds"},
    {"id": "p1_final", "system_file": "prompts/l2va.txt", "align": "l2va", "duration": 6,
     "user": "..."}
  ]
}

Any {{case_id}} in a user prompt is replaced by that case's output from this run,
which is how a composer consumes two describer passes. Cases run in file order.

Every call sends "seed": 0 by default (override per case with "seed": N). Discovered
2026-08-10: temperature 0 alone is NOT reproducible run-to-run against this server --
identical inputs produced outputs differing in length across repeated invocations,
contradicting this project's earlier assumption (see CLAUDE.md). An explicit seed is
required for genuine determinism, matching what the old ComfyUI graph already did.

A case with "align" set to "i2va", "fl2va", or "l2va" gets the spec's graph-injected
alignment line (official_VIDEO_PROMPT_WRITING_GUIDE_base_en.md SS2.1) prepended to its
OUTPUT ONLY, as the first line of the final prompt plus one blank line -- this never
touches the model's own generation, which stays what {{case_id}} substitution and
validate.py --strip-alignment both expect. "fl2va" and "l2va" also require "duration"
(seconds, formatted to exactly two decimal places); the final shot number is read from
the model's own last "[Shot N]" line, not user-supplied, since that's what the model
actually produced. "align": "fl2va" additionally splices a fixed landing sentence onto
the end of integrated_multimodal_description's own paragraph, before overall_soundscape:
-- prompts/fl2va.txt's model is told not to write this sentence itself.

Output is written in the concatenated format validate.py already parses, and each
case is also saved individually under <outdir>/<id>.txt for inspection.
"""
import argparse, base64, json, pathlib, re, sys, time
import urllib.request, urllib.error

THINK = re.compile(r'^\s*<think>.*?</think>\s*', re.S)

# Deliberately not using mimetypes.guess_type(): on Windows it consults the
# registry, which can be wrong for well-known extensions (e.g. .jpg guessing
# as 'application/jpg' rather than 'image/jpeg' if some installer clobbered
# that association). A fixed map keeps this independent of OS/machine state.
IMAGE_MIME = {
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.webp': 'image/webp',
    '.gif': 'image/gif',
    '.bmp': 'image/bmp',
}


LADDER = ['extreme wide', 'wide', 'medium-wide', 'medium', 'medium close-up',
          'close-up', 'extreme close-up']


def shot_rank(framing_line):
    """Map a [[FRAMING]] line onto the shot-size ladder. Longest term wins, so
    'medium close-up' is not mistaken for 'medium' and 'medium-wide' not for 'wide'."""
    low = framing_line.lower()
    best, rank = 0, None
    for i, term in enumerate(LADDER):
        if term in low and len(term) > best:
            best, rank = len(term), i
    return rank


def camera_move(out_a, out_b):
    fa = re.search(r'\[\[FRAMING\]\] (.*)', out_a)
    fb = re.search(r'\[\[FRAMING\]\] (.*)', out_b)
    if not (fa and fb):
        return 'unknown, judge from the first frame and the user description'
    a_txt, b_txt = fa.group(1).strip(), fb.group(1).strip()
    ra, rb = shot_rank(a_txt), shot_rank(b_txt)
    if ra is None or rb is None:
        return f'unknown ({a_txt} to {b_txt})'
    if rb > ra:
        return f'PUSH IN ({LADDER[ra]} to {LADDER[rb]})'
    if rb < ra:
        return f'PULL OUT ({LADDER[ra]} to {LADDER[rb]})'
    return f'NO ZOOM, framing holds at {LADDER[ra]}'


SHOT = re.compile(r'\[Shot (\d+)\]')


def last_shot_number(text):
    nums = [int(n) for n in SHOT.findall(text)]
    return max(nums) if nums else 1


def alignment_line(kind, text, duration):
    """Build the graph-injected alignment line for a finished i2va/fl2va/l2va output.
    Verbatim from official_VIDEO_PROMPT_WRITING_GUIDE_base_en.md SS2.1 -- FL2VA's own
    wording drops the <>/[] brackets that I2VA and L2VA use; that's the spec, not a typo."""
    if kind == 'i2va':
        return ('For the target video, at 0.00 seconds into the target video, '
                '<Picture 1> (from [Shot 1]) is fully referenced.')
    n = last_shot_number(text)
    s = f'{duration:.2f}'
    if kind == 'l2va':
        return (f'How the reference pictures align with the target video — '
                 f'<Picture 1> (from [Shot {n}]) aligns with the {s}-second mark '
                 f'of the target video.')
    if kind == 'fl2va':
        return (f'How the reference pictures align with the target video — '
                 f'Picture 1 (from Shot 1) aligns with the 0.00-second mark of the '
                 f'target video; Picture 2 (from Shot {n}) aligns with the {s}-second '
                 f'mark of the target video.')
    raise SystemExit(f'ERROR: unknown align kind {kind!r} (expected i2va, fl2va, or l2va)')


FL2VA_LANDING = 'The shot lands exactly on <Picture 2>.'


def insert_fl2va_landing(text):
    """Splice the deterministic landing sentence onto the end of
    integrated_multimodal_description's own paragraph, before overall_soundscape: --
    mirrors prompts/fl2va.txt's OUTPUT CONTRACT bullet telling the model not to write
    this sentence itself. Text is otherwise untouched if the label isn't found."""
    idx = text.find('overall_soundscape:')
    if idx == -1:
        return text
    before = text[:idx].rstrip()
    after = text[idx:]
    return f'{before} {FL2VA_LANDING}\n\n{after}'


def load_system(path, cache={}):
    if path not in cache:
        cache[path] = pathlib.Path(path).read_text(encoding='utf-8')
    return cache[path]


def image_payload(path):
    p = pathlib.Path(path)
    if not p.is_file():
        raise SystemExit(f'ERROR: image not found: {p}')
    mime = IMAGE_MIME.get(p.suffix.lower())
    if not mime:
        raise SystemExit(f'ERROR: unsupported image extension {p.suffix!r} for {p} '
                          f'(supported: {", ".join(sorted(IMAGE_MIME))})')
    b64 = base64.b64encode(p.read_bytes()).decode('ascii')
    return {'type': 'image_url', 'image_url': {'url': f'data:{mime};base64,{b64}'}}


def call(cfg, system, user, image, timeout):
    content = [{'type': 'text', 'text': user}]
    if image:
        content.insert(0, image_payload(image))
    body = {
        'model': cfg.get('model', 'local'),
        'messages': [{'role': 'system', 'content': system},
                     {'role': 'user', 'content': content}],
        'temperature': cfg.get('temperature', 0),
        'top_p': cfg.get('top_p', 0.9),
        'max_tokens': cfg.get('max_tokens', 2048),
        'seed': cfg.get('seed', 0),
        'stream': False,
    }
    if cfg.get('top_k') is not None:
        body['top_k'] = cfg['top_k']            # llama-server extension
    if cfg.get('repeat_penalty') is not None:
        body['repeat_penalty'] = cfg['repeat_penalty']
    req = urllib.request.Request(
        cfg.get('server', 'http://localhost:8080/v1/chat/completions'),
        data=json.dumps(body).encode('utf-8'),
        headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode('utf-8'))
    except urllib.error.URLError as e:
        raise SystemExit(f'ERROR: cannot reach server: {e}\n'
                         f'       is llama-server running with --mmproj for vision?')
    text = data['choices'][0]['message']['content']
    return THINK.sub('', text).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cases')
    ap.add_argument('--out', default=None, help='concatenated output file')
    ap.add_argument('--outdir', default='runs', help='per-case output directory')
    ap.add_argument('--only', nargs='*', help='run only these case ids')
    ap.add_argument('--timeout', type=int, default=600)
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    spec = json.loads(pathlib.Path(a.cases).read_text(encoding='utf-8'))
    defaults = spec.get('defaults', {})
    cases = spec['cases']
    if a.only:
        cases = [c for c in cases if c['id'] in a.only]
        if not cases:
            raise SystemExit(f'ERROR: no case ids matched {a.only}')

    outdir = pathlib.Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime('%Y%m%d-%H%M%S')
    out_path = pathlib.Path(a.out) if a.out else outdir / f'run-{stamp}.txt'
    out_path.parent.mkdir(parents=True, exist_ok=True)

    results, records = {}, []
    for n, c in enumerate(cases, 1):
        cfg = {**defaults, **c}
        sys_path = cfg.get('system_file')
        if not sys_path:
            raise SystemExit(f'ERROR: case {c["id"]!r} has no system_file')
        system = load_system(sys_path)

        user = c['user']
        # {{CAMERA:idA:idB}} decides push in / pull out from two FRAMING lines, so the
        # model never has to reason about shot-size ordering
        for ida, idb in re.findall(r'\{\{CAMERA:(\w+):(\w+)\}\}', user):
            token = '{{CAMERA:' + ida + ':' + idb + '}}'
            if ida in results and idb in results:
                user = user.replace(token, camera_move(results[ida], results[idb]))
            elif a.dry_run:
                user = user.replace(token, f'<camera from {ida} to {idb}>')
            else:
                raise SystemExit(f'ERROR: case {c["id"]!r} references {token} '
                                 f'which has not run yet in this invocation.')
        # {{id:FIELD}} pulls a single [[FIELD]] line out of a previous case's output
        for ref, fld in re.findall(r'\{\{(\w+):(\w+)\}\}', user):
            token = '{{' + ref + ':' + fld + '}}'
            if ref in results:
                m = re.search(r'\[\[' + fld + r'\]\] (.*)', results[ref])
                user = user.replace(token, m.group(1).strip() if m else 'not reported')
            elif a.dry_run:
                user = user.replace(token, f'<{fld} of {ref}>')
            else:
                raise SystemExit(f'ERROR: case {c["id"]!r} references {token} '
                                 f'which has not run yet in this invocation.')
        for ref in re.findall(r'\{\{(\w+)\}\}', user):
            if ref in results:
                user = user.replace('{{' + ref + '}}', results[ref])
            elif a.dry_run:
                user = user.replace('{{' + ref + '}}', f'<output of {ref}>')
            else:
                raise SystemExit(f'ERROR: case {c["id"]!r} references {{{{{ref}}}}} '
                                 f'which has not run yet in this invocation. '
                                 f'Run it in the same invocation, or drop --only.')

        align = cfg.get('align')
        if align and align in ('l2va', 'fl2va') and cfg.get('duration') is None:
            raise SystemExit(f'ERROR: case {c["id"]!r} has align={align!r} but no duration')

        label = f'[{n}/{len(cases)}] {c["id"]}'
        if a.dry_run:
            print(f'{label}  system={sys_path}  image={c.get("image", "-")}'
                  + (f'  align={align}' if align else ''))
            print('    ' + user.replace('\n', '\n    ')[:400])
            continue

        t0 = time.time()
        print(f'{label} ... ', end='', flush=True)
        text = call(cfg, system, user, c.get('image'), a.timeout)
        print(f'{time.time() - t0:.1f}s  {len(text)} chars')

        results[c['id']] = text
        output_text = text
        if align == 'fl2va':
            output_text = insert_fl2va_landing(output_text)
        if align:
            output_text = alignment_line(align, text, cfg.get('duration')) + '\n\n' + output_text

        (outdir / f'{c["id"]}.txt').write_text(output_text, encoding='utf-8')
        head = f"{cfg.get('model', 'local')}  [{c['id']}]"
        if c.get('group'):
            head = f"{cfg.get('model', 'local')}  [{c['group']} :: {c['id']}]"
        records.append(f"{head}\n---\n{user}\n---\n{output_text}")

    if not a.dry_run:
        body = []
        last_group = None
        for c, rec in zip([x for x in cases], records):
            g = c.get('group')
            if g and g != last_group:
                body.append(f'##### {g} #####')
                last_group = g
            body.append(rec)
        out_path.write_text('\n----------\n'.join(body) + '\n----------\n',
                            encoding='utf-8')
        print(f'\nwrote {out_path}  ({len(records)} cases)')
        print(f'per-case files in {outdir}/')


if __name__ == '__main__':
    main()
