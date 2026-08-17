#!/usr/bin/env python3
"""Score a run's CONTENT against a test file's `_expected` answer key.

This is the second of two failure pipelines, and the two must not be conflated:

  scripts/validate.py  -> FORMAT.  Does the record have the right fields, in the right
                          order, with no reserved characters? Cannot see content at all.
  scripts/score.py     -> CONTENT. Did the model say the right thing? Needs an answer
                          key, which validate.py never reads.

Only the counts printed here feed the adjudication thresholds in `.claude/CLAUDE.md`.
Format failures are reported separately and are never part of `F`.

The `_expected` map lives at the top level of the test file, keyed by case id:

    "_expected": {
      "sty_coraline1": "stop-motion / none",
      "sty_chair":     "UNSCORABLE (amb) -- the pixels do not settle photo vs render",
      "sty_kasia":     "2D cel / (sub CONTESTED -- score the coarse term only)"
    }

Two markers drop a case out of the denominator, and they mean different things:

  UNSCORABLE  the IMAGE does not determine the answer. Permanent -- pixels don't change.
  CONTESTED   OUR DEFINITIONS cannot decide a decidable image. PROVISIONAL: the ruling
              expires when the vocabulary that made it contested changes, and the case
              must re-enter scoring rather than staying excluded forever.

A marker may appear on the whole value or on one field, e.g.
"2D cel / (sub CONTESTED)" scores the coarse term and excludes the sub-term only.

ACCEPT-SETS (session 16)
------------------------
An `_expected` value may instead be an OBJECT, which is how a case records that more
than one answer is genuinely acceptable:

    "sw_avatar_1": {
      "expect":  "2D cel / digital / western toon | anime / colour",
      "why":     "western production in an anime idiom; the traditions are converging",
      "control": ["sw_ivy_toon", "sw_april_1987"]
    }

  expect   the same "a / b / c" grammar as the string form, except that a field may
           offer `|`-separated ALTERNATIVES. The first is the PRIMARY -- what we would
           write if forced to pick one. Anything outside the set is still a miss.
  why      free prose: why this case admits more than one answer. Also legal on a
           case with no accept-set, purely to tag it -- misses are grouped by `why`
           at the end of the report, which is what fills the six-case adjudication
           cap with one exemplar per pattern instead of a guess.
  control  case ids where this SAME distinction is NOT ambiguous and must still be
           got right. This is the point of the field: an accept-set removes selection
           pressure on a distinction, so the model may collapse it everywhere. If an
           accept-set fires while its controls miss, the change bought nothing, and
           this report says so.

DELIBERATELY OUT OF SCOPE: an accept-set is per-FIELD, so it cannot express "two
fields each holding half a true answer" (`april_1987_figure` -- a photograph OF a
figure, an illegal pairing where neither half is wrong). Those stay CONTESTED. They
are a hole in the vocabulary, and letting the scorer absorb them would remove the
pressure to fix it -- the same error as drawing an accept-set loosely enough to hide
the `digital` over-attractor.

Usage:
  python scripts/score.py tests/describer_style.json runs/run-*.txt --fields MEDIUM SUB_MEDIUM IDIOM TREATMENT
  python scripts/score.py tests/describer_style_sweep.json <run> --fields MEDIUM SUB_MEDIUM
  python scripts/score.py <test> <run> --fields <...> --misses-only
  python scripts/score.py <test> <run> --fields <...> --strict     # ignore accept-sets: primary only

--fields is required -- no default, since a field list from one role silently mis-scores
every other role as all-"(missing)" rather than erroring. Check a sample _expected entry
in the test file to see the field count and "/" order.
"""

import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from validate import (parse_records, head_parts, vocab_terms, DESCRIBER_ROLES,  # noqa: E402
                      COLOUR_MODIFIERS)

# Field name -> (source field, vocab, vocab_terms() kwargs), merged from every role's
# 'derived' entry in DESCRIBER_ROLES (validate.py). Flat rather than keyed by role because
# score.py's --fields is role-agnostic and a derived field name is unique across roles today
# (COLOUR belongs only to 'object') -- the first content-scored field this project has ever
# pulled out of another field's free text instead of matching it literally (session 30).
DERIVED = {}
for _role in DESCRIBER_ROLES.values():
    DERIVED.update(_role.get('derived') or {})

