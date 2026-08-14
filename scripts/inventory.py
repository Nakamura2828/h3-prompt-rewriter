#!/usr/bin/env python
"""Cross-check docs/image_inventory.md against images/, and regenerate the medium tally.

The inventory is hand-written ground truth — validate.py cannot see image content, so this
document is what lets us judge whether a describer said something *true*. That makes it worth
guarding: a row that drifts from the folder is a silently wrong answer key.

    python scripts/inventory.py            # check, and rewrite the tally if it is stale
    python scripts/inventory.py --check    # check only, never write (exit 1 on any problem)

Checks:
  - every file in images/ has a master row, and every master row has a file
  - every master row is covered by the contents table (rows may key several files with `/`)
  - medium/sub come from the closed vocabulary, and each sub belongs to its own coarse term
  - flags come from the known set
  - no duplicate rows in either table
  - every `image` and `system_file` path in tests/*.json actually exists (added session 21 —
    run_tests.py exits hard on these, so a stale path fails months later, not now)

Then regenerates the medium tally in place, so it cannot desync the way the hand-maintained
tallies did (they disagreed with each other about whether crops counted).
"""
import argparse
import io
import json
import pathlib
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from validate import AGE_PERSON                        # noqa: E402

DOC = "docs/image_inventory.md"
IMG_DIR = "images"
TESTS_DIR = "tests"
EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}

# The closed three-axis vocabulary. Mirrors "Style vocabulary" in the document.
#
# VOCAB is the medium axis at two levels: coarse -> its permitted sub-terms, where a coarse
# term mapping to an empty set takes no sub-term and must be written as `none`. IDIOM and
# TREATMENT are the other two axes and are flat -- every image takes exactly one value of
# each, with no dependence on the medium. That independence is the whole point of the
# session-10 rebuild: the old sub-lists mixed all three axes, and the coupling was dragging
# the coarse term to the wrong value (see "Why the rebuild happened" in the document).
VOCAB = {
    "photograph":       set(),
    "live-action film": set(),
    "3D CG":            set(),
    # Session 17: `puppet` merged into `figure`, and `2D cel` lost its sub-list entirely.
    # Kept in sync with scripts/validate.py's MEDIUM_VOCAB by hand -- see the note there.
    "stop-motion":      {"clay", "figure", "model"},
    "2D cel":           set(),
    "comic":            {"ink", "screentone", "digital"},
    "painting":         {"oil", "watercolour", "digital"},
    "drawing":          {"marker", "pencil", "ink", "digital"},
    "vector":           set(),
    "pixel art":        set(),
    "print":            {"engraving", "halftone"},
}
IDIOM = {"anime", "western toon", "flat graphic", "dimensional toon", "realist"}
TREATMENT = {"colour", "monochrome"}

# The age axis (session 19). Unlike the three above it is a MULTISET -- one image can hold a
# toddler and an older adult -- so it tallies by "images in which this bracket appears" rather
# than one row per value.
#
# AGE_PERSON is IMPORTED from validate.py rather than restated here, and deliberately: it is the
# same closed list prompts/describer_character.txt enforces, and a second copy is exactly the
# hand-sync the VOCAB <-> MEDIUM_VOCAB note above still warns about. If the prompt's brackets
# change, this file follows automatically.
AGE_EXTRA = {
    "n/d":   "a human figure is present but the depiction does not determine an age",
    "n/a":   "figures are present but none is human -- animals, and humanoids that carry no "
             "human age at all (a LEGO minifigure, Gumby's clay slab, a skeleton)",
    "crowd": "an un-individuated mass, no bracket claimed for its members",
}
AGE_NONE = "—"                                         # no figure of any kind
# `—` and `n/a` are NOT interchangeable, and the distinction is the whole reason `n/a` exists:
# `—` says the frame is empty of figures, `n/a` says it holds figures the age axis does not
# reach. Collapsing them would make "no sample" and "not applicable" the same reading in the
# tally, and `pooh` (one anthropomorphic bear) would then be indistinguishable from `cannon`.
# Youngest-first, which is the only order a reader expects of age brackets.
AGE_ORDER = ["infant", "toddler", "child", "pre-teen", "teenager",
             "young adult", "adult", "middle-aged", "older adult"]
assert set(AGE_ORDER) == set(AGE_PERSON), set(AGE_ORDER) ^ set(AGE_PERSON)

