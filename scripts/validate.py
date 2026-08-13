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
import argparse, difflib, re, sys, pathlib

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
NOT_FOUND_NAME = NOT_FOUND[2:-2]        # the bare token name, for the [[...]] sweep below

# The closed three-axis style vocabulary (docs/image_inventory.md, "Style vocabulary").
# Rebuilt session 10: the old sub-lists mixed five axes, and that coupling was dragging the
# COARSE term to the wrong value -- 'drawing' was emitted once in 100 images because every
# idiom it could carry lived under some other coarse term. Split into three independent axes.
#
# MEDIUM_VOCAB is the medium axis at two levels: coarse -> its permitted sub-terms, where an
# empty tuple means the coarse term has no sub-level and [[SUB_MEDIUM]] must say 'none'.
# Kept in sync with the master table by hand -- the same lists drive scripts/inventory.py's
# own validation of that table.
MEDIUM_VOCAB = {
    'photograph': (),
    'live-action film': (),
    '3d cg': (),
    'stop-motion': ('clay', 'puppet', 'figure', 'model'),
    '2d cel': ('traditional cel', 'digital'),
    'comic': ('ink', 'screentone', 'digital'),
    'painting': ('oil', 'watercolour', 'digital'),
    'drawing': ('marker', 'pencil', 'ink', 'digital'),
    'vector': (),
    'pixel art': (),
    'print': ('engraving', 'halftone'),
}

# The other two axes are FLAT and MEDIUM-INDEPENDENT: any idiom may pair with any medium.
# That is the point of the rebuild, so these are deliberately not nested under MEDIUM_VOCAB
# and must never be validated against the coarse term.
IDIOM_VOCAB = ('anime', 'western toon', 'flat graphic', 'dimensional toon', 'realist')
TREATMENT_VOCAB = ('colour', 'monochrome', 'vintage technicolor')