MARKERS = ('UNSCORABLE', 'CONTESTED')
ACCEPT_SEP = '|'
OBJ_KEYS = {'expect', 'why', 'control'}


def normalise(raw, cid):
    """An `_expected` value -> (expect string, why, [control ids]).

    Accepts both legal forms: the plain string that every pre-session-16 entry uses,
    and the accept-set object. Validating here rather than at the point of use means a
    typo in a hand-edited key fails loudly on the spot instead of silently scoring the
    case against a missing expectation."""
    if isinstance(raw, str):
        return raw, None, []
    if not isinstance(raw, dict):
        raise SystemExit(f'ERROR: _expected["{cid}"] must be a string or an object, '
                         f'got {type(raw).__name__}.')
    unknown = set(raw) - OBJ_KEYS
    if unknown:
        raise SystemExit(f'ERROR: _expected["{cid}"] has unknown key(s) '
                         f'{sorted(unknown)}; legal keys are {sorted(OBJ_KEYS)}.')
    if 'expect' not in raw:
        raise SystemExit(f'ERROR: _expected["{cid}"] is an object with no "expect" key.')
    control = raw.get('control') or []
    return raw['expect'], raw.get('why'), [control] if isinstance(control, str) else list(control)


def field(output, name):
    m = re.search(r'\[\[' + re.escape(name) + r'\]\](.*)', output)
    return m.group(1).strip() if m else '(missing)'


def split_expected(raw, n_fields):
    """An `_expected` value -> per-field expectations, or a whole-record marker.

    Returns (marker, [per-field expectation, ...]). `marker` is set only when the
    WHOLE record is excluded; a per-field marker stays in the list so the other
    fields still score."""
    for mk in MARKERS:
        # whole-record only when the marker leads the value -- "UNSCORABLE (amb)".
        if raw.strip().upper().startswith(mk):
            return mk, []
    parts = [p.strip() for p in raw.split('/')]
    # Tolerate an expectation that names fewer fields than we are scoring.
    parts += ['(unspecified)'] * (n_fields - len(parts))
    return None, parts[:n_fields]


def marker_in(text):
    for mk in MARKERS:
        if mk in text.upper():
            return mk
    return None


def clean(expectation):
    """Drop a trailing parenthetical note so it cannot contaminate the comparison.

    `_expected` values carry rationale inline -- "photograph / colour  (tie-break 2:
    a photograph OF a watercolour)" -- and splitting on "/" leaves that note glued to
    the last field. Only called after marker_in(), so a marker inside the parenthetical
    has already been honoured."""
    return re.sub(r'\s*\([^()]*\)\s*$', '', expectation).strip()


def alternatives(expectation):
    """A field expectation -> its accepted values, PRIMARY FIRST.

    A field with no `|` yields a one-element list, so the caller has a single path
    for both forms and the string entries cannot behave differently by accident."""
    return [p.strip() for p in clean(expectation).split(ACCEPT_SEP) if p.strip()]


def _derived_value(output, name):
    """A DERIVED field's scored value (rank 1 only) plus its full ranked extraction, for a
    field name declared in DESCRIBER_ROLES -- e.g. COLOUR, pulled out of [[MATERIAL]] rather
    than written literally by the model. Rank 1 is what scores; the full list is diagnostic
    only, so a near-tie or a rank-2 match is visible without any new ground-truth machinery
    (.claude/CLAUDE.md's decision this round: start at strict rank 1, watch the rest).
    A matched synonym (e.g. 'beige') is mapped to its canonical vocab term ('light brown')
    before being returned, so every value this function hands back is a vocabulary word."""
    source, vocab, kwargs, aliases = DERIVED[name]
    raw = vocab_terms(field(output, source).lower(), vocab, **kwargs)
    terms = [aliases.get(t, t) for t in raw]
    return (terms[0] if terms else '(none extracted)'), terms