# `people` cells that assert no human. Anything else must carry a non-`—` age, and vice versa:
# that pairing is the check that would have caught the mathilda set, where ten files recorded no
# bracket at all and the eleventh (`window`) recorded one that disagreed with them.
NO_PEOPLE = re.compile(r"^(none|—|-|\*\*none\*\*|none \(1 bird\))$", re.I)

# Tally order: coarse terms largest-first is unstable as the corpus grows, so fix it explicitly.
ORDER = list(VOCAB)
IDIOM_ORDER = ["realist", "anime", "flat graphic", "western toon", "dimensional toon"]
TREATMENT_ORDER = ["colour", "monochrome"]

# `amb` was RETIRED in session 19. It marked three studio product shots (chair, car_1, car_2)
# whose photograph-vs-render reading is not visually determinable; that ruling now lives where
# every other ambiguity ruling lives -- as an accept-set in `_expected`, written by
# gen_style_sweep.py. The flag is gone rather than merely unused, so a row cannot quietly
# reacquire it and mean something the scoring no longer reads.
FLAGS = {"text", "real", "franchise", "derived", "corr", "nested"}
LIVE_ACTION = {"photograph", "live-action film"}
NONE = {"none", "—", "-", ""}
# Named here only so the tally caption can keep reporting the honest live-action range now that
# the flag that used to identify them is gone. Not a flag, not a vocabulary -- just three names.
AMB_LEGACY = ["chair", "car_1", "car_2"]

# Footnote markers in the generated tally, driven by flags rather than hand-annotation.
MARKERS = [("nested", r"\*\*")]


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse_table(lines, start_heading, stop_prefix="## "):
    """Return (header, rows) for the first markdown table after `start_heading`."""
    i = next(i for i, l in enumerate(lines) if l.startswith(start_heading))
    header, rows = None, []
    for line in lines[i + 1:]:
        if line.startswith(stop_prefix):
            break
        if not line.startswith("|"):
            continue
        c = cells(line)
        if header is None:
            header = c
        elif not re.match(r"^-+$", c[0]):
            rows.append(dict(zip(header, c)))
    return header, rows


def names_in(cell):
    """`a` / `b` -> ['a', 'b']. Contents rows may legitimately key several near-identical files."""
    return [n.strip().strip("`") for n in cell.split("/") if n.strip()]


def age_tokens(cell):
    """An `age` cell -> its tokens. `—` yields nothing, which is what "no human" means."""
    cell = cell.strip()
    if cell in NONE:
        return []
    return [t.strip() for t in cell.split(",") if t.strip()]


def check_age(name, row, problems):
    """Validate one row's `age` cell, and its agreement with `people`."""
    cell = row["age"].strip()
    tokens = age_tokens(cell)
    for t in tokens:
        if t not in AGE_PERSON and t not in AGE_EXTRA:
            problems.append(
                f"`{name}`: age {t!r} is not a bracket or one of {sorted(AGE_EXTRA)}")
    if len(tokens) != len(set(tokens)):
        problems.append(f"`{name}`: age {cell!r} repeats a token — the cell is a set, not a count")
    if "n/a" in tokens and len(tokens) > 1:
        problems.append(f"`{name}`: age {cell!r} — 'n/a' means NO figure is human, so it cannot "
                        f"sit beside a bracket")
    # The two columns must agree about whether the frame holds a figure. Either alone can rot
    # silently; together they cannot -- this is the check that would have caught the mathilda
    # set, where ten files carried no bracket and the eleventh carried one that disagreed.
    empty_people = bool(NO_PEOPLE.match(row["people"].strip()))
    if empty_people and tokens:
        problems.append(f"`{name}`: age {cell!r} but people says no figure")
    if not empty_people and not tokens:
        problems.append(f"`{name}`: people names a figure ({row['people'][:40]!r}) but age is "
                        f"`—`. Use 'n/a' if the figures are not human, 'n/d' if the age is "
                        f"unreadable")


