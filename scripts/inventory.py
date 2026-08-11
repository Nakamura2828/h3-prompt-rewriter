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

Then regenerates the medium tally in place, so it cannot desync the way the hand-maintained
tallies did (they disagreed with each other about whether crops counted).
"""
import argparse
import io
import re
import sys
from collections import Counter, defaultdict

DOC = "docs/image_inventory.md"
IMG_DIR = "images"
EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}

# The closed two-level vocabulary. Mirrors "Medium vocabulary" in the document; a coarse term
# mapping to an empty set takes no sub-term and must be written as an em dash.
VOCAB = {
    "photograph":       {"colour", "archival"},
    "live-action film": {"modern", "vintage Technicolor"},
    "3D CG":            {"product render", "character render", "feature animation"},
    "stop-motion":      set(),
    "2D cel":           {"anime", "western toon", "flat illustration"},
    "comic":            set(),
    "painting":         {"oil", "watercolour", "gouache", "digital"},
    "drawing":          {"marker", "sketch", "ink"},
    "vector":           set(),
    "pixel art":        set(),
    "print":            {"engraving", "technical plate"},
}
# Tally order: coarse terms largest-first is unstable as the corpus grows, so fix it explicitly.
ORDER = list(VOCAB)

FLAGS = {"text", "real", "franchise", "derived", "corr", "amb", "nested"}
LIVE_ACTION = {"photograph", "live-action film"}
NONE = {"—", "-", ""}

# Footnote markers in the generated tally, driven by flags rather than hand-annotation.
MARKERS = [("amb", r"\*"), ("nested", r"\*\*")]


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

    n = len(master)
    la = [r for r in master if r["medium"] in LIVE_ACTION]
    amb = [r for r in la if "amb" in r["flags"]]
    out += ["", (
        f"**Total {n}.** Live-action (`photograph` + `live-action film`) is "
        f"**{len(la)} of {n}, {round(100 * len(la) / n)}%** — down from 29/37, 78% at the start "
        f"of session 7. {len(amb)} of those {len(la)} are `amb`, so the honest range is "
        f"{len(la) - len(amb)}–{len(la)}."
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

    for r in master:
        name, coarse, sub = r["image"].strip("`"), r["medium"], r["sub"]
        if coarse not in VOCAB:
            problems.append(f"`{name}`: medium {coarse!r} not in the vocabulary")
        elif VOCAB[coarse] and sub not in VOCAB[coarse]:
            problems.append(f"`{name}`: sub {sub!r} is not a sub-term of {coarse!r}")
        elif not VOCAB[coarse] and sub not in NONE:
            problems.append(f"`{name}`: {coarse!r} takes no sub-term, found {sub!r}")
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
