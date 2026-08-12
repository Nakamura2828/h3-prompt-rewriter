#!/usr/bin/env python3
"""Locate the repo root by walking up, not by counting directory levels.

These scripts were written in `.claude/experiments/prompt_archive/` and now live in
`reference/prompt_archive/`, which is one level shallower. A hardcoded `parents[2]` was correct
in the first location and silently resolved to a directory ABOVE the repo in the second --
`git ls-tree` then ran outside the repo and the token counts came from nowhere at all.

So the root is found by looking for it. Anything importing this can be moved again without
breaking. `verify.py` deliberately keeps its own copy of this logic: it ships with the archive
as the user-facing check and must not depend on the generator scripts being present.
"""
import pathlib


def find_root(start):
    """Nearest ancestor of `start` that looks like this repo's root."""
    start = pathlib.Path(start).resolve()
    base = start if start.is_dir() else start.parent
    for d in [base, *base.parents]:
        if (d / 'prompts').is_dir() and (d / 'scripts').is_dir():
            return d
    raise SystemExit(f'cannot locate the repo root above {base} -- expected a parent directory '
                     f'containing both prompts/ and scripts/')