def check_test_files(problems):
    """Every `image` and `system_file` path in tests/*.json must resolve.

    Nothing checked this before session 21. run_tests.py exits hard on a missing image and on
    an unreadable system_file, so a test can sit broken indefinitely and only fail when
    someone finally runs it. Three instances were found by accident in one session — a
    deleted captain.jpg, a renamed p1_light-zoom-gun_*.png, and a retired prompt — which is
    why this is a mechanism rather than a note. It lives here because inventory.py is already
    the script that cross-checks recorded paths against what is actually on disk.
    """
    for path in sorted(pathlib.Path(TESTS_DIR).glob("*.json")):
        try:
            spec = json.loads(path.read_text(encoding="utf-8"))
        except ValueError as e:
            problems.append(f"{path.as_posix()}: not valid JSON — {e}")
            continue
        cases = [c for c in spec.get("cases", []) if isinstance(c, dict)]
        default_sys = spec.get("defaults", {}).get("system_file")
        wanted = {c["image"] for c in cases if c.get("image")}
        wanted |= {c.get("system_file", default_sys) for c in cases} - {None}
        for p in sorted(wanted):
            if not pathlib.Path(p).exists():
                problems.append(f"{path.as_posix()}: path does not exist: {p}")


def build_tally(master):
    by_coarse = defaultdict(lambda: defaultdict(list))
    for r in master:
        by_coarse[r["medium"]][r["sub"]].append(r)

    def label(r):
        name = r["image"].strip("`")
        for flag, mark in MARKERS:
            if flag in r["flags"]:
                name += mark
        return name

    out = ["| medium | sub | count | images |", "|---|---|---|---|"]
    for coarse in ORDER:
        subs = by_coarse.get(coarse)
        if not subs:
            continue
        total = sum(len(v) for v in subs.values())
        if not VOCAB[coarse]:                       # no sub-term: one flat row
            names = sorted(label(r) for r in next(iter(subs.values())))
            out.append(f"| `{coarse}` | — | **{total}** | {', '.join(names)} |")
            continue
        out.append(f"| `{coarse}` | | **{total}** | |")
        used = sorted(subs, key=lambda s: (-len(subs[s]), s))
        for sub in used:
            names = sorted(label(r) for r in subs[sub])
            out.append(f"| | {sub} | {len(names)} | {', '.join(names)} |")
        for sub in sorted(VOCAB[coarse] - set(used)):
            out.append(f"| | *{sub}* | *0* | *no sample* |")

    # The other two axes are flat, so they tally as plain one-per-value tables rather than
    # nested under the medium. Keeping them separate is the visible form of the claim that
    # they are independent axes.
    for title, vocab, order, col in (
        ("idiom", IDIOM, IDIOM_ORDER, "idiom"),
        ("treatment", TREATMENT, TREATMENT_ORDER, "treatment"),
    ):
        by_val = defaultdict(list)
        for r in master:
            by_val[r[col]].append(r)
        out += ["", f"### `[[{col.upper()}]]` tally", "",
                f"| {title} | count | images |", "|---|---|---|"]
        for val in order:
            rows = by_val.get(val)
            if not rows:
                out.append(f"| *{val}* | *0* | *no sample* |")
                continue
            names = sorted(label(r) for r in rows)
            out.append(f"| `{val}` | **{len(names)}** | {', '.join(names)} |")

    # The age axis is a multiset, so it cannot join the flat loop above: an image contributes to
    # every bracket it contains. The count is therefore "images holding this bracket" and the
    # column does NOT sum to the corpus size -- said in the caption so nobody reads it as a
    # partition the way the medium tally is one.
    by_age = defaultdict(list)
    for r in master:
        for t in age_tokens(r["age"]):
            by_age[t].append(r)
    out += ["", "### `[[AGE]]` tally", "",
            "| bracket | images | which |", "|---|---|---|"]
    for val in AGE_ORDER + list(AGE_EXTRA):
        rows = by_age.get(val)
        if not rows:
            out.append(f"| *{val}* | *0* | *no sample* |")
            continue
        names = sorted(label(r) for r in rows)
        out.append(f"| `{val}` | **{len(names)}** | {', '.join(names)} |")
    peopled = [r for r in master if age_tokens(r["age"])]
    out += ["", (
        f"**{len(peopled)} of {len(master)} images hold a human figure.** An image contributes to "
        f"every bracket it contains, so this column counts IMAGES PER BRACKET and does not sum to "
        f"the corpus — unlike the medium tally, which partitions it. `n/d` is a figure whose "
        f"depiction does not determine an age; `crowd` is an un-individuated mass. Animals are "
        f"deliberately absent: their vocabulary is a different four-term list whose `adult` would "
        f"collide with the human bracket in the same cell."
    )]

    n = len(master)
    la = [r for r in master if r["medium"] in LIVE_ACTION]
    out += ["", (
        f"**Total {n}.** Live-action (`photograph` + `live-action film`) is "
        f"**{len(la)} of {n}, {round(100 * len(la) / n)}%** — down from 29/37, 78% at the start "
        f"of session 7. Three of those ({', '.join('`%s`' % x for x in AMB_LEGACY)}) are clean "
        f"studio product shots filed as `photograph` on provenance the pixels do not show, so "
        f"the honest range is {len(la) - len(AMB_LEGACY)}–{len(la)}. They carried an `amb` flag "
        f"until session 19; the ruling is now an accept-set in `_expected` instead."
    )]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="never write; exit 1 on any problem")
    args = ap.parse_args()

    text = io.open(DOC, encoding="utf-8").read()
    lines = text.split("\n")
    problems = []

    _, master = parse_table(lines, "## Master table")
    _, contents = parse_table(lines, "## Contents table")

    import os
    on_disk = {
        os.path.splitext(f)[0]
        for f in os.listdir(IMG_DIR)
        if os.path.splitext(f)[1].lower() in EXTS and os.path.isfile(os.path.join(IMG_DIR, f))
    }
    in_master = [r["image"].strip("`") for r in master]

    for dup, k in Counter(in_master).most_common():
        if k > 1:
            problems.append(f"master table: `{dup}` appears {k} times")
    for name in sorted(on_disk - set(in_master)):
        problems.append(f"file with no master row: {name}")
    for name in sorted(set(in_master) - on_disk):
        problems.append(f"master row with no file: `{name}`")

    covered = {n for r in contents for n in names_in(r["image"])}
    for name in sorted(set(in_master) - covered):
        problems.append(f"no contents row: `{name}`")
    for name in sorted(covered - set(in_master)):
        problems.append(f"contents row for unknown image: `{name}`")

    check_test_files(problems)

    for r in master:
        name, coarse, sub = r["image"].strip("`"), r["medium"], r["sub"]
        if coarse not in VOCAB:
            problems.append(f"`{name}`: medium {coarse!r} not in the vocabulary")
        elif VOCAB[coarse] and sub not in VOCAB[coarse]:
            problems.append(f"`{name}`: sub {sub!r} is not a sub-term of {coarse!r}")
        elif not VOCAB[coarse] and sub not in NONE:
            problems.append(f"`{name}`: {coarse!r} takes no sub-term, found {sub!r}")
        # idiom and treatment are flat and medium-independent -- checked against the whole
        # list, never against the coarse term, or we would re-create the coupling the
        # session-10 rebuild removed.
        if r["idiom"] not in IDIOM:
            problems.append(f"`{name}`: idiom {r['idiom']!r} not in the vocabulary")
        if r["treatment"] not in TREATMENT:
            problems.append(f"`{name}`: treatment {r['treatment']!r} not in the vocabulary")
        check_age(name, r, problems)
        for f in (x.strip() for x in r["flags"].split(",")):
            if f and f not in NONE and f not in FLAGS:
                problems.append(f"`{name}`: unknown flag {f!r}")

    for p in problems:
        print(f"  FAIL  {p}")

    # Regenerate the tally: from its table header down to the first footnote line.
    try:
        s = next(i for i, l in enumerate(lines) if l.startswith("| medium | sub | count |"))
        e = next(i for i, l in enumerate(lines[s:], s) if l.startswith("\\*"))
    except StopIteration:
        print("  FAIL  could not locate the tally block")
        return 1

    new = build_tally(master)
    stale = lines[s:e] != new + [""]
    if stale and not args.check:
        io.open(DOC, "w", encoding="utf-8", newline="\n").write(
            "\n".join(lines[:s] + new + [""] + lines[e:])
        )

    print(f"  {len(master)} images · {len(contents)} contents rows · "
          f"{len(set(r['medium'] for r in master))} media")
    if stale:
        print("  tally was stale — " + ("NOT rewritten (--check)" if args.check else "rewritten"))
    else:
        print("  tally up to date")
    print(f"  {len(problems)} problem(s)")
    return 1 if problems or (stale and args.check) else 0


if __name__ == "__main__":
    sys.exit(main())