def read_run(path, fields):
    """({case id: tuple of emitted field values}, {case id: {derived field: full ranked
    extraction}}) for one concatenated run file. The second dict is empty wherever no
    requested field is DERIVED, and is diagnostic-only -- it never affects scoring."""
    got, detail = {}, {}
    for r in parse_records(pathlib.Path(path).read_text(encoding='utf-8')):
        _, cid = head_parts(r['model'])
        if not cid:
            continue
        values, ranked = [], {}
        for f in fields:
            if f in DERIVED:
                v, full = _derived_value(r['output'], f)
                values.append(v)
                ranked[f] = full
            else:
                values.append(field(r['output'], f))
        got[cid] = tuple(values)
        if ranked:
            detail[cid] = ranked
    return got, detail


def _field_match(field_name, got, alt):
    """Exact match, plus -- for a DERIVED field only (session 30) -- one directional
    loosening: a MODIFIER+hue extraction satisfies its bare-hue expectation ('dark grey'
    credits against expected 'grey'), because the model was right about the hue and only
    added information the ground truth's rank-1 pick happened not to carry. NOT the
    reverse (a bare hue never satisfies a modified expectation), and never across two
    different modifiers -- ob_van's expected 'light brown' still needs that modifier to
    mean something, or the mapping that produced it would be pointless."""
    g, a = got.strip().lower(), alt.strip().lower()
    if g == a:
        return True
    if field_name in DERIVED:
        return any(g == f'{m} {a}' for m in COLOUR_MODIFIERS)
    return False


def case_verdict(expect, emitted, nfields, fields=(), strict=False):
    """Score ONE case.

    Returns (state, why, n_field_excluded, field_contested, fired, verdicts):
      state True  = pass, False = miss, None = dropped from the denominator
      why          the exclusion marker when state is None, else None
      verdicts     per-field True/False/None, aligned to `fields`. Needed because a
                   CONTROL guards one AXIS, not the whole record: sw_nadia's idiom can
                   be right while its sub-medium misses for unrelated reasons, and
                   reporting that as a collapsing idiom distinction is a false alarm.
      fired        [(field name, matched value, primary value), ...] for accept-sets
                   that were LOAD-BEARING -- the emitted value matched a non-primary
                   alternative, so without the set this case would have missed. An
                   accept-set that matched its own primary did nothing and is not
                   reported, which keeps the count honest about what was bought.

    `expect` is the normalised expectation STRING; callers pass normalise()'s first
    element. `strict` ignores every alternative but the primary, which is what makes
    the old and new scoring semantics comparable on identical model output.

    Factored out so the baseline run in --baseline is scored by exactly the same
    logic as the run being reported -- a second implementation would drift and
    silently mis-report regressions.
    """
    marker, want = split_expected(expect, nfields)
    if marker:
        return None, marker, 0, False, [], [None] * nfields

    verdicts, per_field, contested, fired = [], 0, False, []
    for i, (w, g) in enumerate(zip(want, emitted)):
        mk = marker_in(w)
        if mk or w == '(unspecified)':
            verdicts.append(None)                        # field excluded
            per_field += 1
            if mk == 'CONTESTED':
                contested = True
            continue
        alts = alternatives(w)
        if strict:
            alts = alts[:1]
        fname = fields[i] if i < len(fields) else None
        hit = next((a for a in alts if _field_match(fname, g, a)), None)
        verdicts.append(hit is not None)
        if hit is not None and hit != alts[0]:
            fired.append((fields[i] if i < len(fields) else f'field {i}', hit, alts[0]))

    scored = [v for v in verdicts if v is not None]
    if not scored:
        return None, 'CONTESTED', per_field, contested, [], verdicts
    return all(scored), None, per_field, contested, fired, verdicts


def wrap(text, label):
    """Fold prose to the report's width, labelling the first line only.

    Continuation lines are indented to the label's width rather than repeating it --
    a `why` string runs several lines and a repeated label reads as several `why`s."""
    cont = ' ' * len(label)
    out, line = [], label
    for word in text.split():
        if len(line) + len(word) + 1 > 96 and line.strip() != label.strip():
            out.append(line.rstrip())
            line = cont
        line += word + ' '
    out.append(line.rstrip())
    return '\n'.join(out)


