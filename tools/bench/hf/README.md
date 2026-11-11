# Hugging Face Space: scaling and soak test (bench/hf-scale)

Answers: how many 20,40 cells per hour at 4, 8, 16 at once, are the 16 cores shared, does a 6 h run survive.
Space root needs: `app.py`, `packages.txt`, `requirements.txt` (unchanged from bench/hf) and a README whose frontmatter has
`sdk: gradio`, `app_file: app.py`, `python_version: 3.7` (same as the first Space). `hfsoak.py` is fetched by the app from this branch.
Optional secret `GH_TOKEN` (fine-grained, repo sohanroy676/mac-world only, Contents read and write, 7-day expiry) pushes events to branch `bench/hf-results`.
Optional variable `AUTOSTART=soak:6:8` re-runs setup + soak on every boot.