def _medium_vocab(out):
    """Drift is read on the COARSE term only. The sub-term legitimately differs between two
    records of one medium (ivy_toon traditional cel / peter_griffin_toon digital), so folding
    it into the drift check would flag a correct discrimination as drift. The same applies to
    [[IDIOM]] and [[TREATMENT]], which are independent axes -- two images can share a medium
    and differ on either."""
    return list(MEDIUM_VOCAB)


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
        'coarse_sub': None,
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
        'coarse_sub': None,
    },
    'style': {
        'fields': ['EXECUTION', 'PALETTE', 'LIGHTING', 'DISTINGUISHING',
                   'MEDIUM', 'SUB_MEDIUM', 'IDIOM', 'TREATMENT', 'LABEL', 'DEFINITION'],
        'closed': {'MEDIUM': tuple(MEDIUM_VOCAB),
                   'IDIOM': IDIOM_VOCAB,
                   'TREATMENT': TREATMENT_VOCAB},
        # 11 coarse terms, so unlike setting's two-value [[SETTING_KIND]] this drift check
        # can actually fail. 'same:' groups here are same-medium groups, NOT the
        # cross-media probe pairs -- those are supposed to differ.
        'drift': ('MEDIUM', _medium_vocab),
        'no_digits': (),          # '16-colour', '1990s' and 'four-panel' are all legitimate
        # Same reasoning as setting: one image has one look, so there is nothing to
        # disambiguate and no judgement worth risking (L-OPTIONAL-JUDGEMENT-IS-A-LIABILITY).
        'not_found': False,
        # This is the one role whose whole job is naming the rendering style.
        'style_warn': False,
        'style_allow': (),
        # [[LIGHTING]] here is the lighting TREATMENT, which is durable, so there is no
        # transient field to quarantine. The prompt bans time-of-day wording instead.
        'atmos_field': None,
        'coarse_sub': ('MEDIUM', 'SUB_MEDIUM', MEDIUM_VOCAB),
    },
    # ---- the two halves of the split style describer (session 12).
    #
    # 'style' above ran out of room: at 3,740 tokens it sat over this model's ~3,700 adherence
    # ceiling, so every further fix cost a rule elsewhere (L-PROMPT-TOKEN-BUDGET). Splitting the
    # ten fields into a describing pass and a classifying pass halves each prompt and makes
    # "classify from what you described" architectural rather than a rule to remember.
    #
    # Note what classify_tokens() derives for free once both rows exist: a stray [[MEDIUM]] in a
    # pass-A record (leaking classification) and a stray [[EXECUTION]] in a pass-B record
    # (echoing its input instead of classifying) are both errors, with no new code.
    #
    # One run file holds both kinds of record, so each half is validated separately:
    #   validate.py describer <run> --role style_look  --id-prefix look_
    #   validate.py describer <run> --role style_class --id-prefix sw_
    'style_look': {
        'fields': ['EXECUTION', 'PALETTE', 'LIGHTING', 'DISTINGUISHING', 'LABEL', 'DEFINITION'],
        'closed': {},
        # Nothing to drift-check: pass A emits no closed vocabulary. The 11-value [[MEDIUM]]
        # that made 'style' worth drift-checking now belongs to style_class.
        'drift': None,
        'no_digits': (),
        'not_found': False,
        'style_warn': False,     # naming the rendering style is still the whole job
        'style_allow': (),
        'atmos_field': None,
        'coarse_sub': None,
    },
    'style_class': {
        'fields': ['MEDIUM', 'SUB_MEDIUM', 'IDIOM', 'TREATMENT'],
        'closed': {'MEDIUM': tuple(MEDIUM_VOCAB),
                   'IDIOM': IDIOM_VOCAB,
                   'TREATMENT': TREATMENT_VOCAB},
        'drift': ('MEDIUM', _medium_vocab),
        'no_digits': (),
        'not_found': False,
        'style_warn': False,
        'style_allow': (),
        # No [[DEFINITION]] here, so the full-stop and atmosphere checks simply never fire.
        'atmos_field': None,
        'coarse_sub': ('MEDIUM', 'SUB_MEDIUM', MEDIUM_VOCAB),
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


# Any [[...]] token, however wrong. The length cap keeps a runaway '[[' in prose from
# swallowing the rest of the output as one enormous "field name".
TOKEN = re.compile(r'\[\[([^\[\]]{1,40})\]\]')
NEAR_MISS_RATIO = 0.75


def classify_tokens(out, role):
    """(foreign, near, unknown) -- every [[...]] token present that is not this role's own.

    An ALLOW-list over the tokens actually emitted. The deny-list this replaced could only
    reject a name some *other* role owned, so an invented token like [[CONTINGENCY]] -- in
    no role's field list at all -- was never checked against anything and passed silently.

    Three buckets, because they mean different things:
      foreign  a real field belonging to another role: the record is bleeding across passes
      near     nothing owns it but it is one edit away from one of ours ([[DISTINGISHING]]):
               the corrupted-field signature of L-PROMPT-TOKEN-BUDGET
      unknown  invented outright

    Derived from the role table rather than listed, so adding a role cannot leave a stale
    entry that rejects one of its own legitimate fields.
    """
    own = set(DESCRIBER_ROLES[role]['fields'])
    other = set(FRAME_FIELDS)
    for spec in DESCRIBER_ROLES.values():
        other.update(spec['fields'])
    other -= own

    foreign, near, unknown = {}, {}, {}
    for name in TOKEN.findall(out):
        base = name.split(':')[0].strip()        # [[CHAR: label]] -> CHAR
        if base in own or base == NOT_FOUND_NAME:
            continue                             # NOT_FOUND has its own checks below
        if base in other:
            foreign[base] = None
            continue
        close = difflib.get_close_matches(base, own, n=1, cutoff=NEAR_MISS_RATIO)
        (near if close else unknown)[base] = close[0] if close else None
    return foreign, near, unknown


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
    foreign, near, unknown = classify_tokens(out, role)
    for f in foreign:
        errs.append(f'foreign field [[{f}]] -- not part of the {role} record')
    for f, closest in near.items():
        errs.append(f'corrupted field [[{f}]] -- no role owns it; looks like [[{closest}]]')
    for f in unknown:
        errs.append(f'invented field [[{f}]] -- not a field of any role')

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

    # --- a two-level closed vocabulary: the sub-term must belong to the coarse term
    if spec['coarse_sub']:
        cf, sf, vocab = spec['coarse_sub']
        coarse = field_text(cf).lower().strip(' .')
        sub = field_text(sf).lower().strip(' .')
        if coarse in vocab:
            allowed = vocab[coarse]
            if allowed and sub not in allowed and sub != 'not determinable':
                errs.append(f'[[{sf}]] is {sub!r}, which is not a sub-term of '
                            f'[[{cf}]] {coarse!r} ({", ".join(allowed)}, or not determinable)')
            elif not allowed and sub != 'none':
                errs.append(f'[[{sf}]] is {sub!r}, but [[{cf}]] {coarse!r} has no '
                            f'sub-terms -- it must say none')

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
    p_d.add_argument('--id-prefix', metavar='PREFIX',
                     help='validate only records whose case id starts with PREFIX. A chained '
                          'test writes two roles into one run file, and each has to be checked '
                          "against its own rules -- e.g. --role style_class --id-prefix sw_")

    for p in (p_h3, p_d):
        p.add_argument('-v', '--verbose', action='store_true',
                       help='also print passing cases')

    a = ap.parse_args()
    recs = parse_records(pathlib.Path(a.path).read_text(encoding='utf-8'))

    results, brackets = [], {}
    for i, r in enumerate(recs, 1):
        group, case_id = head_parts(r['model'])
        if getattr(a, 'id_prefix', None) and not (case_id or '').startswith(a.id_prefix):
            continue
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

    if getattr(a, 'id_prefix', None) and not results:
        raise SystemExit(f'ERROR: no records in {a.path} have a case id starting with '
                         f'{a.id_prefix!r} -- nothing was checked.')

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
