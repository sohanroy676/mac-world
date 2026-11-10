"""Gradio front end that runs the no-root benchmark in the background and shows the report.
Space files needed at the Space root: app.py, packages.txt, requirements.txt (this folder)."""
import glob, os, subprocess, threading
import gradio as gr

REPO = "https://github.com/sohanroy676/mac-world.git"
WORK = "/tmp/bench"
LOG = os.path.join(WORK, "run.log")
state = {"running": False}

def job(args):
    os.makedirs(WORK, exist_ok=True)
    with open(LOG, "w") as f:
        cmd = (f"cd {WORK} && rm -rf mac-world && git clone -q -b bench/hf {REPO} && cd mac-world && "
               f"bash tools/bench/run_bench.sh hf --no-apt {args}")
        subprocess.run(["bash", "-c", cmd], stdout=f, stderr=subprocess.STDOUT)
    state["running"] = False

def start(mode):
    if state["running"]:
        return "Already running."
    state["running"] = True
    threading.Thread(target=job, args=("--smoke" if mode == "smoke" else "--parallel 2",), daemon=True).start()
    return "Started."

def show():
    tail = open(LOG).read()[-6000:] if os.path.exists(LOG) else "(no log yet)"
    rep = "".join(open(p).read() for p in sorted(glob.glob(f"{WORK}/mac-world/bench-results/hf-*.md")))
    return ("RUNNING\n" if state["running"] else "IDLE\n") + tail + "\n\n" + rep

with gr.Blocks() as demo:
    mode = gr.Radio(["smoke", "full"], value="smoke", label="Run")
    msg = gr.Textbox(label="Status")
    gr.Button("Start").click(start, mode, msg)
    out = gr.Textbox(label="Log and report", lines=30)
    gr.Button("Refresh").click(show, None, out)
demo.launch()
