"""v4.1.0 Wave 2l: class B stage 2. Top-3 training seeds (by Wave 2k ranking) per learner and cell, frozen, evaluated on tournament seeds
300-309 (60 s). RAFA best seed also at alphas 0 and 4 (the alpha is an actor input); RAFA ranks 2-3, Global and PF at alpha 1 only
(their actors do not take alpha; the alpha-fair score is computed afterwards). Each model/alpha is 2 jobs of 5 seeds. Actors are fetched
from branch wave-actors (needs `git fetch origin wave-actors`)."""
import json
import os
import subprocess
import sys

cells = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "waves", "cells.json")))
MARGS = {"rafa": ["--mode", "shared", "--obs", "rafa", "--reward", "fair", "--alphaInput"], "global": ["--mode", "global"],
         "pf": ["--mode", "independent", "--reward", "pf"]}
TOP = {("s2", "global"): [2003, 2005, 2004], ("s2", "pf"): [2006, 2007, 2011], ("s2", "rafa"): [2011, 2000, 2002],
       ("s4", "global"): [2008, 2007, 2002], ("s4", "pf"): [2003, 2004, 2001], ("s4", "rafa"): [2001, 2005, 2011],
       ("s5a", "global"): [2001, 2003, 2009], ("s5a", "pf"): [2007, 2003, 2002], ("s5a", "rafa"): [2007, 2010, 2008]}
tree = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", "origin/wave-actors"], text=True).split()
jobs = []
for (cell, lr), seeds in TOP.items():
    for rank, ts in enumerate(seeds):
        job = "w2k-%s-%s-t%d" % (cell, lr, ts)
        src = [f.rsplit("/actors/", 1)[0] for f in tree if f.endswith("/" + job + "/actors/agent0_actor")]
        assert len(src) == 1, (job, src)
        files = sorted(f.split("/actors/", 1)[1] for f in tree if f.startswith(src[0] + "/actors/"))
        alphas = [1, 0, 4] if (lr == "rafa" and rank == 0) else [1]
        for al in alphas:
            for half, ss in (("h0", range(300, 305)), ("h1", range(305, 310))):
                tag = "w2l-%s-%s-t%d-a%g-%s" % (cell, lr, ts, al, half)
                cmds = [{"name": "fetch", "fetch": {"src": src[0] + "/actors", "files": files}}]
                for s in ss:
                    cmds.append({"name": "eval%d" % s, "args": cells[cell]["args"] + ["--stepTime", "0.01", "--check"] + MARGS[lr] + [
                        "--simTime", "60", "--eval", "--loadActor", "{ACT}", "--fairAlpha", str(al), "--seed", str(s), "--tag", tag]})
                w = 1.1 * 60 * 5
                jobs.append({"id": tag, "w": w, "timeout": int(70 * 1.1 * 60 * 2 + 600), "cmds": cmds})
json.dump({"jobs": jobs}, open(sys.argv[1], "w"))
print(len(jobs), "jobs,", "%.1f lab-h" % (sum(j["w"] for j in jobs) / 33.0 * 0.2))
