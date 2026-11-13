"""Gradio front end for running v4 jobs on a Hugging Face Space (branch bench/lanes). Space root files: app.py, packages.txt,
requirements.txt (this folder) and a README with sdk: gradio, app_file: app.py, python_version: 3.7.
Secret GH_TOKEN (fine-grained, repo sohanroy676/mac-world only, Contents read+write, short expiry) lets the Space push results.
Variable AUTOSTART = "batch:.github/jobs/lanes-test.json" re-runs setup and the batch on every boot (resumes after a restart).
Variable REF (default bench/lanes) = branch to clone; LANES (default 16)."""
import os, subprocess, threading, time
import gradio as gr

try:  # ZeroGPU Spaces refuse to start without at least one @spaces.GPU function
    import spaces

    @spaces.GPU
    def _gpu_placeholder():
        return "unused"
except ImportError:
    pass

REPO = "https://github.com/sohanroy676/mac-world.git"
REF = os.environ.get("REF", "bench/lanes")
WORK = "/tmp/jobs"
SRC = f"{WORK}/mac-world"
LOG = f"{WORK}/run.log"
LANES = os.environ.get("LANES", "16")
state = {"running": ""}
ENV = {**os.environ, "BENCH_ROOT": SRC}


def sh(cmd):
    os.makedirs(WORK, exist_ok=True)
    with open(LOG, "a") as f:
        f.write(f"\n$ {cmd}  [{time.strftime('%H:%M:%S')}]\n")
        f.flush()
        subprocess.run(["bash", "-c", cmd], stdout=f, stderr=subprocess.STDOUT, env=ENV)


def setup():
    sh(f"cd {WORK} && rm -rf mac-world && git clone -q -b {REF} {REPO} && cd mac-world && bash tools/bench/run_bench.sh hf --no-apt --smoke")


def run_batch(path, shard=""):
    sh(f"cd {SRC} && git pull -q origin {REF}; RUN_LABEL=hfjobs python3 tools/hf/hfjobs.py '{path}' {LANES} '{shard}'")  # pull: pick up script fixes without rebuilding ns-3


def start(what, path, shard=""):
    if state["running"]:
        return f"Busy: {state['running']}"
    state["running"] = what

    def go():
        try:
            if what == "setup":
                setup()
            else:
                run_batch(path, shard)
        finally:
            state["running"] = ""
    threading.Thread(target=go, daemon=True).start()
    return f"Started {what}"


def show():
    tail = open(LOG).read()[-6000:] if os.path.exists(LOG) else "(no log yet)"
    return f"RUNNING: {state['running'] or 'idle'}\n{tail}"


a = os.environ.get("AUTOSTART", "")
if a.startswith("batch:"):
    def auto():
        state["running"] = "autostart"
        setup()
        run_batch(a[6:])
        state["running"] = ""
    threading.Thread(target=auto, daemon=True).start()

with gr.Blocks() as demo:
    gr.Markdown("1 setup (about 10 min), then 2 run batch. Results go to GitHub branch bench/hf-results (needs GH_TOKEN).")
    path = gr.Textbox(value=".github/jobs/lanes-test.json", label="Batch file in the repo")
    shard = gr.Textbox(value="", label="Shard k/n (empty = whole batch; two Spaces: 0/2 and 1/2)")
    msg = gr.Textbox(label="Status")
    gr.Button("setup").click(lambda p, k: start("setup", p, k), [path, shard], msg)
    gr.Button("run batch").click(lambda p, k: start("batch", p, k), [path, shard], msg)
    out = gr.Textbox(label="Log", lines=30)
    gr.Button("Refresh").click(show, None, out)
demo.launch()
