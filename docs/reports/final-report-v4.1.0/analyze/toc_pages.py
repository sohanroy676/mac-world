#!/usr/bin/env python3
"""Page number of every table-of-contents heading, read from the rendered PDF.
usage: toc_pages.py out/toc_items.json report.pdf out/toc_pages.json"""
import json, re, subprocess, sys

items = json.load(open(sys.argv[1]))
npages = int(re.search(r"Pages:\s+(\d+)", subprocess.check_output(["pdfinfo", sys.argv[2]], text=True)).group(1))
norm = lambda s: re.sub(r"\s+", " ", s.replace(" ", " ")).strip()
pages = [norm(subprocess.check_output(["pdftotext", "-f", str(p), "-l", str(p), "-layout", sys.argv[2], "-"], text=True)) for p in range(1, npages + 1)]
# the contents occupy the first pages; start searching after the page that holds the last contents entry followed by page break
first = 0
for p, t in enumerate(pages):
    if "Scenarios to be considered:" in t and not re.search(r"Scenarios to be considered:\s*\.{3,}", t) and t.count("....") < 5:
        first = p
        break
out, pos = {}, first
for it in items:
    key = norm(it["text"])[:45]
    for p in range(pos, npages):
        if key in pages[p]:
            out[it["bm"]] = p + 1
            pos = p
            break
    else:
        print("NOT FOUND", it["text"])
json.dump(out, open(sys.argv[3], "w"))
print(len(out), "of", len(items), "headings placed")
