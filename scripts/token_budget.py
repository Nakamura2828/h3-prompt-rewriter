#!/usr/bin/env python3
"""Measure system-prompt length against the only limit we can actually demonstrate.

WHAT CHANGED, AND WHY. This script used to enforce an ADHERENCE line at ~3.7k tokens, on the
theory that past it the model starts trading one instruction for another. Two experiments have
now failed to reproduce that, at a combined 1,166 model calls:

  round 1  padded a known-good prompt with INERT filler, logic held constant.
           26/26 format at 4,982 tokens in all four arms. Noise floor zero.
  round 2  held total length fixed at ~5,000 and SUBSTITUTED real rules for that filler,
           2,239 -> 3,805 live-rule tokens. No monotone degradation in format or content,
           in either arm -- including five cells within 20 tokens of 3,386, the exact count
           at which describer_style once dropped to 39/45 and began corrupting field tokens.
           The model also OBEYED up to 21 independently checkable added constraints, so it is
           not silently dropping rules either.

  Full reports: .claude/experiments/bloat/REPORT.md and .claude/experiments/bloat2/REPORT.md

So the ~3.7k line was not a property of the model, and `--check` was failing prompts at 3,885
that both rounds show to be fine. It has been RETIRED rather than moved: relocating an invented
number just puts the artificial barrier somewhere else.

WHAT IS ENFORCED NOW is the real, mechanical ceiling, which had never been guarded at all: a
prompt plus its inputs and its output must fit in the context window, or the server silently
truncates. That is a genuine failure mode with a genuine number behind it.

    headroom = n_ctx - image tokens - max_tokens - room for the user prompt

On the current config that is 16,384 - 2,048 - 2,048 - 1,024 = 11,264 tokens of system prompt.
The largest prompt in the repo is 3,740, i.e. about a third of it.

WHAT IS STILL UNKNOWN, so that silence is not read as a guarantee: everything between ~5,000
tokens (the most either round measured) and the context ceiling is UNTESTED, not known-good. And
neither round tested rules that genuinely COMPETE with each other, which is the shape of the one
degradation the project has ever recorded. What costs a rule is another rule's SEMANTICS, not its
size -- see `L-PROMPT-TOKEN-BUDGET` and `L-DONT-OVER-CONSTRAIN`.

Counts come from the llama-server's own /tokenize endpoint, so they are exact for the model
actually running -- character count is a poor proxy, because the [[FIELD]] tokens and the closed
vocabularies tokenize very unevenly against prose.

Usage:
  python scripts/token_budget.py                                  every prompt, sorted
  python scripts/token_budget.py prompts/describer_style.txt      just this one
  python scripts/token_budget.py prompts/describer_style.txt --sections
  python scripts/token_budget.py --check                          exit 1 only if it cannot fit
  python scripts/token_budget.py --check --image-tokens 4096      a heavier image budget
"""
import argparse
import glob
import io
import json
import os
import re
import sys
import urllib.error
import urllib.request

SERVER = 'http://localhost:8080/tokenize'

# The context budget. Every one of these is a real number about the running server or the
# harness, not an inference about the model's behaviour -- which is the whole point of the
# change. Override any of them from the command line when the situation differs.
#
#   N_CTX          llama-server's -c, per slot. Read live from /props when reachable.
#   IMAGE_TOKENS   --image-min-tokens is a FLOOR (it scales small images UP); --image-max-tokens
#                  would be the cap and we do not set one, so cost is unbounded above.
#                  MEASURED session 14, via usage.prompt_tokens on a one-token reply:
#                      417x480   (0.20 MPx)  2,109      1920x800   (1.54 MPx)  2,132
#                      1049x699  (0.73 MPx)  2,074      1920x1440  (2.76 MPx)  2,702
#                      1000x1000 (1.00 MPx)  2,118
#                  So the floor BINDS for essentially the whole corpus -- an 8x range in pixels
#                  is a 3% range in tokens -- and only past ~1.5 MPx does size start to cost.
#                  2048 is therefore a good default and a slight under-estimate; pass
#                  --image-tokens 2700 to budget the largest image we actually hold.
#   OUTPUT_TOKENS  run_tests.py's max_tokens default.
#   USER_RESERVE   room for the user turn. The describers send ~30 tokens; the fl2va composer
#                  sends ~900 (a full frame record plus the delta), so 1,024 is the honest
#                  reserve for the worst case we actually run.
N_CTX = 16384
IMAGE_TOKENS = 2048
OUTPUT_TOKENS = 2048
USER_RESERVE = 1024

# Fraction of headroom above which a prompt is worth noticing. This is NOT a rediscovered
# adherence line -- it is three quarters of a real ceiling, and it means "you are approaching
# truncation", which is a mechanical fact rather than a claim about instruction-following.
HIGH_SHARE = 0.75


def headroom(n_ctx=N_CTX, image=IMAGE_TOKENS, output=OUTPUT_TOKENS, user=USER_RESERVE):
    """Tokens available to the system prompt before the context window overflows."""
    return n_ctx - image - output - user


DEFAULT_HEADROOM = headroom()


def count(text, server=SERVER):
    req = urllib.request.Request(
        server, data=json.dumps({'content': text}).encode('utf-8'),
        headers={'Content-Type': 'application/json'})
    return len(json.load(urllib.request.urlopen(req, timeout=30))['tokens'])


