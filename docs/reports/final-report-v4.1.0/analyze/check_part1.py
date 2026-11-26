#!/usr/bin/env python3
"""Part I must be the mentor's text: compare the words of sections/10_mentor.md (result directives removed) with analyze/mentor_source.md."""
import re, sys

def words(t):
    t = re.sub(r"\{\{results:\w+\}\}", "", t)
    return re.sub(r"[#|*\-:]", " ", t).split()

a = words(open("analyze/mentor_source.md", encoding="utf8").read())
b = words(open("sections/10_mentor.md", encoding="utf8").read())
if a != b:
    sys.exit("Part I differs from the mentor source")
print("Part I matches the mentor source (%d words)" % len(a))