def accept_axes(expect, fields):
    """Indices of the fields on which `expect` declares alternatives."""
    _mk, want = split_expected(expect, len(fields))
    return [i for i, f in enumerate(want)
            if f != '(unspecified)' and not marker_in(f) and len(alternatives(f)) > 1]


def report_accept_sets(key, fired_of, perfield, got, w, fields, strict):
    """Report which accept-sets were load-bearing, and how their controls did.

    The controls are the point. An accept-set removes selection pressure on the very
    distinction it forgives, so the model may collapse it everywhere -- including
    where the distinction is required. A fired set whose controls are missing is the
    signal that the change bought nothing, and it is worth more than the score.

    A control is judged ONLY on the axes the accept-set covers, never on whole-case
    pass/fail. sw_nadia controls the western-toon/anime IDIOM call and gets it right,
    while missing SUB_MEDIUM to the unrelated `digital` over-attractor; scoring it
    whole-case would raise a collapse warning about a distinction that is fine, and a
    warning that cries wolf is worse than no warning."""
    declared = [cid for cid, (expect, _, _) in key.items()
                if ACCEPT_SEP in expect and not split_expected(expect, 1)[0]]
    if not declared:
        return

    print()
    if strict:
        print(f'accept-sets  {len(declared)} declared, ALL IGNORED (--strict: primary only)')
        return

    print(f'accept-sets  {len(declared)} declared · {len(fired_of)} fired '
          f'(matched a non-primary value, so the set is what made the case pass)')

    collapsing = []
    for cid in declared:
        expect, why, control = key[cid]
        axes = accept_axes(expect, fields)
        axis_names = ', '.join(fields[i] for i in axes) or '(none)'
        marks = fired_of.get(cid)
        if marks:
            shown = ' · '.join(f"{f} = '{hit}' (primary '{prim}')" for f, hit, prim in marks)
            print(f'  FIRED  {cid:{w}}  {shown}')
        else:
            print(f'  --     {cid:{w}}  not load-bearing this round  [{axis_names}]')
        if why:
            print(wrap(why, ' ' * 9 + 'why      '))
        if control:
            _mk, want = split_expected(expect, len(fields))
            states = []
            for c in control:
                v = perfield.get(c)
                if v is None:
                    states.append((c, 'not in this test'))
                    continue
                on_axis = [v[i] for i in axes if i < len(v)]
                scored = [x for x in on_axis if x is not None]
                if not scored:
                    states.append((c, 'excluded'))
                elif all(scored):
                    states.append((c, 'ok'))
                else:
                    # A control that missed ON the axis has still only COLLAPSED if it
                    # drifted to a value this accept-set forgives. sw_marker misses
                    # SUB_MEDIUM to `digital` -- the over-attractor, nothing to do with
                    # marker-vs-pencil -- and calling that a collapse would blame the
                    # accept-set for a defect it neither caused nor hides.
                    drift = [got[c][i].strip().lower() for i in axes
                             if i < len(v) and v[i] is False
                             and any(_field_match(fields[i], got[c][i], alt)
                                     for alt in alternatives(want[i]))]
                    states.append((c, f"COLLAPSED to '{drift[0]}'" if drift
                                   else 'miss (off-distinction)'))
            print(' ' * 9 + f'controls on {axis_names}: '
                  + ' · '.join(f'{c} {s}' for c, s in states))
            if marks and any(s.startswith('COLLAPSED') for _, s in states):
                collapsing.append(cid)

    if collapsing:
        print()
        print(wrap('WARNING: ' + ', '.join(sorted(collapsing)) + ' had an accept-set fire '
                   'while a STRICT CONTROL COLLAPSED -- drifted, on the same axis, to a '
                   'value this very accept-set forgives. That is the failure mode the '
                   'control field exists to catch: the model is not resolving a genuinely '
                   'ambiguous case, it is losing the distinction everywhere. Read this '
                   'before crediting the accept-set with the pass.', '  '))


