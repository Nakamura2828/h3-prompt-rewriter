#!/usr/bin/env python3
"""Offline validator for H3 prompt-rewriter outputs.

Reads the concatenated test-run files produced by scripts/run_tests.py and reports
per-case PASS/FAIL so a review pass only has to read the failures.

The FORMAT is always named explicitly, because this project produces several output
shapes that share nothing but the record wrapper -- the three-field H3 prompt contract,
the [[FIELD]] describer records, and (later) REF2VA's six sections. Checking one against
another's rules is meaningless, so there is no default:

  python3 scripts/validate.py h3        runs.txt
  python3 scripts/validate.py h3        runs.txt --strip-alignment  # graph injects it
  python3 scripts/validate.py describer runs.txt --role character
  python3 scripts/validate.py h3        runs.txt -v                 # also print passes

Every checker here validates FORMAT, not semantics. A case can pass with a completely
wrong description in it.

Record format (as produced by run_tests.py):
    <model>  [<group> :: <id>]
    ---
    <input>
    ---
    <output>
    [---
    Analysis: ...]
    ----------
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


# run_tests.py writes '##### <group> #####' banners as their own chunk between record
# separators. They are section headers, not cases, and were previously validated as
# malformed records -- one guaranteed spurious FAIL per group.
BANNER = re.compile(r'^#{3,}.*#{3,}$')


def parse_records(text):
    text = text.replace('\r\n', '\n')
    chunks = [c for c in re.split(r'\n-{8,}\n', text) if c.strip()]
    recs = []
    for c in chunks:
        parts = [p.strip('\n') for p in re.split(r'\n-{3}\n', c)]
        if len(parts) >= 3:
            recs.append({'model': parts[0].strip(), 'input': parts[1], 'output': parts[2]})
        elif len(parts) == 1 and not BANNER.match(parts[0].strip()):
            recs.append({'model': '', 'input': '', 'output': parts[0]})
    return recs


def duration_of(inp):
    m = re.search(r'(\d+(?:\.\d+)?)\s*seconds?', inp, re.I)
    return float(m.group(1)) if m else None


def check_h3(out, inp, strip_alignment):
    """The three-field contract: t2va / i2va / l2va / fl2va composer output."""
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


# ---------------------------------------------------------------- describer records

# Closed age vocabularies from prompts/describer_character.txt. Longest match wins, so
# 'young adult' is one term rather than 'young' plus 'adult'.
AGE_PERSON = ['infant', 'toddler', 'child', 'pre-teen', 'teenager', 'young adult',
              'adult', 'middle-aged', 'older adult']
AGE_ANIMAL = ['young', 'adult', 'old', 'not visible']

# Rendering-style words a describer record is not supposed to name (describer_style, when
# it exists, will be the exception). A warn, not an error: 'a T-shirt with a cartoon print'
# is a legitimate garment description.
STYLE_WORDS = ['anime', 'manga', 'pixel art', 'pixelated', '2d-animated', '3d cg',
               'photographic', 'photorealistic', 'live-action', 'illustrated',
               'illustration', 'cartoon', 'claymation', 'watercolor', 'watercolour',
               'cel-shaded', 'rendered', 'digital painting']

# Transient conditions that must not reach a setting record's [[DEFINITION]] -- the whole
# point of quarantining them in [[ATMOSPHERE]] is that the subject-definition sentence has
# to hold by day and by night. A warn: some of these are judgement calls (a snow-covered
# park is arguably structural), so a human decides.
ATMOSPHERE_WORDS = ['daylight', 'sunlight', 'sunlit', 'moonlight', 'overcast', 'cloudy',
                    'night', 'nighttime', 'dusk', 'dawn', 'twilight', 'sunset', 'sunrise',
                    'shadow', 'shadows', 'glare', 'backlit', 'rain', 'rainy', 'fog',
                    'foggy', 'mist', 'misty', 'snowfall', 'dimly lit', 'brightly lit',
                    'warm light', 'cool light', 'golden hour', 'blue hour']

# Field tokens belonging to describer_frame.txt. Combined with every role's own field list
# below to derive what counts as foreign for a given role -- hardcoding the foreign list
# breaks as soon as a role legitimately owns one of these names (describer_style will own
# PALETTE and LIGHTING).
FRAME_FIELDS = ['STYLE', 'FRAMING', 'CHAR', 'CROWD', 'OBJECTS', 'ENVIRONMENT', 'LIGHTING',
                'PALETTE', 'TEXT', 'APPEARANCE', 'CLOTHING', 'POSE', 'GAZE', 'POSITION',
                'EXPRESSION', 'HOLDING', 'CAST NOT FOUND']

NOT_FOUND = '[[SUBJECT NOT FOUND]]'


def _character_age_vocab(out):
    """Which closed list applies depends on what the record says it is describing."""
    return AGE_ANIMAL if '[[SUBJECT_KIND]] animal' in out else AGE_PERSON


# One entry per describer role. Add a role by adding a row, not by branching below.
#
#   fields       required [[FIELD]] tokens, in required order
#   closed       field -> the only permitted values for it
#   drift        field whose value must agree across a 'same: ...' test group, plus the
#                vocabulary to read it with; None disables the cross-case check
#   no_digits    fields where a numeral is an error
#   not_found    whether this role may emit the [[SUBJECT NOT FOUND]] tail line
#   style_warn   whether naming a rendering style is worth flagging
#   style_allow  style words that are legitimate for this role anyway
#   atmos_field  the field holding transient conditions, which [[DEFINITION]] must not reuse
DESCRIBER_ROLES = {
    'character': {
        'fields': ['SUBJECT_KIND', 'APPEARANCE', 'CLOTHING', 'DISTINGUISHING',
                   'LABEL', 'DEFINITION'],
        'closed': {'SUBJECT_KIND': ('person', 'animal')},
        'drift': ('APPEARANCE', _character_age_vocab),
        'no_digits': ('APPEARANCE',),
        'not_found': True,
        'style_warn': True,
        'style_allow': (),
        'atmos_field': None,
    },
    'setting': {
        'fields': ['SETTING_KIND', 'STRUCTURE', 'CONTENTS', 'DISTINGUISHING', 'PLACE',
                   'ATMOSPHERE', 'LABEL', 'DEFINITION'],
        'closed': {'SETTING_KIND': ('interior', 'exterior')},
        'drift': ('SETTING_KIND', lambda out: ['interior', 'exterior']),
        'no_digits': (),          # counting windows or pews is durable and useful
        # No conditional tail line for this role. Across three rounds it caused EVERY format
        # failure (1, then 5, then 3 cases) and was 0-for-2 on the cases it existed to serve --
        # firing where the named place was visible, staying silent where it was absent. Unlike
        # character, a setting image has one place the camera is in, so there is nothing to
        # disambiguate. Emitting the line at all is now an error.
        'not_found': False,
        'style_warn': True,
        # 'rendered' is a building term here ('a rendered plaster column'), not a style claim
        'style_allow': ('rendered',),
        'atmos_field': 'ATMOSPHERE',
    },
}


def age_terms(line, vocab):
    """Every vocabulary term present in a line, dropping any that is merely a substring
    of a longer term already matched ('adult' inside 'young adult')."""
    spans = []
    for t in sorted(vocab, key=len, reverse=True):
        for m in re.finditer(r'(?<![\w-])' + re.escape(t) + r'(?![\w-])', line):
            if not any(s <= m.start() and m.end() <= e for s, e in spans):
                spans.append((m.start(), m.end()))
                yield t


def foreign_fields(role):
    """Every field token that is not this role's own: the other roles' fields plus the
    frame describer's. Derived rather than listed so adding a role cannot silently leave
    a stale entry that rejects one of its own legitimate fields."""
    known = set(FRAME_FIELDS)
    for spec in DESCRIBER_ROLES.values():
        known.update(spec['fields'])
    return sorted(known - set(DESCRIBER_ROLES[role]['fields']))


def check_describer(out, inp, role):
    """A structured [[FIELD]] describer record. Format only -- this cannot tell whether
    the right subject was picked or whether the description is accurate."""
    errs, warns = [], []
    spec = DESCRIBER_ROLES[role]
    fields = spec['fields']
    out = out.strip()

    # --- field labels: present, once each, in order, and first thing in the reply
    if not out.startswith(f'[[{fields[0]}]]'):
        errs.append(f'reply does not begin with [[{fields[0]}]]')
    positions = {}
    for f in fields:
        hits = [m.start() for m in re.finditer(r'\[\[' + re.escape(f) + r'\]\]', out)]
        if not hits:
            errs.append(f'missing field [[{f}]]')
        elif len(hits) > 1:
            errs.append(f'field [[{f}]] appears {len(hits)} times '
                        f'(a second one usually means a second record)')
        else:
            positions[f] = hits[0]
    ordered = [f for f in fields if f in positions]
    if ordered != sorted(ordered, key=lambda f: positions[f]):
        errs.append('fields are out of order')

    # --- reserved characters and stray output
    if '<' in out or '>' in out:
        errs.append('contains < or > (reserved for downstream H3 tags)')
    if '```' in out:
        errs.append('contains a markdown fence')
    if re.search(r'^\s*(User|INPUT|OUTPUT)\s*:', out, re.M):
        errs.append('continues into another turn or example (User:/INPUT:/OUTPUT:)')
    for f in foreign_fields(role):
        if f'[[{f}]]' in out or f'[[{f}:' in out:
            errs.append(f'foreign field [[{f}]] -- not part of the {role} record')

    def field_text(name):
        m = re.search(r'\[\[' + re.escape(name) + r'\]\](.*)', out)
        return m.group(1).strip() if m else ''

    # --- closed vocabularies for whole fields (SUBJECT_KIND, SETTING_KIND, ...)
    for fname, allowed in spec['closed'].items():
        val = field_text(fname).lower().strip(' .')
        if val not in allowed:
            errs.append(f'[[{fname}]] is {val!r}, expected one of {", ".join(allowed)}')

    # --- the one closed vocabulary that sits inside a longer field
    if role == 'character':
        kind = field_text('SUBJECT_KIND').lower()
        app = field_text('APPEARANCE')
        vocab = AGE_ANIMAL if kind == 'animal' else AGE_PERSON
        found = list(age_terms(app.lower(), vocab))
        if not found:
            errs.append(f'[[APPEARANCE]] states no age bracket from the {kind or "person"} '
                        f'list ({", ".join(vocab)})')
        elif len(found) > 1:
            errs.append(f'[[APPEARANCE]] hedges between age brackets: {found}')

    for fname in spec['no_digits']:
        if re.search(r'\d', field_text(fname)):
            errs.append(f'[[{fname}]] contains a digit -- numerals are banned there')

    if 'DEFINITION' in fields:
        definition = field_text('DEFINITION')
        if definition.endswith('.'):
            warns.append('[[DEFINITION]] ends with a full stop; it is spliced mid-sentence')
        # The atmosphere quarantine: a place is the same place by day and by night, so the
        # spliced subject-definition sentence must not carry the hour or the weather.
        if spec['atmos_field']:
            low_def = definition.lower()
            for w in ATMOSPHERE_WORDS:
                if re.search(r'(?<![\w-])' + re.escape(w) + r'(?![\w-])', low_def):
                    warns.append(f'[[DEFINITION]] carries a transient condition: {w!r} '
                                 f'(belongs in [[{spec["atmos_field"]}]] only)')

    # --- the conditional tail line
    nf = out.find(NOT_FOUND)
    if nf != -1:
        if not spec['not_found']:
            errs.append(f'{NOT_FOUND} emitted by the {role} role, which has no such line')
        tail = out[nf + len(NOT_FOUND):].strip().lower()
        if tail in ('none', 'n/a', ''):
            errs.append(f'{NOT_FOUND} {tail!r} -- emit nothing when the subject was found')
        if 'SUBJECT:' not in inp:
            errs.append(f'{NOT_FOUND} emitted with no SUBJECT line in the input')
        if positions and nf < max(positions.values()):
            errs.append(f'{NOT_FOUND} is not last; it must follow [[{fields[-1]}]]')

    if spec['style_warn']:
        low = out.lower()
        for w in STYLE_WORDS:
            if w in spec['style_allow']:
                continue
            if re.search(r'(?<![\w-])' + re.escape(w) + r'(?![\w-])', low):
                warns.append(f'names a rendering style: {w!r} (another pass covers style)')
    return errs, warns


# ------------------------------------------------------------------------- reporting

HEAD = re.compile(r'\[(?:(.*?)\s*::\s*)?([^\[\]]*?)\]\s*$')


def head_parts(model_line):
    """Pull (group, id) out of run_tests.py's '<model>  [<group> :: <id>]' header."""
    m = HEAD.search(model_line.strip())
    return (m.group(1), m.group(2)) if m else (None, None)


