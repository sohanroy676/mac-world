"""Shared helpers: which platform runs a job, and how heavy it is. A job is {id, cmds|args, ref?, pin?, on?, w?}.
on = "hf" | "actions" overrides the default: jobs whose trainer mode is a learner go to hf (one CPU type, so learner
results compare cleanly); beb/static/idlesense jobs are byte-identical on every CPU and go to actions. w = estimated minutes."""
NON_LEARNED = {"beb", "static", "idlesense"}


def cmd_lists(job):
    cmds = job["cmds"] if "cmds" in job else [{"name": "run", "args": job["args"]}]
    return [c["args"] if isinstance(c, dict) else c for c in cmds]


def modes(job):
    out = []
    for a in cmd_lists(job):
        out.append(a[a.index("--mode") + 1] if "--mode" in a else "independent")
    return out


def target(job):
    if job.get("on"):
        return job["on"]
    return "actions" if all(m in NON_LEARNED for m in modes(job)) else "hf"


def weight(job):
    return float(job.get("w") or len(cmd_lists(job)))