def report_why_groups(key, label):
    """Group the misses by their `why` tag, so the six-case cap can be filled with one
    exemplar per pattern rather than by hand-triaging the list every round."""
    groups = {}
    for cid, (_expect, why, _ctl) in key.items():
        if label.get(cid) == 'MISS':
            groups.setdefault(why, []).append(cid)
    if not any(k for k in groups):          # no miss carries a tag: nothing to group by
        return

    print()
    print('misses grouped by `why`:')
    for why in sorted(groups, key=lambda k: (k is None, k or '')):
        # First sentence only. A `why` written for an accept-set is a full rationale --
        # controls, reversal conditions, the lot -- and printing all of it as a group
        # HEADER buries the one thing this section is for, which is seeing the shape of
        # the miss population at a glance.
        head = (why or '(untagged)').split('. ')[0].strip()
        if why and len(head) < len(why.rstrip('.')):
            head += ' [...]'
        print(wrap(head, '  '))
        print(wrap(', '.join(sorted(groups[why])), '      '))


def banner(verdict, n_miss, n, threshold, enriched):
    """Repeat the gate verdict where it cannot be scrolled past, with the required action.

    It used to print once, as a single line under ~140 lines of per-case output, and was
    missed in two consecutive sessions despite being emitted correctly every time. A rule
    that is well-written, machine-emitted and still skipped twice needs a mechanism, not
    more prose. Suppress with --no-gate when an automated caller does its own handling."""
    action = ('lead with the SYSTEMATIC FINDING, attach 2-3 exemplars'
              if verdict == 'DIAGNOSIS' else
              'bring up to %d case(s), one per distinct pattern' % min(n_miss, 6))
    body = ['GATE: ' + verdict,
            '%d content miss(es) of %d scorable - threshold %d%s'
            % (n_miss, n, threshold, '  (enriched: gated on movement)' if enriched else ''),
            action,
            'ask BEFORE designing any fix, and BEFORE archive_run.py --clean']
    w = max(len(x) for x in body) + 2
    print()
    print('+' + '-' * w + '+')
    for x in body:
        print('| ' + x.ljust(w - 1) + '|')
    print('+' + '-' * w + '+')


