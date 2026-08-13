#!/usr/bin/env python3
"""RULE COMPLIANCE -- does the model actually OBEY the novel rules it was given?

Side experiment: .claude/handoffs/SIDE_HANDOFF_bloat_calibration2.md

This measure was not in the plan. It became obviously necessary once the first scored round came
back: describer_setting at 3,406 live-rule tokens emitted the word "various", which the very
prompt it was running under bans by name.

WHY IT MATTERS MORE THAN THE PLANNED METRICS. L-PROMPT-TOKEN-BUDGET's actual claim is that
"adding a rule silently costs a rule" -- the model stops honouring some instruction it was
previously honouring. Format score and item count are both INDIRECT proxies for that. This is the
direct measurement: take the constraints actually present in a given cell's prompt, and count how
many of them that cell's own output breaks.

It is only defined for the N and NF arms. R restates rules the prompt already had, so an R
violation is a violation of the ORIGINAL prompt and is already what validate.py measures.

MATCHING IS DELIBERATELY CONSERVATIVE. Every check is word-boundaried, so 'etc' does not fire
inside 'stretched' and 'suit' does not fire inside 'suitable'. Only rules that can be checked
mechanically and unambiguously are included -- a rule like "write the colour before the material"
needs judgement and is left out rather than guessed at. So this UNDERCOUNTS violations, which is
the safe direction: a violation reported here is real.

  python reference/experiments/bloat2/compliance.py
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
assert ROOT.name == 'h3-prompt-rewriter' and (ROOT / '.git').is_dir(), \
    f'ROOT resolved to {ROOT} -- refusing to run outside the project'
sys.path.insert(0, str(ROOT / 'scripts'))
from validate import parse_records, head_parts          # noqa: E402

RUNS = HERE / 'runs'

# (label, regex, the rule-pool line it comes from -- matched by a distinctive substring so that
# a check only counts in a cell whose prompt ACTUALLY CONTAINS that rule).
CHECKS = [
    ('nestled',        r'(?<![\w-])nestled(?![\w-])',                       'nestled'),
    ('quaint/etc',     r'(?<![\w-])(quaint|picturesque|whimsical)(?![\w-])', 'quaint'),
    ('idyllic/etc',    r'(?<![\w-])(idyllic|serene|tranquil)(?![\w-])',      'idyllic'),
    ('breathtaking',   r'(?<![\w-])(breathtaking|majestic|iconic)(?![\w-])', 'breathtaking'),
    ('bespoke/etc',    r'(?<![\w-])(bespoke|artisanal|curated)(?![\w-])',    'bespoke'),
    ('myriad/etc',     r'(?<![\w-])(myriad|sundry|plethora)(?![\w-])',       'myriad'),
    ('various/etc',    r'(?<![\w-])(various|assorted|miscellaneous)(?![\w-])', 'various'),
    ('aforementioned', r'(?<![\w-])(aforementioned|notwithstanding|henceforth|hitherto)(?![\w-])',
                       'aforementioned'),
    ('very/quite',     r'(?<![\w-])(very|quite|rather)(?![\w-])',            'as intensifiers'),
    ('etc/e.g.',       r'(?<![\w-])(etc|e\.g\.|i\.e\.)(?![\w-])',            'Finish the list'),
    ('em dash',        r'—',                                           'em dash'),
    ('ampersand',      r'&',                                                'ampersand'),
    ('currency/%',     r'[$£€%]',                                 'currency symbol'),
    ('URL',            r'https?://|www\.',                                  'URL'),
    ('also/etc',       r'(?<![\w-])(also|additionally|furthermore|moreover)(?![\w-])',
                       '"also"'),
    ('perhaps/etc',    r'(?<![\w-])(perhaps|maybe|possibly)(?![\w-])',       '"perhaps"'),
    # The rule this checks has an explicit carve-out in its own text: a FRAMED photograph or
    # picture is a physical object on a wall or a shelf and is a legitimate [[CONTENTS]] item;
    # what is banned is naming the recording. Both hits this check produced before the carve-out
    # was implemented were "a small framed photograph", i.e. false positives against my own rule.
    ('image/photo',    r'(?<![\w-])(?<!framed )(image|images|photo|photos|photograph|photographs)'
                       r'(?![\w-])',
                       '"image"'),
    ('two spaces',     r'\S  +\S',                                          'two spaces in a row'),
    ('digit under 10', r'(?<![\w.:/-])[1-9](?![\w.:/-])',                    'below ten as words'),
    ('1st/2nd',        r'(?<![\w-])\d+(st|nd|rd|th)(?![\w-])',              'ordinal as a digit'),
    ('weight/temp',    r'(?<![\w-])(kilograms?|pounds?|degrees?|celsius|fahrenheit)(?![\w-])',
                       'weight or temperature'),
]

# Which cells to check, and where their rule text lives.
CELLS = [
    ('setting', 's_N2700', 'N2700'), ('setting', 's_N3100', 'N3100'),
    ('setting', 's_N3400', 'N3400'), ('setting', 's_N3800', 'N3800'),
    ('setting', 's_NF3400', 'NF3400'),
    ('fl2va', 'N3100', 'N3100'), ('fl2va', 'N3400', 'N3400'),
    ('fl2va', 'N3800', 'N3800'), ('fl2va', 'NF3400', 'NF3400'),
]


def outputs(path, prefix=None):
    d = {}
    for r in parse_records(pathlib.Path(path).read_text(encoding='utf-8')):
        _, cid = head_parts(r['model'])
        if cid and (prefix is None or cid.startswith(prefix)):
            d[cid] = r['output']
    return d


def main():
    man = {(m['prompt'], m['tag']): m for m in
           json.loads((HERE / 'manifest.json').read_text(encoding='utf-8'))}
    fl2va_run = RUNS / 'fl2va__f_img.txt'

    print(f'{"cell":<16}{"live":>6}{"rules":>7}{"checked":>9}{"broken":>8}   which')
    rows = []
    for probe, tag, ptag in CELLS:
        prompt = 'describer_setting' if probe == 'setting' else 'fl2va'
        m = man[(prompt, ptag)]
        rule_text = m['rule_text']

        if probe == 'setting':
            outs = outputs(RUNS / f'setting__{tag}.txt')
        else:
            if not fl2va_run.exists():
                continue
            outs = outputs(fl2va_run, prefix=f'c_{tag}_')

        active = [(lab, rx) for lab, rx, needle in CHECKS if needle in rule_text]
        broken = {}
        for cid, out in outs.items():
            for lab, rx in active:
                hits = re.findall(rx, out, re.I)
                if hits:
                    broken.setdefault(lab, []).append(cid)
        rows.append({'probe': probe, 'cell': tag, 'live': m['live_tokens'],
                     'rule_units': m['rule_units'], 'checked': len(active),
                     'broken': {k: v for k, v in broken.items()},
                     'n_broken': len(broken),
                     'n_cases': sum(len(v) for v in broken.values())})
        print(f'{probe + " " + tag:<16}{m["live_tokens"]:>6}{m["rule_units"]:>7}'
              f'{len(active):>9}{len(broken):>8}   '
              + (', '.join(f'{k} ({len(v)})' for k, v in sorted(broken.items())) or '-'))

    (HERE / 'compliance.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
    print('\nNOTE: "checked" counts only the mechanically-checkable rules PRESENT in that cell\'s')
    print('prompt, so it grows with the ladder. "broken" counts distinct rules violated at least')
    print('once. Matching is word-boundaried and conservative, so this undercounts.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