def server_n_ctx(server=SERVER):
    """The running server's context per slot, or None if it cannot be read.

    Preferred over the N_CTX constant for the same reason counts come from /tokenize: the real
    number is available, so there is no reason to assume one. Returns None rather than raising,
    so the constant can stand in when the server is down.
    """
    try:
        url = server.rsplit('/', 1)[0] + '/props'
        with urllib.request.urlopen(url, timeout=15) as r:
            gs = json.load(r).get('default_generation_settings', {})
        return int(gs['n_ctx']) if gs.get('n_ctx') else None
    except Exception:                     # noqa: BLE001 -- fall back to the constant, never crash
        return None


def band(n, room=None):
    """(marker, note) for a token count, against the CONTEXT headroom.

    Kept as a two-value tuple because reference/prompt_archive/measure.py imports and calls it
    as band(n). Its meaning has changed -- it no longer reports an adherence band, because there
    is no evidence for one -- but its shape has not.
    """
    room = DEFAULT_HEADROOM if room is None else room
    if n > room:
        return 'OVER', 'will not fit: {} tokens against {} of headroom'.format(n, room)
    if n >= HIGH_SHARE * room:
        return 'HIGH', 'over {:.0%} of the {} context headroom -- watch for truncation'.format(
            HIGH_SHARE, room)
    return 'ok  ', ''


def split_sections(text):
    """[(name, body)] split on ALL-CAPS heading lines.

    Heuristic, deliberately: these prompts are hand-written prose with no markup, and a
    heading is recognisable as a line whose first word is capitalised throughout. Field
    lines ([[X]] ...) and bullets are excluded so they don't read as headings.
    """
    out, name, buf = [], '(preamble)', []
    for line in text.split('\n'):
        first = line.split(' ')[0] if line else ''
        # Hyphens are allowed inside the first word: 'TIE-BREAK RULES' is a heading, and
        # str.isalpha() rejects it, which silently folded that whole section into the one
        # above it and made the vocabulary look bigger than it is.
        is_head = (len(first) >= 3 and first.isupper()
                   and first.replace('-', '').isalpha()
                   and not line.startswith(('[', '-', ' ')))
        if is_head:
            out.append((name, '\n'.join(buf)))
            name, buf = line.strip(), [line]
        else:
            buf.append(line)
    out.append((name, '\n'.join(buf)))
    return [(n, b) for n, b in out if b.strip()]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('paths', nargs='*', help='prompt files (default: prompts/*.txt)')
    ap.add_argument('--sections', action='store_true',
                    help='break each file down by section -- use this to find what to cut')
    ap.add_argument('--check', action='store_true',
                    help='exit 1 only if a prompt cannot fit its context budget')
    ap.add_argument('--server', default=SERVER)
    ap.add_argument('--n-ctx', type=int, default=None,
                    help='context per slot (default: read from the server, else %d)' % N_CTX)
    ap.add_argument('--image-tokens', type=int, default=IMAGE_TOKENS,
                    help='budget for the image; --image-min-tokens is a FLOOR, so raise this '
                         'for large images (default: %(default)s)')
    ap.add_argument('--output-tokens', type=int, default=OUTPUT_TOKENS,
                    help='max_tokens reserved for the reply (default: %(default)s)')
    ap.add_argument('--user-reserve', type=int, default=USER_RESERVE,
                    help='room for the user turn; the fl2va composer sends ~900 '
                         '(default: %(default)s)')
    a = ap.parse_args()

    paths = a.paths or sorted(glob.glob('prompts/*.txt'))
    if not paths:
        raise SystemExit('no prompt files found -- run from the repo root')

    n_ctx = a.n_ctx or server_n_ctx(a.server) or N_CTX
    room = headroom(n_ctx, a.image_tokens, a.output_tokens, a.user_reserve)

    try:
        rows = [(count(io.open(p, encoding='utf-8').read(), a.server), p) for p in paths]
    except urllib.error.URLError as e:
        raise SystemExit('ERROR: cannot reach the tokenizer at {} ({}).\n'
                         'The llama-server must be running -- counts must come from the '
                         'real tokenizer, so there is no offline fallback.'.format(a.server, e))

    width = max(len(os.path.basename(p)) for _, p in rows)
    worst = 0
    for n, p in sorted(rows, reverse=True):
        marker, note = band(n, room)
        worst = max(worst, n)
        print('{}  {:>5}  {:>4}%  {:<{w}}  {}'.format(
            marker, n, round(100 * n / room), os.path.basename(p), note, w=width))

        if a.sections:
            for name, body in split_sections(io.open(p, encoding='utf-8').read()):
                sn = count(body, a.server)
                print('                   {:>5}  {:>3}%  {}'.format(
                    sn, round(100 * sn / n), name[:70]))
            print()

    print('\ncontext budget: {} n_ctx - {} image - {} output - {} user = {} for the system '
          'prompt'.format(n_ctx, a.image_tokens, a.output_tokens, a.user_reserve, room))
    print('the % column is the share of that headroom used. Largest prompt here: {} ({:.0%})'
          .format(worst, worst / room))
    print('NOTE: nothing degrades at ~5,000 tokens (two experiments, 1,166 calls). Between '
          '~5,000 and {} is UNTESTED,\n      not known-good. What costs a rule is another '
          "rule's semantics, not its size (L-PROMPT-TOKEN-BUDGET).".format(room))
    if a.check and worst > room:
        print('FAIL: at least one prompt cannot fit the {}-token context budget'.format(room))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
