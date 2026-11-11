"""Gradio front end for the HF scaling + soak benchmark (branch bench/hf-scale).
Space files at the Space root: app.py, packages.txt, requirements.txt, README.md (this folder).
Space secret (optional): GH_TOKEN = fine-grained GitHub token, repo sohanroy676/mac-world only, Contents: read and write, short expiry.
Space variable (optional): AUTOSTART = "soak:6:8" runs setup and then a 6 h soak with 8 cells on every boot (tests restart recovery)."""
import glob, os, subprocess, threading, time
import gradio as gr

try:  # ZeroGPU Spaces refuse to start without at least one @spaces.GPU function
    import spaces

    @spaces.GPU
    def _gpu_placeholder():
        return "unused"
except ImportError:
    pass

REPO = "https://github.com/sohanroy676/mac-world.git"
WORK = "/tmp/bench"
SRC = f"{WORK}/mac-world"
LOG = f"{WORK}/run.log"
state = {"running": ""}
HF_ENV = {**os.environ, "BENCH_ROOT": SRC}

def sh(cmd):
    os.makedirs(WORK, exist_ok=True)
    with open(LOG, "a") as f:
        f.write(f"\n$ {cmd}  [{time.strftime('%H:%M:%S')}]\n"); f.flush()
        subprocess.run(["bash", "-c", cmd], stdout=f, stderr=subprocess.STDOUT, env=HF_ENV)

def setup():
    sh(f"cd {WORK} && rm -rf mac-world && git clone -q -b bench/hf-scale {REPO} && cd mac-world && "
       f"bash tools/bench/run_bench.sh hf --no-apt --smoke")

def task(name):
    label = f"{name}-{time.strftime('%m%d-%H%M')}"
    pre = f"cd {SRC} && RUN_LABEL={label} python3 tools/bench/hf/hfsoak.py"
    return {"setup": None, "pushtest": f"{pre} pushtest", "scale": f"{pre} scale 4 8 16",
            "soak": f"{pre} soak 6 8"}[name]

def run(name):
    if state["running"]:
        return f"Busy: {state['running']}"
    state["running"] = name
    def go():
        try:
            if name == "setup": setup()
            else: sh(task(name))
        finally:
            state["running"] = ""
    threading.Thread(target=go, daemon=True).start()
    return f"Started {name}"

def show():
    tail = open(LOG).read()[-5000:] if os.path.exists(LOG) else "(no log yet)"
    ev = ""
    for p in sorted(glob.glob(f"{SRC}/bench-results/hfsoak/events.jsonl"))[-1:]:
        ev = "".join(open(p).readlines()[-15:])
    return f"RUNNING: {state['running'] or 'idle'}\n{tail}\n\n--- last events ---\n{ev}"

def autostart():
    a = os.environ.get("AUTOSTART", "")
    if a.startswith("soak"):
        _, hours, k = a.split(":")
        def go():
            state["running"] = "autostart"
            setup()
            sh(f"cd {SRC} && RUN_LABEL=auto-{time.strftime('%m%d-%H%M')} python3 tools/bench/hf/hfsoak.py soak {hours} {k}")
            state["running"] = ""
        threading.Thread(target=go, daemon=True).start()

autostart()
with gr.Blocks() as demo:
    gr.Markdown("1 Setup (about 10 min) then 2 Push test, 3 Scale (4, 8, 16 at once), 4 Soak (6 h).")
    msg = gr.Textbox(label="Status")
    with gr.Row():
        for n in ("setup", "pushtest", "scale", "soak"):
            gr.Button(n).click(lambda n=n: run(n), None, msg)
    out = gr.Textbox(label="Log", lines=30)
    gr.Button("Refresh").click(show, None, out)
demo.launch()
