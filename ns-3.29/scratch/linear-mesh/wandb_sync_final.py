"""Upload the 81 final offline W&B runs (v2.0.0 *-cwfix benchmarks) and name/tag them.

    python wandb_sync_final.py sync [--pilot]   upload runs that are not on the server yet
    python wandb_sync_final.py tag              rename `<topo> <mode> s<seed>`, add tags
    python wandb_sync_final.py check            count how many of the 81 run ids are on the server

Needs a W&B login (`wandb login` or WANDB_API_KEY in the environment; never commit a key).
Run from the project venv: ../../venv/bin/python wandb_sync_final.py ...

Why a patch: wandb 0.18.7 `wandb sync` printed "done" and wrote `.synced`, but created no run, because
the server answers the GraphQL introspection probes with null and the client crashed in `upsert_run`
('NoneType' object has no attribute 'get'). The patch below only acts when a probe fails and sets the
client's own no-introspection fallback; no package file or pin is changed. A run only counts as synced
when the API finds it afterwards. See docs/final-results-v2.2.0.md section 5.
"""
import argparse
import csv
import glob
import os
import subprocess
import sys

from config import wandb_entity as ENTITY

PROJECT = "contention_window"
HERE = os.path.dirname(os.path.abspath(__file__))
SETS = ["fixed60", "imbalance", "load0.5", "load1", "load150"]


def load_runs():
    runs = []
    for s in SETS:
        with open(os.path.join(HERE, "results/bench-v2.0.0-%s-cwfix/manifest.csv" % s)) as f:
            for r in csv.DictReader(f):
                assert r["result"] == "PASS", r
                files = glob.glob(os.path.join(HERE, r["run_dir"], "run-*.wandb"))
                assert len(files) == 1, (r["run_dir"], files)
                runs.append(dict(set=s, topo=r["topo"], mode=r["mode"], seed=int(r["seed"]),
                                 file=files[0], id=os.path.basename(files[0])[4:-len(".wandb")]))
    assert len(runs) == 81 and len({r["id"] for r in runs}) == 81, len(runs)
    return runs


def patch_introspection():
    from wandb.sdk.internal import internal_api as ia
    orig_settings, orig_info = ia.Api.server_settings_introspection, ia.Api.server_info_introspection

    def settings(self):
        try:
            orig_settings(self)
        except Exception:
            self._server_settings_type = []

    def info(self):
        try:
            return orig_info(self)
        except Exception:
            self.query_types, self.mutation_types, self.server_info_types = [], [], []
            return [], [], []

    ia.Api.server_settings_introspection = settings
    ia.Api.server_info_introspection = info


def on_server(api, r):
    try:
        api.run("%s/%s/%s" % (ENTITY, PROJECT, r["id"]))
        return True
    except Exception:
        return False


def cmd_sync(runs, pilot):
    import wandb
    api = wandb.Api()
    todo = [r for r in runs if r["set"] == "load0.5"][:1] if pilot else runs
    ok = 0
    for r in todo:
        if on_server(api, r):
            print("skip (already on server)", r["id"])
            ok += 1
            continue
        if os.path.exists(r["file"] + ".synced"):
            os.remove(r["file"] + ".synced")  # stale marker from a sync that never created the run
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "_sync", "-e", ENTITY, "-p", PROJECT, r["file"]],
                           capture_output=True, text=True)
        good = on_server(api, r)
        print("OK  " if good else "FAIL", r["set"], r["topo"], r["mode"], r["seed"], r["id"], flush=True)
        if not good:
            print((p.stdout + p.stderr)[-800:])
            if pilot:
                break
        ok += good
    print("on server %d/%d" % (ok, len(todo)))
    return ok == len(todo)


def cmd_tag(runs):
    import wandb
    api = wandb.Api()
    n = 0
    for r in runs:
        try:
            run = api.run("%s/%s/%s" % (ENTITY, PROJECT, r["id"]))
        except Exception:
            continue
        run.display_name = "%s %s s%d" % (r["topo"], r["mode"], r["seed"])
        run.tags = ["multi-ap", "final-v2.2.0", "bench-" + r["set"], "mode-" + r["mode"]]
        run.update()
        n += 1
    print("renamed+tagged %d/%d runs" % (n, len(runs)))
    return n == len(runs)


def cmd_check(runs):
    import wandb
    api = wandb.Api()
    n = sum(on_server(api, r) for r in runs)
    print("%s/%s: %d/%d of the final run ids found" % (ENTITY, PROJECT, n, len(runs)))
    return n == len(runs)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "_sync":  # internal: patched `wandb sync` in a child process
        patch_introspection()
        from wandb.cli.cli import cli
        cli(["sync"] + sys.argv[2:])
        sys.exit(0)
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("command", choices=["sync", "tag", "check"])
    ap.add_argument("--pilot", action="store_true", help="sync only the first load0.5 run")
    a = ap.parse_args()
    runs = load_runs()
    if a.command == "sync":
        success = cmd_sync(runs, a.pilot)
    else:
        success = cmd_tag(runs) if a.command == "tag" else cmd_check(runs)
    sys.exit(0 if success else 1)
