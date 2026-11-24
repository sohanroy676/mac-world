#!/usr/bin/env python3
"""Turns the pandoc text of the mentor's scenario list (analyze/mentor_source.md, produced with `pandoc -t gfm --wrap=none`)
into sections/10_mentor.md: same words, same order, same tables; only the heading levels are ours, and a result block
directive ({{results:N}}) follows each scenario.   Usage: python3 make_mentor_md.py > ../sections/10_mentor.md"""
import re
import sys

src = [l.rstrip("\n") for l in open(sys.argv[1] if len(sys.argv) > 1 else "analyze/mentor_source.md", encoding="utf8")]
out = []
SUB = {"Topology", "Experimental variations", "Objective", "Research questions"}
scen = None


def close():
    global scen
    if scen:
        out.extend(["", "{{results:%s}}" % scen, ""])
        scen = None


for l in src:
    t = l.strip()
    plain = re.sub(r"^\*\*(.*)\*\*$", r"\1", re.sub(r"^#+\s*", "", t))
    m = re.match(r"^Scenario (\d+):", plain)
    if plain == "Scenarios to be considered:":
        out.append("# " + plain)
    elif m:
        close()
        scen = m.group(1)
        out.append("## " + plain)
    elif plain == "Extension:":
        close()
        scen = "ext"
        out.extend(["## " + plain])
    elif plain in SUB:
        out.append("### " + plain)
    else:
        out.append(l)
close()
text = re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n"
sys.stdout.write(text)