def report(results, verbose):
    npass = 0
    for i, (label, errs, warns) in enumerate(results, 1):
        if errs:
            print(f'[{i}] FAIL  {label}')
        else:
            npass += 1
            if not (warns or verbose):
                continue
            print(f'[{i}] PASS  {label}')
        for e in errs:
            print(f'        ERROR  {e}')
        for w in warns:
            print(f'        warn   {w}')
    print(f'\n{npass}/{len(results)} passed')
    return npass == len(results)


def main():
    ap = argparse.ArgumentParser(
        description='Validate H3 prompt-rewriter run output. The format is always named '
                    'explicitly -- these output shapes share no rules.')
    sub = ap.add_subparsers(dest='format', required=True, metavar='FORMAT')

    p_h3 = sub.add_parser('h3', help='three-field contract (t2va/i2va/l2va/fl2va)')
    p_h3.add_argument('path')
    p_h3.add_argument('--strip-alignment', action='store_true',
                      help='the graph injects the alignment line; ignore it')

    p_d = sub.add_parser('describer', help='structured [[FIELD]] describer records')
    p_d.add_argument('path')
    p_d.add_argument('--role', default='character', choices=sorted(DESCRIBER_ROLES),
                     help='which describer role wrote these records')

    for p in (p_h3, p_d):
        p.add_argument('-v', '--verbose', action='store_true',
                       help='also print passing cases')

    a = ap.parse_args()
    recs = parse_records(pathlib.Path(a.path).read_text(encoding='utf-8'))

    results, brackets = [], {}
    for i, r in enumerate(recs, 1):
        group, case_id = head_parts(r['model'])
        if a.format == 'h3':
            errs, warns = check_h3(r['output'], r['input'], a.strip_alignment)
        else:
            errs, warns = check_describer(r['output'], r['input'], a.role)
            # Cases in a group named 'same: ...' describe the same subject or the same
            # place, so the role's drift field must agree across them. This is the drift
            # check REF2VA needs (CLAUDE.md).
            drift = DESCRIBER_ROLES[a.role]['drift']
            if drift and group and group.startswith('same:'):
                dfield, vocab_of = drift
                m = re.search(r'\[\[' + re.escape(dfield) + r'\]\](.*)', r['output'])
                terms = list(age_terms(m.group(1).lower(), vocab_of(r['output']))) if m else []
                brackets.setdefault(group, []).append((case_id, terms[0] if terms else None))
        label = case_id or (r['input'].strip().split('\n')[0])[:64] or f'record {i}'
        results.append((label, errs, warns))

    ok = report(results, a.verbose)

    dname = (DESCRIBER_ROLES[a.role]['drift'] or (None,))[0] if a.format == 'describer' else None
    for group, entries in sorted(brackets.items()):
        seen = {b for _, b in entries if b}
        if len(seen) > 1:
            ok = False
            print(f'\nFAIL  {group}: [[{dname}]] drifted across the same subject')
            for cid, b in entries:
                print(f'        {cid}: {b}')
        elif len(entries) > 1:
            print(f'\nOK    {group}: [[{dname}]] is {seen.pop() if seen else "unset"} '
                  f'in all {len(entries)} cases')

    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