def report_clusters(key, got, perfield, fields):
    """Group the misses by (field, expected -> got). One cluster is one candidate finding.

    Step 3 of the adjudication protocol says to pick cases for what they TEACH, never the
    first six in file order -- which requires knowing which failures share a direction.
    Doing that by hand is how three separately-explained CONTESTED rulings hid a single
    over-attractor for eight sessions; see L-EXCLUSIONS-HIDE-A-SHARED-DIRECTION."""
    clusters = {}
    for cid, per in perfield.items():
        if not per:
            continue
        want = [x.strip() for x in key[cid][0].split('/')]
        emitted = got.get(cid) or []
        for i, f in enumerate(fields):
            if i < len(per) and per[i] is False and i < len(emitted) and i < len(want):
                primary = want[i].split(ACCEPT_SEP)[0].strip()
                clusters.setdefault((f, primary, emitted[i].strip()), []).append(cid)
    if not clusters:
        return
    print()
    print('miss clusters -- one cluster is one candidate finding; take exemplars from '
          'DIFFERENT rows')
    rows = sorted(clusters.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    for (f, want, emitted), ids in rows:
        names = sorted(i[3:] if i.startswith('sw_') else i for i in ids)
        head = '%2dx  %s  %s -> %s' % (len(ids), f, want, emitted)
        print('  %-54s %s%s' % (head, ', '.join(names[:6]),
                                ' ...' if len(names) > 6 else ''))
    singles = sum(1 for _, ids in rows if len(ids) == 1)
    print('  (%d cluster(s), %d of them a single case)' % (len(rows), singles))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('test', help='test JSON carrying the _expected map')
    ap.add_argument('run', help='a concatenated runs/run-*.txt')
    ap.add_argument('--fields', nargs='+', default=None,
                    help='fields the _expected value describes, in "a / b" order -- '
                         'required, no default (session 31: a hardcoded style-role default '
                         'used to silently mis-score every other role as all-"(missing)")')
    ap.add_argument('--misses-only', action='store_true',
                    help='omit the passing rows')
    ap.add_argument('--baseline', metavar='RUN',
                    help='the previous round of the SAME test. On an enriched test the gate '
                         'is on movement, not level, so this is what makes it meaningful: it '
                         'reports regressions (passed then, missing now) and cases that '
                         'changed to a DIFFERENT wrong answer.')
    ap.add_argument('--strict', action='store_true',
                    help='honour only the PRIMARY value of every accept-set, i.e. score '
                         'under the pre-session-16 semantics. Run a file both ways to get a '
                         'controlled A/B of the scoring change on identical model output.')
    ap.add_argument('--no-gate', action='store_true',
                    help='suppress the gate banner and the miss-cluster report. For an '
                         'automated caller that does its own handling -- the default is '
                         'deliberately loud, because this verdict was missed in two '
                         'consecutive sessions while being printed correctly every time.')
    a = ap.parse_args()

    spec = json.loads(pathlib.Path(a.test).read_text(encoding='utf-8'))
    expected = spec.get('_expected')
    if not expected:
        raise SystemExit(f'ERROR: {a.test} has no top-level "_expected" map -- '
                         f'nothing to score against.')

    if not a.fields:
        sample_cid, sample_val = next(iter(expected.items()))
        raise SystemExit(
            f'ERROR: --fields is required -- there is no safe default across roles.\n'
            f'  A sample _expected entry from {a.test}:\n'
            f'    "{sample_cid}": {sample_val!r}\n'
            f'  Count the "/"-separated segments and name each field, in that order '
            f'(cross-check against the role\'s field list in DESCRIBER_ROLES, scripts/validate.py).\n'
            f'  Example: --fields OBJECT_KIND COLOUR')

    got, derived_detail = read_run(a.run, a.fields)

    # Normalise every entry up front so a malformed object fails before any scoring
    # happens, rather than half way down a report the reader might already trust.
    key = {cid: normalise(raw, cid) for cid, raw in expected.items()}

    rows, excluded = [], []
    field_contested = set()
    n_pass = n_miss = 0
    per_field_excluded = 0
    state, fired_of, label, perfield = {}, {}, {}, {}

    for cid, (expect, _why, _ctl) in key.items():
        if cid not in got:
            excluded.append((cid, 'NOT RUN', expect))
            label[cid] = 'not run'
            continue
        ok, why, per_field, contested, fired, verdicts = case_verdict(
            expect, got[cid], len(a.fields), a.fields, a.strict)
        perfield[cid] = verdicts
        per_field_excluded += per_field
        if contested:
            field_contested.add(cid)
        state[cid] = ok
        if fired:
            fired_of[cid] = fired
        if ok is None:
            excluded.append((cid, why, ' / '.join(got[cid])))
            label[cid] = f'skip ({why})'
            continue
        n_pass += ok
        n_miss += not ok
        label[cid] = 'pass' if ok else 'MISS'
        if not ok or not a.misses_only:
            rows.append((cid, ' / '.join(got[cid]), expect, ok))

    w = max((len(c) for c, *_ in rows + excluded), default=10)
    for cid, g, e, ok in rows:
        print(f'{"ok " if ok else "MISS"}  {cid:{w}}  {g:34}  expected {e}')
        if not ok:
            # Diagnostic only -- never scored. A DERIVED field (COLOUR) that missed on rank 1
            # may still have matched further down its own ranked extraction; showing the full
            # list is how a near-tie or a rank-2 match gets watched (this round's decision)
            # without inventing accept-set machinery to chase it prematurely.
            for i, fname in enumerate(a.fields):
                if fname in DERIVED and i < len(perfield.get(cid) or []) \
                        and perfield[cid][i] is False:
                    full = derived_detail.get(cid, {}).get(fname)
                    if full and len(full) > 1:
                        print(f'      {fname} full ranked extraction: {full}')

    if excluded:
        print()
        for cid, why, g in excluded:
            print(f'skip  {cid:{w}}  {g:34}  [{why}]')

    n = n_pass + n_miss
    print()
    print(f'CONTENT  {n_pass}/{n} exact   ({n_miss} misses)')

    n_contested = sum(1 for _, why, _ in excluded if why == 'CONTESTED')
    n_unscorable = sum(1 for _, why, _ in excluded if why == 'UNSCORABLE')
    n_notrun = sum(1 for _, why, _ in excluded if why == 'NOT RUN')
    total = n + n_contested + n_unscorable
    print(f'excluded {len(excluded)}: {n_contested} contested · '
          f'{n_unscorable} unscorable · {n_notrun} not run'
          + (f' · {per_field_excluded} field(s) on {len(field_contested)} '
             f'partly-scored case(s)' if per_field_excluded else ''))

    if total:
        # Surfaced deliberately: a growing contested share means the vocabulary is
        # asking for a distinction the images don't support (.claude/CLAUDE.md).
        # Counts partly-contested cases too -- a contested SUB-term is still the
        # vocabulary failing to decide, which is the signal this number exists for.
        contested_any = n_contested + len(field_contested)
        print(f'contested rate  {contested_any}/{total} = '
              f'{100 * contested_any / total:.0f}% of ruled cases'
              + (f'  ({n_contested} whole, {len(field_contested)} partial)'
                 if field_contested else ''))
        print('  NOTE: contested rulings are PROVISIONAL -- they expire when the '
              'vocabulary changes.')

    report_accept_sets(key, fired_of, perfield, got, w, a.fields, a.strict)
    report_why_groups(key, label)

    # The gate infers "high failure rate -> structural problem", and that inference needs a
    # REPRESENTATIVE sample. An enriched test (one deliberately stocked with known failures
    # so a fix is measurable) has a high rate BY CONSTRUCTION, so its level says nothing --
    # gate it on movement against the previous round instead. See .claude/CLAUDE.md.
    threshold = max(6, round(0.15 * n))
    enriched = spec.get('_gate') == 'enriched'

    if not enriched:
        verdict = 'ADJUDICATION' if n_miss <= threshold else 'DIAGNOSIS'
        print(f'\ngate: F={n_miss} vs threshold max(6, 15% of {n})={threshold}  ->  {verdict}')
    elif not a.baseline:
        verdict = 'ADJUDICATION'
        print(f'\ngate: ENRICHED test, no --baseline given  ->  {verdict}')
        print(f'      the level ({n_miss}/{n} misses) is by construction and means nothing '
              f'on its own.')
        print('      pass --baseline <previous run of this test> to gate on movement.')
    else:
        base, _base_detail = read_run(a.baseline, a.fields)
        regressed, fixed, changed = [], [], []
        for cid, now in state.items():
            if cid not in base or now is None:
                continue
            then, *_ = case_verdict(key[cid][0], base[cid], len(a.fields),
                                    a.fields, a.strict)
            if then is None:
                continue
            if then and not now:
                regressed.append(cid)
            elif now and not then:
                fixed.append(cid)
            elif not now and not then and base[cid] != got[cid]:
                changed.append(cid)

        verdict = 'ADJUDICATION' if len(regressed) <= threshold else 'DIAGNOSIS'
        print(f'\ngate: ENRICHED test, gated on movement vs {pathlib.Path(a.baseline).name}')
        print(f'      fixed {len(fixed)} · regressed {len(regressed)} · '
              f'still missing but a DIFFERENT wrong answer {len(changed)}')
        for label, ids in (('fixed', fixed), ('REGRESSED', regressed),
                           ('changed', changed)):
            if ids:
                print(f'        {label:10} {", ".join(sorted(ids))}')
        print(f'      R={len(regressed)} vs threshold max(6, 15% of {n})={threshold}  '
              f'->  {verdict}')
        if changed:
            print('      NOTE: a "changed" case is a real signal -- a fix moved it sideways. '
                  'It is worth a slot; an unchanged known failure is not.')

    if verdict == 'DIAGNOSIS':
        print('      lead with the systematic finding, and attach 2-3 exemplars')
    else:
        print(f'      bring {min(n_miss, 6)} of them'
              + (' (triage to six, one per pattern)' if n_miss > 6 else ''))

    if not a.no_gate:
        banner(verdict, n_miss, n, threshold, enriched)
        report_clusters(key, got, perfield, a.fields)
    print('      format failures are counted separately -- run scripts/validate.py')

    sys.exit(0 if n_miss == 0 else 1)


if __name__ == '__main__':
    main()
