# Hugging Face Space test

1. Create a Gradio Space with **CPU basic** hardware.
2. Copy `app.py`, `packages.txt`, `requirements.txt` from this folder to the Space root and add this README's frontmatter in the Space's own README:
   `sdk: gradio`, `app_file: app.py`.
3. Open the Space, press Start (smoke first), then Refresh to see the log and report.
The benchmark runs without root (`--no-apt`) and uses micromamba for Python 3.7.
